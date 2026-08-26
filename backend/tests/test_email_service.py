from unittest.mock import Mock

import pytest

from app.services.email_service import EmailService


# =========================================================
# TEST: EMAIL SERVICE INITIALIZATION
# =========================================================

def test_email_service_initialization(monkeypatch):

    mock_resend_api_key = "test_api_key"

    monkeypatch.setattr(
        "app.services.email_service.settings.RESEND_API_KEY",
        mock_resend_api_key
    )

    service = EmailService()

    assert service is not None


# =========================================================
# TEST: SUCCESSFULLY SEND LOWEST PRICE ALERT
# =========================================================

def test_send_lowest_price_alert_successfully(monkeypatch):

    service = EmailService()

    mock_response = {
        "id": "test-email-id"
    }

    mock_send = Mock(
        return_value=mock_response
    )

    monkeypatch.setattr(
        "app.services.email_service.resend.Emails.send",
        mock_send
    )

    response = service.send_lowest_price_alert(
        recipient_email="test@example.com",
        product_name="Test Laptop",
        old_price=50000.00,
        new_price=45000.00,
        currency_code="INR",
        product_url="https://example.com/test-laptop"
    )

    assert response == mock_response

    mock_send.assert_called_once()

    email_data = mock_send.call_args[0][0]

    assert email_data["from"]

    assert email_data["to"] == [
        "test@example.com"
    ]

    assert (
        email_data["subject"]
        == "🔥 Price Drop Alert: Test Laptop"
    )

    assert "Test Laptop" in email_data["html"]

    assert "50000.0" in email_data["html"]

    assert "45000.0" in email_data["html"]

    assert "INR" in email_data["html"]

    assert "https://example.com/test-laptop" in email_data["html"]


# =========================================================
# TEST: EMAIL SEND FAILURE
# =========================================================

def test_send_lowest_price_alert_failure(monkeypatch):

    service = EmailService()

    mock_send = Mock(
        side_effect=Exception("Resend API failed")
    )

    monkeypatch.setattr(
        "app.services.email_service.resend.Emails.send",
        mock_send
    )

    with pytest.raises(
        Exception,
        match="Failed to send price alert email"
    ):

        service.send_lowest_price_alert(
            recipient_email="test@example.com",
            product_name="Test Phone",
            old_price=30000.00,
            new_price=25000.00,
            currency_code="INR",
            product_url="https://example.com/test-phone"
        )

    mock_send.assert_called_once()