import pytest
from sqlalchemy import select

from app.models.user import User
from app.models.product import Product
from app.models.price_history import PriceHistory


@pytest.mark.asyncio
async def test_create_user(db_session):
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    assert user.id is not None
    assert user.name == "Test User"
    assert user.email == "test@example.com"
    assert user.auth_provider == "local"


@pytest.mark.asyncio
async def test_create_product_for_user(db_session):
    user = User(
        name="Test User",
        email="productuser@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    product = Product(
        user_id=user.id,
        product_name="Test Product",
        product_url="https://example.com/test-product",
        current_price=999.99,
        currency_code="INR",
        product_image_url="https://example.com/image.jpg"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    assert product.id is not None
    assert product.user_id == user.id
    assert product.product_name == "Test Product"
    assert float(product.current_price) == 999.99


@pytest.mark.asyncio
async def test_create_price_history_for_product(db_session):
    user = User(
        name="Test User",
        email="historyuser@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()

    product = Product(
        user_id=user.id,
        product_name="Test Product",
        product_url="https://example.com/history-product",
        current_price=500.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    price_history = PriceHistory(
        product_id=product.id,
        price=500.00
    )

    db_session.add(price_history)
    await db_session.commit()
    await db_session.refresh(price_history)

    assert price_history.id is not None
    assert price_history.product_id == product.id
    assert float(price_history.price) == 500.00
    assert price_history.recorded_at is not None


@pytest.mark.asyncio
async def test_product_belongs_to_user(db_session):
    user = User(
        name="Relationship User",
        email="relationship@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    product = Product(
        user_id=user.id,
        product_name="Relationship Product",
        product_url="https://example.com/relationship-product",
        current_price=1000.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()

    result = await db_session.execute(
        select(Product).where(Product.user_id == user.id)
    )

    products = result.scalars().all()

    assert len(products) == 1
    assert products[0].user_id == user.id
    assert products[0].product_name == "Relationship Product"


@pytest.mark.asyncio
async def test_price_history_belongs_to_product(db_session):
    user = User(
        name="Price User",
        email="priceuser@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()

    product = Product(
        user_id=user.id,
        product_name="Price Product",
        product_url="https://example.com/price-product",
        current_price=800.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    history1 = PriceHistory(
        product_id=product.id,
        price=1000.00
    )

    history2 = PriceHistory(
        product_id=product.id,
        price=800.00
    )

    db_session.add_all([history1, history2])
    await db_session.commit()

    result = await db_session.execute(
        select(PriceHistory)
        .where(PriceHistory.product_id == product.id)
        .order_by(PriceHistory.id)
    )

    history = result.scalars().all()

    assert len(history) == 2
    assert float(history[0].price) == 1000.00
    assert float(history[1].price) == 800.00
    


@pytest.mark.asyncio
async def test_deleting_product_deletes_price_history(db_session):
    # Create user
    user = User(
        name="Cascade User",
        email="cascade@example.com",
        password_hash="hashed_password",
        auth_provider="local"
    )

    db_session.add(user)
    await db_session.commit()

    # Create product
    product = Product(
        user_id=user.id,
        product_name="Cascade Product",
        product_url="https://example.com/cascade-product",
        current_price=1000.00,
        currency_code="INR"
    )

    db_session.add(product)
    await db_session.commit()
    await db_session.refresh(product)

    # Create price history
    history = PriceHistory(
        product_id=product.id,
        price=1000.00
    )

    db_session.add(history)
    await db_session.commit()

    product_id = product.id

    # Delete product
    await db_session.delete(product)
    await db_session.commit()

    # Verify associated price history is deleted
    result = await db_session.execute(
        select(PriceHistory).where(
            PriceHistory.product_id == product_id
        )
    )

    remaining_history = result.scalars().all()

    assert len(remaining_history) == 0