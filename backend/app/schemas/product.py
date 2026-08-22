from pydantic import BaseModel, HttpUrl


class ProductData(BaseModel):
    productName: str
    currentPrice: float
    currencyCode: str
    productImageUrl: HttpUrl | None = None