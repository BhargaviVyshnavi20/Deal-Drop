from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.firecrawl_service import FirecrawlService
from app.schemas.product import ProductData
from app.models.product import Product
from app.models.price_history import PriceHistory

from sqlalchemy import select

from app.services.price_tracker_service import PriceTrackerService



router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


firecrawl_service = FirecrawlService()
price_tracker_service = PriceTrackerService()


class TrackProductRequest(BaseModel):
    url: HttpUrl


@router.post("/track")
async def track_product(
    request: TrackProductRequest,
    db: AsyncSession = Depends(get_db)
):

    try:
        # Step 1: Check whether this URL is already being tracked
        result = await db.execute(
            select(Product).where(
                Product.product_url == str(request.url)
            )
        )

        existing_product = result.scalar_one_or_none()

        if existing_product:
            raise HTTPException(
                status_code=409,
                detail="This product URL is already being tracked"
            )

        # Step 2: Scrape product using Firecrawl
        scraped_data = firecrawl_service.scrape_product(
            str(request.url)
        )

        # Step 3: Validate Firecrawl JSON using Pydantic
        product_data = ProductData(
            **scraped_data
        )

        # Step 4: Create the product
        product = Product(
            product_name=product_data.productName,
            product_url=str(request.url),
            current_price=product_data.currentPrice,
            currency_code=product_data.currencyCode,
            product_image_url=(
                str(product_data.productImageUrl)
                if product_data.productImageUrl
                else None
            )
        )

        # Step 5: Add product to database session
        db.add(product)

        # Flush sends the INSERT so we can get product.id
        await db.flush()

        # Step 6: Create the initial price history record
        price_history = PriceHistory(
            product_id=product.id,
            price=product.current_price
        )

        db.add(price_history)

        # Step 7: Commit both records
        await db.commit()

        # Step 8: Refresh the product
        await db.refresh(product)

        return {
            "message": "Product tracked successfully",
            "product": {
                "id": product.id,
                "productName": product.product_name,
                "productUrl": product.product_url,
                "currentPrice": float(product.current_price),
                "currencyCode": product.currency_code,
                "productImageUrl": product.product_image_url
            }
        }

    except HTTPException:
        raise

    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
        




@router.post("/{product_id}/check-price")
async def check_product_price(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):

    # Step 1: Find the product
    result = await db.execute(
        select(Product).where(
            Product.id == product_id
        )
    )

    product = result.scalar_one_or_none()

    # Step 2: Product doesn't exist
    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    try:
        # Step 3: Check the latest price
        result = await price_tracker_service.check_product_price(
            product=product,
            db=db
        )

        await db.commit()

        return result
    
    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )




@router.post("/check-all-prices")
async def check_all_product_prices(
    db: AsyncSession = Depends(get_db)
):
    try:
        results = await price_tracker_service.check_all_products(
            db=db
        )

        return {
            "message": "Price check completed",
            "total_products": len(results),
            "results": results
        }

    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


