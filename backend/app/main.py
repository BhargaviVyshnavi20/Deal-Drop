from fastapi import FastAPI
from app.routes.product import router as product_router

app = FastAPI(
    title="Deal Drop API",
    version="1.0.0",
)


@app.get("/")
async def root():
    return {"message": "Deal Drop API is running"}



app.include_router(product_router)