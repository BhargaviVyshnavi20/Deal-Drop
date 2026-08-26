import logging
from zoneinfo import ZoneInfo

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.db.database import AsyncSessionLocal
from app.services.price_tracker_service import PriceTrackerService


logger = logging.getLogger(__name__)


scheduler = AsyncIOScheduler(
    timezone=ZoneInfo("Asia/Kolkata")
)


async def check_all_product_prices():
    """
    Scheduled job that checks prices for all tracked products.
    """

    logger.info("Scheduled price check started")

    async with AsyncSessionLocal() as db:

        price_tracker_service = PriceTrackerService()

        try:
            results = await price_tracker_service.check_all_products(
                db=db
            )

            logger.info(
                "Scheduled price check completed. "
                "Products checked: %s",
                len(results)
            )

            for result in results:
                logger.info(
                    "Price check result: %s",
                    result
                )

        except Exception as e:

            await db.rollback()

            logger.exception(
                "Scheduled price check failed: %s",
                str(e)
            )


def start_scheduler():
    """
    Start the APScheduler price checking job.
    """

    # Prevent duplicate scheduler startup
    if scheduler.running:
        logger.info("Scheduler is already running")
        return

    scheduler.add_job(
        check_all_product_prices,
        trigger="cron",
        hour=9,
        minute=0,
        id="price_checker",
        replace_existing=True,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()

    logger.info(
        "Price tracker scheduler started successfully"
    )

# def start_scheduler():

#     if scheduler.running:
#         logger.info("Scheduler is already running")
#         return

#     scheduler.add_job(
#         check_all_product_prices,
#         trigger="interval",
#         minutes=1,
#         id="price_checker",
#         replace_existing=True,
#         max_instances=1,
#         coalesce=True
#     )

#     scheduler.start()

#     print("Price tracker scheduler started successfully")

def shutdown_scheduler():
    """
    Shut down the scheduler safely.
    """

    if scheduler.running:

        scheduler.shutdown()

        logger.info(
            "Price tracker scheduler stopped"
        )