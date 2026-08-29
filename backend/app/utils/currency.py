def normalize_currency(currency: str | None) -> str:
    if not currency:
        return "INR"

    currency = currency.strip().upper()

    currency_map = {
        "₹": "INR",
        "RS": "INR",
        "RS.": "INR",
        "INR": "INR",
        "RUPEE": "INR",
        "RUPEES": "INR",

        "$": "USD",
        "USD": "USD",

        "€": "EUR",
        "EUR": "EUR",

        "£": "GBP",
        "GBP": "GBP",
    }

    return currency_map.get(currency, currency)