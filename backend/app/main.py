from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routes.product import router as product_router
from app.routes.auth import router as auth_router

from app.services.scheduler_service import (
    start_scheduler,
    shutdown_scheduler
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    # Application startup
    start_scheduler()

    yield

    # Application shutdown
    shutdown_scheduler()


app = FastAPI(
    title="Deal Drop API",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
async def root():

    return {
        "message": "Deal Drop API is running"
    }


app.include_router(product_router)

app.include_router(auth_router)