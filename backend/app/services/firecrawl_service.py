import os

from firecrawl import Firecrawl
from app.core.config import settings


class FirecrawlService:

    def __init__(self):
        self.firecrawl = Firecrawl(
        api_key=settings.FIRECRAWL_API_KEY
    )

    def scrape_product(self, url: str) -> dict:

        schema = {
            "type": "object",
            "properties": {
                "productName": {
                    "type": "string"
                },
                "currentPrice": {
                    "type": "number"
                },
                "currencyCode": {
                    "type": "string"
                },
                "productImageUrl": {
                    "type": "string"
                }
            },
            "required": [
                "productName",
                "currentPrice",
                "currencyCode"
            ]
        }

        try:
            result = self.firecrawl.scrape(
                url,
                formats=[
                    {
                        "type": "json",
                        "schema": schema
                    }
                ]
            )


            data = result.json

            return {
                "productName": data.get("productName"),
                "currentPrice": data.get("currentPrice"),
                "currencyCode": data.get("currencyCode"),
                "productImageUrl": data.get("productImageUrl")
            }

        except Exception as e:
            raise Exception(f"Firecrawl scraping failed: {str(e)}")