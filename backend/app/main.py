from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.product import router as product_router
from app.routes.auth import router as auth_router

from app.services.scheduler_service import (
    start_scheduler,
    shutdown_scheduler,
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
    lifespan=lifespan,
)


# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {
        "message": "Deal Drop API is running"
    }


app.include_router(product_router)
app.include_router(auth_router)