from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.db.database import AsyncSessionLocal
from app.services.price_tracker_service import PriceTrackerService


scheduler = AsyncIOScheduler(
    timezone=ZoneInfo("Asia/Kolkata")
)


async def check_all_product_prices():
    """
    Scheduled job that checks prices for all tracked products.
    """

    async with AsyncSessionLocal() as db:

        price_tracker_service = PriceTrackerService()

        try:
            results = await price_tracker_service.check_all_products(
                db=db
            )

            print("Scheduled price check completed")
            print(results)

        except Exception as e:
            await db.rollback()

            print(
                f"Scheduled price check failed: {str(e)}"
            )


def start_scheduler():

    scheduler.add_job(
        check_all_product_prices,
        trigger="cron",
        hour=9,
        minute=0,
        id="price_checker",
        replace_existing=True
    )

    scheduler.start()

    print("Price tracker scheduler started")