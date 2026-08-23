from fastapi import FastAPI

from app.routes.product import router as product_router
from app.routes.auth import router as auth_router


app = FastAPI(
    title="Deal Drop API",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "Deal Drop API is running"}


app.include_router(product_router)
app.include_router(auth_router)