from unittest.mock import Mock

import pytest

from app.services.google_auth_service import GoogleAuthService


# =========================================================
# TEST: NEW GOOGLE USER
# =========================================================

@pytest.mark.asyncio
async def test_google_login_creates_new_user(
    client,
    monkeypatch
):

    mock_user_info = {
        "google_id": "google-user-123",
        "email": "googleuser@example.com",
        "name": "Google User",
        "profile_picture_url": "https://example.com/profile.jpg"
    }

    monkeypatch.setattr(
        GoogleAuthService,
        "verify_google_token",
        Mock(return_value=mock_user_info)
    )

    response = await client.post(
        "/auth/google",
        json={
            "token": "valid-google-token"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


# =========================================================
# TEST: EXISTING GOOGLE USER
# =========================================================

@pytest.mark.asyncio
async def test_google_login_existing_google_user(
    client,
    monkeypatch
):

    mock_user_info = {
        "google_id": "existing-google-123",
        "email": "existinggoogle@example.com",
        "name": "Existing Google User",
        "profile_picture_url": None
    }

    monkeypatch.setattr(
        GoogleAuthService,
        "verify_google_token",
        Mock(return_value=mock_user_info)
    )

    # First login creates the user
    first_response = await client.post(
        "/auth/google",
        json={
            "token": "valid-google-token"
        }
    )

    assert first_response.status_code == 200

    # Second login should use the existing user
    second_response = await client.post(
        "/auth/google",
        json={
            "token": "valid-google-token"
        }
    )

    assert second_response.status_code == 200

    data = second_response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


# =========================================================
# TEST: LINK EXISTING LOCAL USER
# =========================================================

@pytest.mark.asyncio
async def test_google_login_links_existing_local_user(
    client,
    monkeypatch
):

    email = "localuser@example.com"

    # Create a normal local account first
    signup_response = await client.post(
        "/auth/signup",
        json={
            "name": "Local User",
            "email": email,
            "password": "password123"
        }
    )

    assert signup_response.status_code == 201

    mock_user_info = {
        "google_id": "google-linked-123",
        "email": email,
        "name": "Local User",
        "profile_picture_url": "https://example.com/profile.jpg"
    }

    monkeypatch.setattr(
        GoogleAuthService,
        "verify_google_token",
        Mock(return_value=mock_user_info)
    )

    response = await client.post(
        "/auth/google",
        json={
            "token": "valid-google-token"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


# =========================================================
# TEST: INVALID GOOGLE TOKEN
# =========================================================

@pytest.mark.asyncio
async def test_google_login_invalid_token(
    client,
    monkeypatch
):

    monkeypatch.setattr(
        GoogleAuthService,
        "verify_google_token",
        Mock(
            side_effect=ValueError(
                "Invalid Google authentication token"
            )
        )
    )

    response = await client.post(
        "/auth/google",
        json={
            "token": "invalid-google-token"
        }
    )

    assert response.status_code == 401

    assert response.json()["detail"] == (
        "Invalid Google authentication token"
    )