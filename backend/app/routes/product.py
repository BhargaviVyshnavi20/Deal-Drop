from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.services.firecrawl_service import FirecrawlService
from app.schemas.product import ProductData
from app.models.product import Product


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


firecrawl_service = FirecrawlService()


class TrackProductRequest(BaseModel):
    url: HttpUrl


@router.post("/track")
async def track_product(
    request: TrackProductRequest,
    db: AsyncSession = Depends(get_db)
):

    try:
        # Step 1: Scrape product using Firecrawl
        scraped_data = firecrawl_service.scrape_product(
            str(request.url)
        )

        # Step 2: Validate Firecrawl JSON using Pydantic
        product_data = ProductData(
            **scraped_data
        )

        # Step 3: Convert validated data to SQLAlchemy model
        product = Product(
            product_name=product_data.productName,
            current_price=product_data.currentPrice,
            currency_code=product_data.currencyCode,
            product_image_url=(
                str(product_data.productImageUrl)
                if product_data.productImageUrl
                else None
            )
        )

        # Step 4: Add product to database session
        db.add(product)

        # Step 5: Commit to PostgreSQL
        await db.commit()

        # Step 6: Get generated database ID
        await db.refresh(product)

        return {
            "message": "Product tracked successfully",
            "product": {
                "id": product.id,
                "productName": product.product_name,
                "currentPrice": float(product.current_price),
                "currencyCode": product.currency_code,
                "productImageUrl": product.product_image_url
            }
        }

    except Exception as e:

        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )