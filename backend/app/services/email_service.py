import html
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
        product_url: str,
        product_image_url: str | None = None,
    ):
        try:
            # Calculations
            savings = old_price - new_price

            percentage_drop = (
                (savings / old_price) * 100
                if old_price > 0
                else 0
            )

            # Escape dynamic text for HTML safety
            safe_product_name = html.escape(product_name)
            safe_product_url = html.escape(product_url)

            # Product image section
            image_html = ""

            if product_image_url:
                safe_image_url = html.escape(product_image_url)

                image_html = f"""
                    <div style="text-align: center; padding: 30px 20px 10px;">
                        <img
                            src="{safe_image_url}"
                            alt="{safe_product_name}"
                            style="
                                width: 180px;
                                max-width: 100%;
                                height: 220px;
                                object-fit: contain;
                                border-radius: 12px;
                                display: inline-block;
                            "
                        />
                    </div>
                """

            # Email HTML
            email_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
            </head>

            <body style="
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
                font-family: Arial, Helvetica, sans-serif;
                color: #1f2937;
            ">

                <div style="
                    width: 100%;
                    padding: 30px 10px;
                    box-sizing: border-box;
                ">

                    <div style="
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.08);
                    ">

                        <!-- Header -->
                        <div style="
                            background-color: #ff5a1f;
                            padding: 22px;
                            text-align: center;
                            color: #ffffff;
                        ">
                            <h1 style="
                                margin: 0;
                                font-size: 24px;
                                font-weight: 700;
                            ">
                                🎉 Price Drop Alert!
                            </h1>

                            <p style="
                                margin: 8px 0 0;
                                font-size: 14px;
                                color: #fff3ee;
                            ">
                                Great news! Your tracked product is now cheaper.
                            </p>
                        </div>

                        <!-- Product Image -->
                        {image_html}

                        <!-- Product Content -->
                        <div style="padding: 25px 30px 30px;">

                            <!-- Product Name -->
                            <h2 style="
                                margin: 10px 0 25px;
                                font-size: 20px;
                                line-height: 1.4;
                                text-transform: uppercase;
                                color: #1f2937;
                            ">
                                {safe_product_name}
                            </h2>

                            <!-- Price Drop Banner -->
                            <div style="
                                background-color: #fff7dc;
                                border-left: 4px solid #f4a300;
                                padding: 16px;
                                margin-bottom: 25px;
                                border-radius: 4px;
                            ">
                                <strong style="
                                    font-size: 16px;
                                    color: #7a5200;
                                ">
                                    📉 Price dropped by {percentage_drop:.1f}%!
                                </strong>
                            </div>

                            <!-- Previous Price -->
                            <div style="
                                background-color: #f8fafc;
                                padding: 18px;
                                margin-bottom: 15px;
                                border-radius: 6px;
                            ">
                                <p style="
                                    margin: 0 0 8px;
                                    font-size: 14px;
                                    color: #6b7280;
                                ">
                                    Previous Price
                                </p>

                                <p style="
                                    margin: 0;
                                    font-size: 20px;
                                    color: #9ca3af;
                                    text-decoration: line-through;
                                ">
                                    {currency_code} {old_price:,.2f}
                                </p>
                            </div>

                            <!-- Current Price -->
                            <div style="
                                padding: 18px;
                                margin-bottom: 15px;
                            ">
                                <p style="
                                    margin: 0 0 8px;
                                    font-size: 14px;
                                    color: #6b7280;
                                ">
                                    Current Lowest Price
                                </p>

                                <p style="
                                    margin: 0;
                                    font-size: 32px;
                                    font-weight: 700;
                                    color: #f4511e;
                                ">
                                    {currency_code} {new_price:,.2f}
                                </p>
                            </div>

                            <!-- Savings -->
                            <div style="
                                background-color: #dcfce7;
                                padding: 18px;
                                border-radius: 6px;
                                margin-bottom: 30px;
                            ">
                                <p style="
                                    margin: 0 0 8px;
                                    font-size: 14px;
                                    color: #166534;
                                ">
                                    You Save
                                </p>

                                <p style="
                                    margin: 0;
                                    font-size: 24px;
                                    font-weight: 700;
                                    color: #15803d;
                                ">
                                    {currency_code} {savings:,.2f}
                                </p>
                            </div>

                            <!-- CTA Button -->
                            <div style="text-align: center;">
                                <a
                                    href="{safe_product_url}"
                                    style="
                                        display: inline-block;
                                        background-color: #ff5a1f;
                                        color: #ffffff;
                                        text-decoration: none;
                                        padding: 16px 35px;
                                        border-radius: 7px;
                                        font-size: 16px;
                                        font-weight: 700;
                                    "
                                >
                                    View Product →
                                </a>
                            </div>

                            <!-- Footer -->
                            <div style="
                                text-align: center;
                                margin-top: 35px;
                                padding-top: 20px;
                                border-top: 1px solid #e5e7eb;
                            ">
                                <p style="
                                    margin: 0;
                                    font-size: 13px;
                                    color: #9ca3af;
                                ">
                                    You're receiving this alert because you're tracking this product on
                                    <strong>DealDrop</strong>.
                                </p>
                            </div>

                        </div>

                    </div>

                </div>

            </body>
            </html>
            """

            response = resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": [recipient_email],
                "subject": f"🔥 Price Drop Alert: {product_name}",
                "html": email_html,
            })

            return response

        except Exception as e:
            raise Exception(
                f"Failed to send price alert email: {str(e)}"
            )


    def send_password_reset_email(
        self,
        recipient_email: str,
        reset_url: str,
    ):
        """
        Send a password reset email.

        The reset URL contains the one-time reset token.
        """

        try:
            # Escape dynamic content for HTML safety
            safe_reset_url = html.escape(
                reset_url,
                quote=True
            )

            email_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <meta
                    name="viewport"
                    content="width=device-width, initial-scale=1.0"
                >
            </head>

            <body style="
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
                font-family: Arial, Helvetica, sans-serif;
                color: #1f2937;
            ">

                <div style="
                    width: 100%;
                    padding: 30px 10px;
                    box-sizing: border-box;
                ">

                    <div style="
                        max-width: 600px;
                        margin: 0 auto;
                        background-color: #ffffff;
                        border-radius: 12px;
                        overflow: hidden;
                        box-shadow:
                            0 4px 15px
                            rgba(0, 0, 0, 0.08);
                    ">

                        <!-- Header -->
                        <div style="
                            background-color: #ff5a1f;
                            padding: 25px;
                            text-align: center;
                            color: #ffffff;
                        ">
                            <h1 style="
                                margin: 0;
                                font-size: 26px;
                                font-weight: 700;
                            ">
                                DealDrop
                            </h1>

                            <p style="
                                margin: 8px 0 0;
                                font-size: 14px;
                                color: #fff3ee;
                            ">
                                Password Reset
                            </p>
                        </div>

                        <!-- Content -->
                        <div style="
                            padding: 35px 30px;
                        ">

                            <h2 style="
                                margin: 0 0 18px;
                                font-size: 22px;
                                color: #1f2937;
                            ">
                                Reset your password
                            </h2>

                            <p style="
                                margin: 0 0 20px;
                                font-size: 15px;
                                line-height: 1.6;
                                color: #4b5563;
                            ">
                                We received a request to reset your
                                DealDrop password.
                            </p>

                            <p style="
                                margin: 0 0 28px;
                                font-size: 15px;
                                line-height: 1.6;
                                color: #4b5563;
                            ">
                                Click the button below to choose a
                                new password.
                            </p>

                            <!-- CTA -->
                            <div style="
                                text-align: center;
                                margin: 30px 0;
                            ">
                                <a
                                    href="{safe_reset_url}"
                                    style="
                                        display: inline-block;
                                        background-color: #ff5a1f;
                                        color: #ffffff;
                                        text-decoration: none;
                                        padding: 15px 32px;
                                        border-radius: 7px;
                                        font-size: 16px;
                                        font-weight: 700;
                                    "
                                >
                                    Reset Password
                                </a>
                            </div>

                            <!-- Expiration -->
                            <div style="
                                background-color: #fff7dc;
                                border-left:
                                    4px solid #f4a300;
                                padding: 15px;
                                margin-top: 25px;
                                border-radius: 4px;
                            ">
                                <p style="
                                    margin: 0;
                                    font-size: 14px;
                                    line-height: 1.5;
                                    color: #7a5200;
                                ">
                                    This password reset link will
                                    expire in 15 minutes.
                                </p>
                            </div>

                            <!-- Security notice -->
                            <p style="
                                margin: 28px 0 0;
                                font-size: 13px;
                                line-height: 1.6;
                                color: #9ca3af;
                            ">
                                If you did not request a password
                                reset, you can safely ignore this
                                email. Your password will remain
                                unchanged.
                            </p>

                            <!-- Footer -->
                            <div style="
                                text-align: center;
                                margin-top: 35px;
                                padding-top: 20px;
                                border-top:
                                    1px solid #e5e7eb;
                            ">
                                <p style="
                                    margin: 0;
                                    font-size: 13px;
                                    color: #9ca3af;
                                ">
                                    DealDrop
                                </p>
                            </div>

                        </div>

                    </div>

                </div>

            </body>
            </html>
            """

            response = resend.Emails.send({
                "from": settings.RESEND_FROM_EMAIL,
                "to": [recipient_email],
                "subject": "Reset your DealDrop password",
                "html": email_html,
            })

            return response

        except Exception as e:
            raise Exception(
                f"Failed to send password reset email: {str(e)}"
            )