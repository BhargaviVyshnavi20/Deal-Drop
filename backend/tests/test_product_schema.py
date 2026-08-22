from app.schemas.product import ProductData


data = {
    "productName": "Nike Air Max 270",
    "currencyCode": "INR",
    "productImageUrl": None
}


product = ProductData(**data)

print(product)
print(product.model_dump())