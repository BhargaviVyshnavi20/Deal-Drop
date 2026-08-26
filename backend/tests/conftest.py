import pytest

from httpx import ASGITransport, AsyncClient

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.main import app
from app.db.base import Base
from app.db.database import get_db
from app.core.config import settings

# Import models so SQLAlchemy registers all tables
from app.models.user import User
from app.models.product import Product
from app.models.price_history import PriceHistory


TEST_DATABASE_URL = settings.TEST_DATABASE_URL


@pytest.fixture
async def db_session():
    """
    Create a fresh database engine and session for every test.
    """

    test_engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
    )

    TestingSessionLocal = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    # Create clean tables before each test
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

        await session.rollback()

    # Remove tables after the test
    async with test_engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)

    # Close all connections completely
    await test_engine.dispose()


@pytest.fixture
async def client(db_session):
    """
    Create an async FastAPI test client and override
    the production database dependency.
    """

    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as test_client:

        yield test_client

    app.dependency_overrides.clear()