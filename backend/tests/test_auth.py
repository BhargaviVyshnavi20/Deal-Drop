import pytest

from sqlalchemy import select

from app.models.user import User


@pytest.mark.asyncio
async def test_signup_success(client, db_session):
    response = await client.post(
        "/auth/signup",
        json={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 201

    data = response.json()

    assert data["message"] == "User registered successfully"

    assert data["user"]["name"] == "Test User"
    assert data["user"]["email"] == "testuser@example.com"
    assert data["user"]["authProvider"] == "local"

    # Verify that the user actually exists in the database
    result = await db_session.execute(
        select(User).where(
            User.email == "testuser@example.com"
        )
    )

    user = result.scalar_one_or_none()

    assert user is not None
    assert user.name == "Test User"
    assert user.auth_provider == "local"
    assert user.password_hash is not None


@pytest.mark.asyncio
async def test_signup_duplicate_email(client):
    user_data = {
        "name": "Test User",
        "email": "duplicate@example.com",
        "password": "TestPassword123"
    }

    # First signup
    first_response = await client.post(
        "/auth/signup",
        json=user_data
    )

    assert first_response.status_code == 201

    # Second signup with the same email
    second_response = await client.post(
        "/auth/signup",
        json=user_data
    )

    assert second_response.status_code == 409

    data = second_response.json()

    assert data["detail"] == "Email is already registered"


@pytest.mark.asyncio
async def test_login_success(client):
    signup_data = {
        "name": "Login User",
        "email": "login@example.com",
        "password": "TestPassword123"
    }

    # Create user first
    signup_response = await client.post(
        "/auth/signup",
        json=signup_data
    )

    assert signup_response.status_code == 201

    # Login
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "login@example.com",
            "password": "TestPassword123"
        }
    )

    assert login_response.status_code == 200

    data = login_response.json()

    assert "access_token" in data
    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_with_wrong_password(client):
    signup_data = {
        "name": "Wrong Password User",
        "email": "wrongpassword@example.com",
        "password": "CorrectPassword123"
    }

    # Create user
    signup_response = await client.post(
        "/auth/signup",
        json=signup_data
    )

    assert signup_response.status_code == 201

    # Login with incorrect password
    login_response = await client.post(
        "/auth/login",
        json={
            "email": "wrongpassword@example.com",
            "password": "WrongPassword123"
        }
    )

    assert login_response.status_code == 401

    data = login_response.json()

    assert data["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_with_nonexistent_email(client):
    response = await client.post(
        "/auth/login",
        json={
            "email": "doesnotexist@example.com",
            "password": "TestPassword123"
        }
    )

    assert response.status_code == 401

    data = response.json()

    assert data["detail"] == "Invalid email or password"