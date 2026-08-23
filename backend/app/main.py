from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes.product import router as product_router
from app.services.scheduler_service import (
    start_scheduler,
    scheduler
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Start scheduler when FastAPI starts
    start_scheduler()

    yield

    # Stop scheduler when FastAPI shuts down
    scheduler.shutdown()


app = FastAPI(
    title="Deal Drop API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():
    return {"message": "Deal Drop API is running"}


app.include_router(product_router)