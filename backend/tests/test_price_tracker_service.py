import pytest

from unittest.mock import Mock

from sqlalchemy import select

from app.models.user import User
from app.models.product import Product
from app.models.price_history import PriceHistory
from app.services.price_tracker_service import PriceTrackerService


# =========================================================
# TEST: PRICE DECREASES
# =========================================================

@pytest.mark.asyncio
async def test_price_decreases(
    db_session,
    monkeypatch
):

    # Create user
    user = User(
        name="Test User",
        email="serviceuser1@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create product
    product = Product(
        user_id=user.id,
        product_name="Test Phone",
        product_url="https://example.com/test-phone-service",
        current_price=50000.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Create service
    service = PriceTrackerService()

    # Fake Firecrawl response with lower price
    fake_scraped_data = {
        "productName": "Test Phone",
        "currentPrice": 45000.00,
        "currencyCode": "INR",
        "productImageUrl": None
    }

    monkeypatch.setattr(
        service.firecrawl_service,
        "scrape_product",
        Mock(return_value=fake_scraped_data)
    )

    # Run price check
    result = await service.check_product_price(
        product=product,
        db=db_session
    )

    await db_session.commit()
    await db_session.refresh(product)

    # Verify result
    assert result["product_id"] == product.id
    assert result["old_price"] == 50000.00
    assert result["new_price"] == 45000.00
    assert result["price_changed"] is True

    # Verify product price updated
    assert float(product.current_price) == 45000.00

    # Verify price history created
    history_result = await db_session.execute(
        select(PriceHistory).where(
            PriceHistory.product_id == product.id
        )
    )

    history = history_result.scalars().all()

    assert len(history) == 1
    assert float(history[0].price) == 45000.00


# =========================================================
# TEST: PRICE INCREASES
# =========================================================

@pytest.mark.asyncio
async def test_price_increases(
    db_session,
    monkeypatch
):

    user = User(
        name="Test User",
        email="serviceuser2@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    product = Product(
        user_id=user.id,
        product_name="Test Laptop",
        product_url="https://example.com/test-laptop-service",
        current_price=50000.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    service = PriceTrackerService()

    fake_scraped_data = {
        "productName": "Test Laptop",
        "currentPrice": 55000.00,
        "currencyCode": "INR",
        "productImageUrl": None
    }

    monkeypatch.setattr(
        service.firecrawl_service,
        "scrape_product",
        Mock(return_value=fake_scraped_data)
    )

    result = await service.check_product_price(
        product=product,
        db=db_session
    )

    await db_session.commit()
    await db_session.refresh(product)

    assert result["price_changed"] is True
    assert result["old_price"] == 50000.00
    assert result["new_price"] == 55000.00

    assert float(product.current_price) == 55000.00

    history_result = await db_session.execute(
        select(PriceHistory).where(
            PriceHistory.product_id == product.id
        )
    )

    history = history_result.scalars().all()

    assert len(history) == 1
    assert float(history[0].price) == 55000.00


# =========================================================
# TEST: PRICE REMAINS THE SAME
# =========================================================

@pytest.mark.asyncio
async def test_price_remains_unchanged(
    db_session,
    monkeypatch
):

    user = User(
        name="Test User",
        email="serviceuser3@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    product = Product(
        user_id=user.id,
        product_name="Test Headphones",
        product_url="https://example.com/test-headphones-service",
        current_price=3000.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    service = PriceTrackerService()

    fake_scraped_data = {
        "productName": "Test Headphones",
        "currentPrice": 3000.00,
        "currencyCode": "INR",
        "productImageUrl": None
    }

    monkeypatch.setattr(
        service.firecrawl_service,
        "scrape_product",
        Mock(return_value=fake_scraped_data)
    )

    result = await service.check_product_price(
        product=product,
        db=db_session
    )

    await db_session.commit()
    await db_session.refresh(product)

    # Verify no change
    assert result["price_changed"] is False
    assert result["old_price"] == 3000.00
    assert result["new_price"] == 3000.00

    assert float(product.current_price) == 3000.00

    # Verify NO price history record was created
    history_result = await db_session.execute(
        select(PriceHistory).where(
            PriceHistory.product_id == product.id
        )
    )

    history = history_result.scalars().all()

    assert len(history) == 0

# =========================================================
# TEST: CHECK ALL PRODUCTS SUCCESSFULLY
# =========================================================

@pytest.mark.asyncio
async def test_check_all_products_successfully(
    db_session,
    monkeypatch
):

    # Create user
    user = User(
        name="Check All User",
        email="checkallservice@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create first product
    product_1 = Product(
        user_id=user.id,
        product_name="Product One",
        product_url="https://example.com/service-product-one",
        current_price=1000.00,
        currency_code="INR"
    )

    # Create second product
    product_2 = Product(
        user_id=user.id,
        product_name="Product Two",
        product_url="https://example.com/service-product-two",
        current_price=2000.00,
        currency_code="INR"
    )

    db_session.add_all([
        product_1,
        product_2
    ])

    await db_session.commit()

    await db_session.refresh(product_1)
    await db_session.refresh(product_2)

    service = PriceTrackerService()

    # Mock the individual product price-check method
    async def mock_check_product_price(product, db):

        return {
            "product_id": product.id,
            "old_price": float(product.current_price),
            "new_price": float(product.current_price),
            "price_changed": False
        }

    monkeypatch.setattr(
        service,
        "check_product_price",
        mock_check_product_price
    )

    # Run check for all products
    results = await service.check_all_products(
        db=db_session
    )

    # Verify results
    assert len(results) == 2

    checked_product_ids = {
        result["product_id"]
        for result in results
    }

    assert product_1.id in checked_product_ids
    assert product_2.id in checked_product_ids

# =========================================================
# TEST: CHECK ALL PRODUCTS CONTINUES AFTER FAILURE
# =========================================================

@pytest.mark.asyncio
async def test_check_all_products_continues_after_failure(
    db_session,
    monkeypatch
):

    user = User(
        name="Failure Test User",
        email="failuretest@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    product_1 = Product(
        user_id=user.id,
        product_name="Successful Product",
        product_url="https://example.com/successful-product",
        current_price=1000.00,
        currency_code="INR"
    )

    product_2 = Product(
        user_id=user.id,
        product_name="Failing Product",
        product_url="https://example.com/failing-product",
        current_price=2000.00,
        currency_code="INR"
    )

    db_session.add_all([
        product_1,
        product_2
    ])

    await db_session.commit()

    await db_session.refresh(product_1)
    await db_session.refresh(product_2)

    service = PriceTrackerService()

    async def mock_check_product_price(product, db):

        if product.id == product_2.id:

            raise Exception("Firecrawl scraping failed")

        return {
            "product_id": product.id,
            "old_price": float(product.current_price),
            "new_price": float(product.current_price),
            "price_changed": False
        }

    monkeypatch.setattr(
        service,
        "check_product_price",
        mock_check_product_price
    )

    results = await service.check_all_products(
        db=db_session
    )

    # Both products should have results
    assert len(results) == 2

    # Find each result
    successful_result = next(
        result
        for result in results
        if result["product_id"] == product_1.id
    )

    failed_result = next(
        result
        for result in results
        if result["product_id"] == product_2.id
    )

    # Successful product was checked
    assert successful_result["price_changed"] is False

    # Failed product contains error information
    assert failed_result["price_changed"] is False

    assert (
        failed_result["error"]
        == "Firecrawl scraping failed"
    )

# =========================================================
# TEST: NEW LOWEST PRICE SENDS EMAIL
# =========================================================

@pytest.mark.asyncio
async def test_new_lowest_price_sends_email(
    db_session,
    monkeypatch
):

    user = User(
        name="Lowest Price User",
        email="lowest@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    product = Product(
        user_id=user.id,
        product_name="Test Phone",
        product_url="https://example.com/lowest-price-phone",
        current_price=50000.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Existing price history
    db_session.add(
        PriceHistory(
            product_id=product.id,
            price=50000.00
        )
    )

    await db_session.commit()

    service = PriceTrackerService()

    fake_scraped_data = {
        "productName": "Test Phone",
        "currentPrice": 45000.00,
        "currencyCode": "INR",
        "productImageUrl": None
    }

    monkeypatch.setattr(
        service.firecrawl_service,
        "scrape_product",
        Mock(return_value=fake_scraped_data)
    )

    mock_send_email = Mock()

    monkeypatch.setattr(
        service.email_service,
        "send_lowest_price_alert",
        mock_send_email
    )

    result = await service.check_product_price(
        product=product,
        db=db_session
    )

    assert result["price_changed"] is True
    assert result["new_lowest_price"] is True
    assert result["email_sent"] is True

    mock_send_email.assert_called_once()

    mock_send_email.assert_called_once_with(
        recipient_email=user.email,
        product_name=product.product_name,
        old_price=50000.00,
        new_price=45000.00,
        currency_code="INR",
        product_url=product.product_url
    )


# =========================================================
# TEST: PRICE DROP BUT NOT NEW LOWEST
# =========================================================

@pytest.mark.asyncio
async def test_price_drop_not_new_lowest_does_not_send_email(
    db_session,
    monkeypatch
):

    user = User(
        name="History User",
        email="history@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    product = Product(
        user_id=user.id,
        product_name="Test Laptop",
        product_url="https://example.com/history-laptop",
        current_price=50000.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Historical lowest price is already 40000
    db_session.add(
        PriceHistory(
            product_id=product.id,
            price=40000.00
        )
    )

    await db_session.commit()

    service = PriceTrackerService()

    # Current price drops to 45000,
    # but historical lowest is still 40000
    fake_scraped_data = {
        "productName": "Test Laptop",
        "currentPrice": 45000.00,
        "currencyCode": "INR",
        "productImageUrl": None
    }

    monkeypatch.setattr(
        service.firecrawl_service,
        "scrape_product",
        Mock(return_value=fake_scraped_data)
    )

    mock_send_email = Mock()

    monkeypatch.setattr(
        service.email_service,
        "send_lowest_price_alert",
        mock_send_email
    )

    result = await service.check_product_price(
        product=product,
        db=db_session
    )

    assert result["price_changed"] is True
    assert result["new_lowest_price"] is False
    assert result["email_sent"] is False

    mock_send_email.assert_not_called()

# =========================================================
# TEST: EMAIL FAILURE DOES NOT BREAK PRICE TRACKING
# =========================================================

@pytest.mark.asyncio
async def test_email_failure_does_not_break_price_tracking(
    db_session,
    monkeypatch
):

    user = User(
        name="Email Failure User",
        email="emailfailure@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    product = Product(
        user_id=user.id,
        product_name="Test Tablet",
        product_url="https://example.com/email-failure-tablet",
        current_price=30000.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Existing history
    db_session.add(
        PriceHistory(
            product_id=product.id,
            price=30000.00
        )
    )

    await db_session.commit()

    service = PriceTrackerService()

    fake_scraped_data = {
        "productName": "Test Tablet",
        "currentPrice": 25000.00,
        "currencyCode": "INR",
        "productImageUrl": None
    }

    monkeypatch.setattr(
        service.firecrawl_service,
        "scrape_product",
        Mock(return_value=fake_scraped_data)
    )

    # Simulate Resend failure
    monkeypatch.setattr(
        service.email_service,
        "send_lowest_price_alert",
        Mock(
            side_effect=Exception("Resend API failed")
        )
    )

    result = await service.check_product_price(
        product=product,
        db=db_session
    )

    # Price tracking should still succeed
    assert result["price_changed"] is True
    assert result["new_lowest_price"] is True
    assert result["email_sent"] is False

    # Product price should still be updated
    assert float(product.current_price) == 25000.00

    # New history should still be added
    history_result = await db_session.execute(
        select(PriceHistory).where(
            PriceHistory.product_id == product.id
        )
    )

    history = history_result.scalars().all()

    assert len(history) == 2


# =========================================================
# TEST: UNCHANGED PRICE DOES NOT SEND EMAIL
# =========================================================

@pytest.mark.asyncio
async def test_unchanged_price_does_not_send_email(
    db_session,
    monkeypatch
):

    user = User(
        name="No Change User",
        email="nochange@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    product = Product(
        user_id=user.id,
        product_name="Test Headphones",
        product_url="https://example.com/no-change-headphones",
        current_price=5000.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    service = PriceTrackerService()

    fake_scraped_data = {
        "productName": "Test Headphones",
        "currentPrice": 5000.00,
        "currencyCode": "INR",
        "productImageUrl": None
    }

    monkeypatch.setattr(
        service.firecrawl_service,
        "scrape_product",
        Mock(return_value=fake_scraped_data)
    )

    mock_send_email = Mock()

    monkeypatch.setattr(
        service.email_service,
        "send_lowest_price_alert",
        mock_send_email
    )

    result = await service.check_product_price(
        product=product,
        db=db_session
    )

    assert result["price_changed"] is False
    assert result["new_lowest_price"] is False

    mock_send_email.assert_not_called()

