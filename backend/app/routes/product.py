from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, HttpUrl
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_current_user
from app.db.database import get_db
from app.models.price_history import PriceHistory
from app.models.product import Product
from app.models.user import User
from app.schemas.product import ProductData
from app.services.firecrawl_service import FirecrawlService
from app.services.price_tracker_service import PriceTrackerService


router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


firecrawl_service = FirecrawlService()
price_tracker_service = PriceTrackerService()


class TrackProductRequest(BaseModel):
    url: HttpUrl


# =========================================================
# TRACK A NEW PRODUCT
# =========================================================

@router.post(
    "/track",
    status_code=status.HTTP_201_CREATED
)
async def track_product(
    request: TrackProductRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Step 1: Check whether this URL is already tracked
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

        # Step 3: Validate scraped data
        product_data = ProductData(
            **scraped_data
        )

        # Step 4: Create product
        product = Product(
            user_id=current_user.id,
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

        # Step 5: Add product
        db.add(product)

        # Flush to generate product ID
        await db.flush()

        # Step 6: Create initial price history record
        price_history = PriceHistory(
            product_id=product.id,
            price=product.current_price
        )

        db.add(price_history)

        # Step 7: Commit
        await db.commit()

        # Step 8: Refresh product
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


# =========================================================
# CHECK ONE PRODUCT'S PRICE
# =========================================================

@router.post("/{product_id}/check-price")
async def check_product_price(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    # Find the product AND verify ownership
    result = await db.execute(
        select(Product).where(
            Product.id == product_id,
            Product.user_id == current_user.id
        )
    )

    product = result.scalar_one_or_none()

    if not product:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    try:
        # Check latest price
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


# =========================================================
# CHECK ALL PRODUCTS FOR CURRENT USER
# =========================================================

@router.post("/check-all-prices")
async def check_all_product_prices(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):

    try:
        # Get only products belonging to the logged-in user
        result = await db.execute(
            select(Product).where(
                Product.user_id == current_user.id
            )
        )

        products = result.scalars().all()

        results = []

        # Check each of the user's products
        for product in products:
            try:
                check_result = await price_tracker_service.check_product_price(
                    product=product,
                    db=db
                )

                results.append(check_result)

            except Exception as e:
                # Continue checking other products even if one fails
                results.append({
                    "product_id": product.id,
                    "price_changed": False,
                    "error": str(e)
                })

        # Save all successful price updates
        await db.commit()

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
        
# =========================================================
# RETURN PRODUCCTS RELATED TO SPECIFIC USER
# =========================================================

@router.get("/")
async def get_my_products(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await db.execute(
            select(Product)
            .where(Product.user_id == current_user.id)
            .order_by(Product.created_at.desc())
        )

        products = result.scalars().all()

        return {
            "total_products": len(products),
            "products": [
                {
                    "id": product.id,
                    "productName": product.product_name,
                    "productUrl": product.product_url,
                    "currentPrice": float(product.current_price),
                    "currencyCode": product.currency_code,
                    "productImageUrl": product.product_image_url,
                    "createdAt": product.created_at
                }
                for product in products
            ]
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ==============================================================
# used to display a price trend/chart on the DealDrop frontend
# ==============================================================

@router.get("/{product_id}/price-history")
async def get_product_price_history(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # First, verify that the product exists and belongs to the user
        product_result = await db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.user_id == current_user.id
            )
        )

        product = product_result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        # Get price history ordered from oldest to newest
        history_result = await db.execute(
            select(PriceHistory)
            .where(PriceHistory.product_id == product_id)
            .order_by(PriceHistory.recorded_at.asc())
        )

        price_history = history_result.scalars().all()

        return {
            "product_id": product.id,
            "productName": product.product_name,
            "currentPrice": float(product.current_price),
            "priceHistory": [
                {
                    "id": history.id,
                    "price": float(history.price),
                    "recordedAt": history.recorded_at
                }
                for history in price_history
            ]
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# =========================================================
# view details of one specific product
# =========================================================

@router.get("/{product_id}")
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        result = await db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.user_id == current_user.id
            )
        )

        product = result.scalar_one_or_none()

        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        return {
            "id": product.id,
            "productName": product.product_name,
            "productUrl": product.product_url,
            "currentPrice": float(product.current_price),
            "currencyCode": product.currency_code,
            "productImageUrl": product.product_image_url,
            "createdAt": product.created_at
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
 
 
 # =========================================================
# delete a tracked product
# =========================================================

@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    try:
        # Find the product and verify ownership
        result = await db.execute(
            select(Product).where(
                Product.id == product_id,
                Product.user_id == current_user.id
            )
        )

        product = result.scalar_one_or_none()

        # Product doesn't exist or belongs to another user
        if not product:
            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        # Delete the product
        await db.delete(product)

        # Save changes
        await db.commit()

        return {
            "message": "Product deleted successfully",
            "product_id": product_id
        }

    except HTTPException:
        raise

    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
       
