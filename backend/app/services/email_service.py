import resend

from app.core.config import settings


class EmailService:

    def __init__(self):
        resend.api_key = settings.RESEND_API_KEY

    def send_lowest_price_alert(
        self,
        recipient_email: str,
        product_name: str,
        old_price: float,
        new_price: float,
        currency_code: str,
        product_url: str
    ):
        try:
            response = resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": [recipient_email],
                "subject": f"🔥 Price Drop Alert: {product_name}",
                "html": f"""
                    <h2>Great news! 🎉</h2>

                    <p>
                        <strong>{product_name}</strong>
                        has reached its lowest tracked price so far!
                    </p>

                    <p>
                        <strong>Previous Price:</strong>
                        {currency_code} {old_price}
                    </p>

                    <p>
                        <strong>New Lowest Price:</strong>
                        {currency_code} {new_price}
                    </p>

                    <p>
                        <a href="{product_url}">
                            View Product
                        </a>
                    </p>

                    <p>— DealDrop</p>
                """
            })

            return response

        except Exception as e:
            raise Exception(
                f"Failed to send price alert email: {str(e)}"
            )