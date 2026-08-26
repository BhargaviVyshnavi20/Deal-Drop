import pytest

from unittest.mock import Mock

from app.services.firecrawl_service import FirecrawlService


# =========================================================
# TEST: SUCCESSFUL PRODUCT SCRAPING
# =========================================================

def test_scrape_product_successfully(monkeypatch):

    # Create service
    service = FirecrawlService()

    # Fake response returned by Firecrawl
    fake_result = Mock()

    fake_result.json = {
        "productName": "Test iPhone",
        "currentPrice": 50000.00,
        "currencyCode": "INR",
        "productImageUrl": "https://example.com/iphone.jpg"
    }

    # Mock Firecrawl scrape method
    mock_scrape = Mock(
        return_value=fake_result
    )

    monkeypatch.setattr(
        service.firecrawl,
        "scrape",
        mock_scrape
    )

    # Call service
    result = service.scrape_product(
        "https://example.com/test-iphone"
    )

    # Verify returned data
    assert result["productName"] == "Test iPhone"

    assert result["currentPrice"] == 50000.00

    assert result["currencyCode"] == "INR"

    assert (
        result["productImageUrl"]
        == "https://example.com/iphone.jpg"
    )

    # Verify Firecrawl was called
    mock_scrape.assert_called_once()


# =========================================================
# TEST: PRODUCT IMAGE IS OPTIONAL
# =========================================================

def test_scrape_product_without_image(monkeypatch):

    service = FirecrawlService()

    fake_result = Mock()

    fake_result.json = {
        "productName": "Test Keyboard",
        "currentPrice": 3000.00,
        "currencyCode": "INR"
    }

    monkeypatch.setattr(
        service.firecrawl,
        "scrape",
        Mock(return_value=fake_result)
    )

    result = service.scrape_product(
        "https://example.com/test-keyboard"
    )

    assert result["productName"] == "Test Keyboard"

    assert result["currentPrice"] == 3000.00

    assert result["currencyCode"] == "INR"

    # Missing optional image should become None
    assert result["productImageUrl"] is None


# =========================================================
# TEST: FIRECRAWL SCRAPING FAILURE
# =========================================================

def test_scrape_product_failure(monkeypatch):

    service = FirecrawlService()

    # Simulate Firecrawl failure
    monkeypatch.setattr(
        service.firecrawl,
        "scrape",
        Mock(
            side_effect=Exception("API request failed")
        )
    )

    with pytest.raises(Exception) as exc_info:

        service.scrape_product(
            "https://example.com/failing-product"
        )

    # Verify our custom error message
    assert (
        "Firecrawl scraping failed: API request failed"
        in str(exc_info.value)
    )