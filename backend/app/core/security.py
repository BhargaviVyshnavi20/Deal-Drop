from datetime import datetime, timedelta, timezone
import hashlib
import secrets

from jwt.exceptions import InvalidTokenError

from fastapi import HTTPException, status
import jwt
from pwdlib import PasswordHash

from app.core.config import settings


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    """
    Hash a plain-text password before storing it.
    """
    return password_hash.hash(password)


def verify_password(
    plain_password: str,
    hashed_password: str
) -> bool:
    """
    Verify a plain-text password against its hash.
    """
    return password_hash.verify(
        plain_password,
        hashed_password
    )


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None
) -> str:
    """
    Create a JWT access token.
    """

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=30)

    payload = {
        "sub": subject,
        "exp": expire
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )

    return encoded_jwt


def verify_access_token(token: str) -> str:
    """
    Verify a JWT access token and return the user ID.
    """

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        return user_id

    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )


# =========================================================
# PASSWORD RESET TOKEN
# =========================================================

def create_password_reset_token() -> str:
    """
    Generate a cryptographically secure password reset token.

    The raw token is returned to the caller so it can be
    included in the reset email. Only its hash should be
    stored in the database.
    """
    return secrets.token_urlsafe(32)


def hash_password_reset_token(token: str) -> str:
    """
    Hash a password reset token before storing it.

    The raw reset token is never stored in the database.
    """
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()