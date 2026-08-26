import pytest

from unittest.mock import Mock, AsyncMock

from app.models.product import Product
from app.models.price_history import PriceHistory

from app.routes.product import (
    firecrawl_service,
    price_tracker_service
)

# =========================================================
# HELPER: CREATE USER AND GET JWT TOKEN
# =========================================================

async def create_user_and_get_token(
    client,
    name,
    email,
    password="TestPassword123"
):
    # -----------------------------------------------------
    # Step 1: Signup
    # -----------------------------------------------------

    signup_response = await client.post(
        "/auth/signup",
        json={
            "name": name,
            "email": email,
            "password": password
        }
    )

    assert signup_response.status_code == 201

    user_id = signup_response.json()["user"]["id"]

    # -----------------------------------------------------
    # Step 2: Login
    # -----------------------------------------------------

    login_response = await client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    return headers, user_id


# =========================================================
# HELPER: CREATE PRODUCT DIRECTLY IN TEST DATABASE
# =========================================================

async def create_product(
    db_session,
    user_id,
    product_name="Test Product",
    product_url="https://example.com/test-product",
    current_price=1000.00,
    currency_code="INR",
    product_image_url=None
):
    product = Product(
        user_id=user_id,
        product_name=product_name,
        product_url=product_url,
        current_price=current_price,
        currency_code=currency_code,
        product_image_url=product_image_url
    )

    db_session.add(product)

    await db_session.commit()
    await db_session.refresh(product)

    return product


# =========================================================
# TEST: GET PRODUCTS REQUIRES AUTHENTICATION
# =========================================================

@pytest.mark.asyncio
async def test_get_products_requires_authentication(client):

    response = await client.get(
        "/products/"
    )

    assert response.status_code == 401


# =========================================================
# TEST: USER SEES ONLY THEIR OWN PRODUCTS
# =========================================================

@pytest.mark.asyncio
async def test_get_my_products_returns_only_current_users_products(
    client,
    db_session
):

    # Create User 1
    headers_user_1, user_1_id = await create_user_and_get_token(
        client,
        "User One",
        "user1@example.com"
    )

    # Create User 2
    headers_user_2, user_2_id = await create_user_and_get_token(
        client,
        "User Two",
        "user2@example.com"
    )

    # Create product for User 1
    await create_product(
        db_session=db_session,
        user_id=user_1_id,
        product_name="User 1 Product",
        product_url="https://example.com/user1-product"
    )

    # Create product for User 2
    await create_product(
        db_session=db_session,
        user_id=user_2_id,
        product_name="User 2 Product",
        product_url="https://example.com/user2-product"
    )

    # User 1 requests products
    response = await client.get(
        "/products/",
        headers=headers_user_1
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total_products"] == 1

    assert len(data["products"]) == 1

    assert data["products"][0]["productName"] == "User 1 Product"


# =========================================================
# TEST: GET SINGLE PRODUCT
# =========================================================

@pytest.mark.asyncio
async def test_get_single_product(
    client,
    db_session
):

    # Create user and get JWT token
    headers, user_id = await create_user_and_get_token(
        client,
        "Product User",
        "productuser@example.com"
    )

    # Create product
    product = await create_product(
        db_session=db_session,
        user_id=user_id,
        product_name="My Laptop",
        product_url="https://example.com/my-laptop",
        current_price=50000.00
    )

    # Get product
    response = await client.get(
        f"/products/{product.id}",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == product.id

    assert data["productName"] == "My Laptop"

    assert data["productUrl"] == "https://example.com/my-laptop"

    assert data["currentPrice"] == 50000.00

    assert data["currencyCode"] == "INR"


# =========================================================
# TEST: USER CANNOT ACCESS ANOTHER USER'S PRODUCT
# =========================================================

@pytest.mark.asyncio
async def test_user_cannot_access_another_users_product(
    client,
    db_session
):

    # Create User 1 (product owner)
    headers_user_1, user_1_id = await create_user_and_get_token(
        client,
        "Owner",
        "owner@example.com"
    )

    # Create User 2
    headers_user_2, user_2_id = await create_user_and_get_token(
        client,
        "Other User",
        "other@example.com"
    )

    # Create product belonging to User 1
    product = await create_product(
        db_session=db_session,
        user_id=user_1_id,
        product_name="Private Product",
        product_url="https://example.com/private-product"
    )

    # User 2 tries to access User 1's product
    response = await client.get(
        f"/products/{product.id}",
        headers=headers_user_2
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found"

    # Verify owner can access the product
    owner_response = await client.get(
        f"/products/{product.id}",
        headers=headers_user_1
    )

    assert owner_response.status_code == 200


# =========================================================
# TEST: GET NON-EXISTENT PRODUCT
# =========================================================

@pytest.mark.asyncio
async def test_get_nonexistent_product(
    client
):

    headers, user_id = await create_user_and_get_token(
        client,
        "Test User",
        "nonexistent@example.com"
    )

    response = await client.get(
        "/products/99999",
        headers=headers
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found"


# =========================================================
# TEST: DELETE PRODUCT
# =========================================================

@pytest.mark.asyncio
async def test_delete_product(
    client,
    db_session
):

    # Create user
    headers, user_id = await create_user_and_get_token(
        client,
        "Delete User",
        "delete@example.com"
    )

    # Create product
    product = await create_product(
        db_session=db_session,
        user_id=user_id,
        product_name="Product To Delete",
        product_url="https://example.com/delete-product"
    )

    product_id = product.id

    # Delete product
    response = await client.delete(
        f"/products/{product_id}",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Product deleted successfully"

    assert data["product_id"] == product_id

    # Verify product is deleted
    deleted_product = await db_session.get(
        Product,
        product_id
    )

    assert deleted_product is None


# =========================================================
# TEST: USER CANNOT DELETE ANOTHER USER'S PRODUCT
# =========================================================

@pytest.mark.asyncio
async def test_user_cannot_delete_another_users_product(
    client,
    db_session
):

    # Create User 1
    headers_user_1, user_1_id = await create_user_and_get_token(
        client,
        "Owner",
        "deleteowner@example.com"
    )

    # Create User 2
    headers_user_2, user_2_id = await create_user_and_get_token(
        client,
        "Other User",
        "deleteother@example.com"
    )

    # Create product belonging to User 1
    product = await create_product(
        db_session=db_session,
        user_id=user_1_id,
        product_name="Protected Product",
        product_url="https://example.com/protected-product"
    )

    # User 2 tries to delete the product
    response = await client.delete(
        f"/products/{product.id}",
        headers=headers_user_2
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found"

    # Verify product still exists
    existing_product = await db_session.get(
        Product,
        product.id
    )

    assert existing_product is not None

    assert existing_product.user_id == user_1_id


# =========================================================
# TEST: DELETE NON-EXISTENT PRODUCT
# =========================================================

@pytest.mark.asyncio
async def test_delete_nonexistent_product(
    client
):

    headers, user_id = await create_user_and_get_token(
        client,
        "Delete Test User",
        "deletenonexistent@example.com"
    )

    response = await client.delete(
        "/products/99999",
        headers=headers
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found"


# =========================================================
# TEST: GET PRODUCT PRICE HISTORY
# =========================================================

@pytest.mark.asyncio
async def test_get_product_price_history(
    client,
    db_session
):

    # Create user
    headers, user_id = await create_user_and_get_token(
        client,
        "History User",
        "history@example.com"
    )

    # Create product
    product = await create_product(
        db_session=db_session,
        user_id=user_id,
        product_name="History Product",
        product_url="https://example.com/history-product",
        current_price=800.00
    )

    # Create price history records
    history_1 = PriceHistory(
        product_id=product.id,
        price=1000.00
    )

    history_2 = PriceHistory(
        product_id=product.id,
        price=800.00
    )

    db_session.add_all([
        history_1,
        history_2
    ])

    await db_session.commit()

    # Get price history
    response = await client.get(
        f"/products/{product.id}/price-history",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product.id

    assert data["productName"] == "History Product"

    assert data["currentPrice"] == 800.00

    assert len(data["priceHistory"]) == 2

    assert data["priceHistory"][0]["price"] == 1000.00

    assert data["priceHistory"][1]["price"] == 800.00


# =========================================================
# TEST: USER CANNOT ACCESS ANOTHER USER'S PRICE HISTORY
# =========================================================

@pytest.mark.asyncio
async def test_user_cannot_access_another_users_price_history(
    client,
    db_session
):

    # Create product owner
    headers_owner, owner_id = await create_user_and_get_token(
        client,
        "History Owner",
        "historyowner@example.com"
    )

    # Create another user
    headers_other, other_user_id = await create_user_and_get_token(
        client,
        "Other User",
        "historyother@example.com"
    )

    # Create product for owner
    product = await create_product(
        db_session=db_session,
        user_id=owner_id,
        product_name="Private History Product",
        product_url="https://example.com/private-history"
    )

    # Add history
    history = PriceHistory(
        product_id=product.id,
        price=1000.00
    )

    db_session.add(history)

    await db_session.commit()

    # Other user tries to access history
    response = await client.get(
        f"/products/{product.id}/price-history",
        headers=headers_other
    )

    assert response.status_code == 404

    data = response.json()

    assert data["detail"] == "Product not found"

    # Owner can access it
    owner_response = await client.get(
        f"/products/{product.id}/price-history",
        headers=headers_owner
    )

    assert owner_response.status_code == 200


# =========================================================
# TEST: TRACK PRODUCT SUCCESSFULLY
# =========================================================

@pytest.mark.asyncio
async def test_track_product_successfully(
    client,
    db_session,
    monkeypatch
):

    # Create authenticated user
    headers, user_id = await create_user_and_get_token(
        client,
        "Track User",
        "trackuser@example.com"
    )

    # Fake response from Firecrawl
    fake_scraped_data = {
        "productName": "Test Headphones",
        "currentPrice": 2500.00,
        "currencyCode": "INR",
        "productImageUrl": "https://example.com/headphones.jpg"
    }

    # Mock Firecrawl
    monkeypatch.setattr(
        firecrawl_service,
        "scrape_product",
        Mock(return_value=fake_scraped_data)
    )

    response = await client.post(
        "/products/track",
        headers=headers,
        json={
            "url": "https://example.com/test-headphones"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "Product tracked successfully"

    assert data["product"]["productName"] == "Test Headphones"

    assert data["product"]["currentPrice"] == 2500.00

    assert data["product"]["currencyCode"] == "INR"

    assert (
        data["product"]["productImageUrl"]
        == "https://example.com/headphones.jpg"
    )

    # Verify product exists in database
    product_id = data["product"]["id"]

    product = await db_session.get(
        Product,
        product_id
    )

    assert product is not None

    assert product.user_id == user_id

    assert product.product_name == "Test Headphones"

    # Verify initial price history was created
    # We will query this in the next step using the relationship/endpoint
# =========================================================
# TEST: TRACKING PRODUCT CREATES INITIAL PRICE HISTORY
# =========================================================

@pytest.mark.asyncio
async def test_track_product_creates_initial_price_history(
    client,
    db_session,
    monkeypatch
):

    headers, user_id = await create_user_and_get_token(
        client,
        "Price History User",
        "trackhistory@example.com"
    )

    fake_scraped_data = {
        "productName": "Test Keyboard",
        "currentPrice": 3500.00,
        "currencyCode": "INR",
        "productImageUrl": None
    }

    monkeypatch.setattr(
        firecrawl_service,
        "scrape_product",
        Mock(return_value=fake_scraped_data)
    )

    response = await client.post(
        "/products/track",
        headers=headers,
        json={
            "url": "https://example.com/test-keyboard"
        }
    )

    assert response.status_code == 201

    product_id = response.json()["product"]["id"]

    # Check price history endpoint
    history_response = await client.get(
        f"/products/{product_id}/price-history",
        headers=headers
    )

    assert history_response.status_code == 200

    history_data = history_response.json()

    assert len(history_data["priceHistory"]) == 1

    assert (
        history_data["priceHistory"][0]["price"]
        == 3500.00
    )

# =========================================================
# TEST: TRACK PRODUCT WITH INVALID URL
# =========================================================

@pytest.mark.asyncio
async def test_track_product_with_invalid_url(
    client
):

    headers, user_id = await create_user_and_get_token(
        client,
        "Invalid URL User",
        "invalidurl@example.com"
    )

    response = await client.post(
        "/products/track",
        headers=headers,
        json={
            "url": "this-is-not-a-valid-url"
        }
    )

    assert response.status_code == 422
 
 
# =========================================================
# TEST: CHECK SINGLE PRODUCT PRICE - PRICE CHANGED
# =========================================================

@pytest.mark.asyncio
async def test_check_product_price_changed(
    client,
    db_session,
    monkeypatch
):

    # Create authenticated user
    headers, user_id = await create_user_and_get_token(
        client,
        "Price Check User",
        "pricecheck@example.com"
    )

    # Create product
    product = await create_product(
        db_session=db_session,
        user_id=user_id,
        product_name="Test Phone",
        product_url="https://example.com/test-phone",
        current_price=50000.00
    )

    # Fake result from PriceTrackerService
    fake_result = {
        "product_id": product.id,
        "old_price": 50000.00,
        "new_price": 45000.00,
        "price_changed": True
    }

    # Mock the async service method
    monkeypatch.setattr(
        price_tracker_service,
        "check_product_price",
        AsyncMock(return_value=fake_result)
    )

    response = await client.post(
        f"/products/{product.id}/check-price",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product.id
    assert data["old_price"] == 50000.00
    assert data["new_price"] == 45000.00
    assert data["price_changed"] is True


# =========================================================
# TEST: CHECK SINGLE PRODUCT PRICE - NO PRICE CHANGE
# =========================================================

@pytest.mark.asyncio
async def test_check_product_price_not_changed(
    client,
    db_session,
    monkeypatch
):

    headers, user_id = await create_user_and_get_token(
        client,
        "No Change User",
        "nochange@example.com"
    )

    product = await create_product(
        db_session=db_session,
        user_id=user_id,
        product_name="Test Laptop",
        product_url="https://example.com/test-laptop",
        current_price=60000.00
    )

    fake_result = {
        "product_id": product.id,
        "old_price": 60000.00,
        "new_price": 60000.00,
        "price_changed": False
    }

    monkeypatch.setattr(
        price_tracker_service,
        "check_product_price",
        AsyncMock(return_value=fake_result)
    )

    response = await client.post(
        f"/products/{product.id}/check-price",
        headers=headers
    )

    assert response.status_code == 200

    data = response.json()

    assert data["product_id"] == product.id
    assert data["price_changed"] is False
    assert data["old_price"] == 60000.00
    assert data["new_price"] == 60000.00


# =========================================================
# TEST: CHECK PRICE FOR NONEXISTENT PRODUCT
# =========================================================

@pytest.mark.asyncio
async def test_check_price_for_nonexistent_product(
    client
):

    headers, _ = await create_user_and_get_token(
        client,
        "Missing Product User",
        "missingproduct@example.com"
    )

    response = await client.post(
        "/products/99999/check-price",
        headers=headers
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Product not found"

# =========================================================
# TEST: USER CANNOT CHECK ANOTHER USER'S PRODUCT PRICE
# =========================================================

@pytest.mark.asyncio
async def test_user_cannot_check_another_users_product_price(
    client,
    db_session
):

    # Owner
    headers_owner, owner_id = await create_user_and_get_token(
        client,
        "Product Owner",
        "priceowner@example.com"
    )

    # Another user
    headers_other, _ = await create_user_and_get_token(
        client,
        "Other User",
        "priceother@example.com"
    )

    product = await create_product(
        db_session=db_session,
        user_id=owner_id,
        product_name="Private Phone",
        product_url="https://example.com/private-phone",
        current_price=30000.00
    )

    # Other user tries to check it
    response = await client.post(
        f"/products/{product.id}/check-price",
        headers=headers_other
    )

    assert response.status_code == 404

    assert response.json()["detail"] == "Product not found"

# =========================================================
# TEST: CHECK ALL PRICES FOR CURRENT USER
# =========================================================

@pytest.mark.asyncio
async def test_check_all_product_prices(
    client,
    db_session,
    monkeypatch
):

    headers_user_1, user_1_id = await create_user_and_get_token(
        client,
        "Check All User",
        "checkall@example.com"
    )

    headers_user_2, user_2_id = await create_user_and_get_token(
        client,
        "Another User",
        "anothercheckall@example.com"
    )

    # User 1 products
    product_1 = await create_product(
        db_session=db_session,
        user_id=user_1_id,
        product_name="User 1 Product A",
        product_url="https://example.com/user1-product-a",
        current_price=1000.00
    )

    product_2 = await create_product(
        db_session=db_session,
        user_id=user_1_id,
        product_name="User 1 Product B",
        product_url="https://example.com/user1-product-b",
        current_price=2000.00
    )

    # User 2 product - should NOT be checked
    product_3 = await create_product(
        db_session=db_session,
        user_id=user_2_id,
        product_name="User 2 Product",
        product_url="https://example.com/user2-product",
        current_price=3000.00
    )

    # Mock result for each checked product
    async def mock_check_product_price(product, db):

        return {
            "product_id": product.id,
            "old_price": float(product.current_price),
            "new_price": float(product.current_price),
            "price_changed": False
        }

    monkeypatch.setattr(
        price_tracker_service,
        "check_product_price",
        mock_check_product_price
    )

    response = await client.post(
        "/products/check-all-prices",
        headers=headers_user_1
    )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "Price check completed"

    # Only User 1's two products should be checked
    assert data["total_products"] == 2

    assert len(data["results"]) == 2

    checked_product_ids = {
        result["product_id"]
        for result in data["results"]
    }

    assert product_1.id in checked_product_ids
    assert product_2.id in checked_product_ids

    # User 2's product must not be checked
    assert product_3.id not in checked_product_ids

# =========================================================
# TEST: CHECK ALL PRICES REQUIRES AUTHENTICATION
# =========================================================

@pytest.mark.asyncio
async def test_check_all_prices_requires_authentication(
    client
):

    response = await client.post(
        "/products/check-all-prices"
    )

    assert response.status_code == 401
   