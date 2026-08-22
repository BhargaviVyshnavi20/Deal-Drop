from app.services.firecrawl_service import FirecrawlService
from app.schemas.product import ProductData


def main():

    url = "https://www.amazon.in/Norwegian-Wood-Haruki-Murakami-ebook/dp/B005TKD6NY"

    # Step 1: Scrape using Firecrawl
    service = FirecrawlService()

    scraped_data = service.scrape_product(url)

    print("\nRaw Firecrawl Data")
    print("------------------------")
    print(scraped_data)

    # Step 2: Validate using Pydantic
    product = ProductData(**scraped_data)

    print("\nValidated Product")
    print("------------------------")
    print(f"Product Name  : {product.productName}")
    print(f"Current Price : {product.currentPrice}")
    print(f"Currency      : {product.currencyCode}")
    print(f"Product Image : {product.productImageUrl}")


if __name__ == "__main__":
    main()