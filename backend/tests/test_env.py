import os
from dotenv import load_dotenv


load_dotenv()

api_key = os.getenv("FIRECRAWL_API_KEY")

if api_key:
    print("Firecrawl API key loaded successfully")
    print("Key starts with:", api_key[:5])
else:
    print("Firecrawl API key NOT found")