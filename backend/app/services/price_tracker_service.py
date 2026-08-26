from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.price_history import PriceHistory
from app.models.user import User

from app.schemas.product import ProductData

from app.services.firecrawl_service import FirecrawlService
from app.services.email_service import EmailService


class PriceTrackerService:

    def __init__(self):

        self.firecrawl_service = FirecrawlService()

        self.email_service = EmailService()


    async def check_product_price(
        self,
        product: Product,
        db: AsyncSession
    ):

        # Step 1: Scrape the latest product data
        scraped_data = self.firecrawl_service.scrape_product(
            product.product_url
        )

        # Step 2: Validate scraped data
        product_data = ProductData(
            **scraped_data
        )

        # Step 3: Get latest price
        latest_price = product_data.currentPrice

        old_price = float(product.current_price)
        new_price = float(latest_price)

        # Step 4: Check if the price changed
        if old_price == new_price:

            return {
                "product_id": product.id,
                "old_price": old_price,
                "new_price": new_price,
                "price_changed": False,
                "new_lowest_price": False
            }

        # Step 5: Find the lowest historical price
        result = await db.execute(
            select(
                func.min(PriceHistory.price)
            ).where(
                PriceHistory.product_id == product.id
            )
        )

        lowest_historical_price = result.scalar_one_or_none()

        # If there is no history for some reason,
        # use the current product price as the comparison
        if lowest_historical_price is None:
            lowest_historical_price = old_price

        lowest_historical_price = float(
            lowest_historical_price
        )

        # Step 6: Check whether this is a new lowest price
        is_new_lowest_price = (
            new_price < lowest_historical_price
        )

        # Step 7: Update the current product price
        product.current_price = latest_price

        # Step 8: Add the new price to price history
        price_history = PriceHistory(
            product_id=product.id,
            price=latest_price
        )

        db.add(price_history)

        # Step 9: Send email if this is a new lowest price
        email_sent = False

        if is_new_lowest_price:

            try:

                # Get the product owner
                result = await db.execute(
                    select(User).where(
                        User.id == product.user_id
                    )
                )

                user = result.scalar_one_or_none()

                if user:

                    self.email_service.send_lowest_price_alert(
                        recipient_email=user.email,
                        product_name=product.product_name,
                        old_price=old_price,
                        new_price=new_price,
                        currency_code=product.currency_code,
                        product_url=product.product_url
                    )

                    email_sent = True

            except Exception as e:

                # Email failure should not stop price tracking
                print(
                    f"Failed to send lowest price email "
                    f"for product {product.id}: {str(e)}"
                )

        return {
            "product_id": product.id,
            "old_price": old_price,
            "new_price": new_price,
            "price_changed": True,
            "new_lowest_price": is_new_lowest_price,
            "email_sent": email_sent
        }


    async def check_all_products(
        self,
        db: AsyncSession
    ):

        """
        Check the latest price for all tracked products.
        """

        # Step 1: Get all tracked products
        result = await db.execute(
            select(Product)
        )

        products = result.scalars().all()

        results = []

        # Step 2: Check every product
        for product in products:

            try:

                check_result = await self.check_product_price(
                    product=product,
                    db=db
                )

                results.append(check_result)

            except Exception as e:

                # Continue checking remaining products
                results.append({
                    "product_id": product.id,
                    "price_changed": False,
                    "error": str(e)
                })

        # Step 3: Save all successful price changes
        await db.commit()

        return results