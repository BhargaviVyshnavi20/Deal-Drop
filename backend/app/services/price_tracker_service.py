from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.product import Product
from app.models.price_history import PriceHistory
from app.schemas.product import ProductData
from app.services.firecrawl_service import FirecrawlService


class PriceTrackerService:

    def __init__(self):
        self.firecrawl_service = FirecrawlService()

    async def check_product_price(
        self,
        product: Product,
        db: AsyncSession
    ):

        # Step 1: Scrape the same product URL again
        scraped_data = self.firecrawl_service.scrape_product(
            product.product_url
        )

        # Step 2: Validate the scraped data
        product_data = ProductData(
            **scraped_data
        )

        # Step 3: Get the latest price
        latest_price = product_data.currentPrice

        # Step 4: Compare prices
        if float(product.current_price) != float(latest_price):

            old_price = float(product.current_price)

            product.current_price = latest_price

            price_history = PriceHistory(
                product_id=product.id,
                price=latest_price
            )

            db.add(price_history)

            return {
                "product_id": product.id,
                "old_price": old_price,
                "new_price": float(latest_price),
                "price_changed": True
            }

        # No price change
        return {
            "product_id": product.id,
            "old_price": float(product.current_price),
            "new_price": float(product.current_price),
            "price_changed": False
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
        # Save all price changes together
        await db.commit()

        return results