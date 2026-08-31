
import asyncio

from app.db.database import AsyncSessionLocal
from app.services.price_tracker_service import PriceTrackerService


async def main():
    async with AsyncSessionLocal() as db:
        service = PriceTrackerService()

        try:
            results = await service.check_all_products(db)

            print('PRICE CHECK RESULTS:')
            print(results)

        except Exception as e:
            await db.rollback()
            print('PRICE CHECK ERROR:')
            print(type(e).__name__, str(e))


asyncio.run(main())
PY
python /tmp/test_price_check.py"