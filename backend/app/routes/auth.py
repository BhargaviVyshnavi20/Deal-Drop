from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserSignup,
    UserLogin,
    Token,
    GoogleAuthRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
    create_password_reset_token,
    hash_password_reset_token,
)

from app.services.google_auth_service import GoogleAuthService
from app.services.email_service import EmailService
from app.core.config import settings


# =========================================================
# ROUTER
# =========================================================

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)

security = HTTPBearer()


# =========================================================
# CURRENT USER
# =========================================================

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    token = credentials.credentials

    user_id = verify_access_token(token)

    result = await db.execute(
        select(User).where(
            User.id == int(user_id)
        )
    )

    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# =========================================================
# SIGNUP
# =========================================================

@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
)
async def signup(
    user_data: UserSignup,
    db: AsyncSession = Depends(get_db),
):
    # Check whether the email is already registered
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email is already registered",
        )

    # Create the user
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(
            user_data.password
        ),
        auth_provider="local",
    )

    try:
        db.add(user)

        await db.commit()
        await db.refresh(user)

        return {
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "authProvider": user.auth_provider,
            },
        }

    except Exception as exc:
        await db.rollback()

        print(
            f"SIGNUP ERROR: {type(exc).__name__}: {exc}",
            flush=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to register user.",
        )


# =========================================================
# LOGIN
# =========================================================

@router.post(
    "/login",
    response_model=Token,
)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    # Find the user by email
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    user = result.scalar_one_or_none()

    # Check email and password
    if (
        not user
        or not user.password_hash
        or not verify_password(
            user_data.password,
            user.password_hash,
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Create JWT token
    access_token = create_access_token(
        subject=str(user.id)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# =========================================================
# FORGOT PASSWORD
# =========================================================

@router.post("/forgot-password")
async def forgot_password(
    user_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request a password reset email.

    Always returns the same response whether or not
    the email exists. This prevents account enumeration.
    """

    # Generic response used for both existing and
    # non-existing email addresses.
    generic_response = {
        "message": (
            "If an account exists with that email, "
            "a password reset link has been sent."
        )
    }

    # Find the user
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    user = result.scalar_one_or_none()

    # Do not reveal whether the email exists.
    if not user:
        return generic_response

    # Google-only accounts do not have a password
    # to reset.
    if not user.password_hash:
        return generic_response

    # Generate a secure random token.
    reset_token = create_password_reset_token()

    # Store only the hash in the database.
    reset_token_hash = hash_password_reset_token(
        reset_token
    )

    # PostgreSQL column is TIMESTAMP WITHOUT TIME ZONE.
    #
    # Therefore we intentionally use a naive UTC datetime
    # instead of datetime.now(timezone.utc).
    reset_token_expires_at = (
        datetime.utcnow()
        + timedelta(minutes=15)
    )

    user.password_reset_token_hash = (
        reset_token_hash
    )

    user.password_reset_expires_at = (
        reset_token_expires_at
    )

    try:
        # Save reset token information.
        await db.commit()

        # Build password reset URL.
        reset_url = (
            f"{settings.FRONTEND_URL}"
            f"/reset-password?token={reset_token}"
        )

        # Send reset email.
        email_service = EmailService()

        email_service.send_password_reset_email(
            recipient_email=user.email,
            reset_url=reset_url,
        )

        return generic_response

    except Exception as exc:
        await db.rollback()

        # Log the actual error for backend debugging.
        # The user receives only a generic error.
        print(
            f"PASSWORD RESET ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to process password reset request.",
        )


# =========================================================
# RESET PASSWORD
# =========================================================

@router.post("/reset-password")
async def reset_password(
    user_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset the user's password using the one-time
    password reset token.
    """

    # Hash the token supplied by the user.
    token_hash = hash_password_reset_token(
        user_data.token
    )

    # Find the user with the matching token hash.
    result = await db.execute(
        select(User).where(
            User.password_reset_token_hash
            == token_hash
        )
    )

    user = result.scalar_one_or_none()

    # Invalid token
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    # Check whether the token has an expiration time.
    if not user.password_reset_expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    # PostgreSQL returns a naive datetime because
    # the column is TIMESTAMP WITHOUT TIME ZONE.
    current_time = datetime.utcnow()

    # Check token expiration.
    if (
        current_time
        > user.password_reset_expires_at
    ):
        # Clear expired token.
        user.password_reset_token_hash = None
        user.password_reset_expires_at = None

        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired password reset token.",
        )

    # Set the new password.
    user.password_hash = hash_password(
    user_data.new_password
    )

    # Make the token one-time-use.
    user.password_reset_token_hash = None
    user.password_reset_expires_at = None

    try:
        await db.commit()

        return {
            "message": "Password reset successfully.",
        }

    except Exception as exc:
        await db.rollback()

        print(
            f"PASSWORD RESET CONFIRMATION ERROR: "
            f"{type(exc).__name__}: {exc}",
            flush=True,
        )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to reset password.",
        )


# =========================================================
# GOOGLE LOGIN
# =========================================================

@router.post(
    "/google",
    response_model=Token,
)
async def google_login(
    google_data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db),
):
    google_auth_service = GoogleAuthService()

    # Verify Google ID token
    try:
        user_info = (
            google_auth_service.verify_google_token(
                google_data.token
            )
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google authentication token",
        )

    google_id = user_info["google_id"]
    email = user_info["email"]
    name = user_info["name"]
    profile_picture_url = (
        user_info["profile_picture_url"]
    )

    # Check whether this Google account already exists
    result = await db.execute(
        select(User).where(
            User.google_id == google_id
        )
    )

    user = result.scalar_one_or_none()

    if not user:

        # Check if a user already exists
        # with the same email.
        result = await db.execute(
            select(User).where(
                User.email == email
            )
        )

        user = result.scalar_one_or_none()

        if user:
            # Link existing account to Google.
            user.google_id = google_id
            user.auth_provider = "google"

            if profile_picture_url:
                user.profile_picture_url = (
                    profile_picture_url
                )

        else:
            # Create a new Google user.
            user = User(
                name=name or email.split("@")[0],
                email=email,
                google_id=google_id,
                auth_provider="google",
                profile_picture_url=(
                    profile_picture_url
                ),
                password_hash=None,
            )

            db.add(user)

        await db.commit()
        await db.refresh(user)

    # Create DealDrop JWT.
    access_token = create_access_token(
        subject=str(user.id)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


# =========================================================
# CURRENT USER
# =========================================================

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user),
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "auth_provider": current_user.auth_provider,
        "profile_picture_url": (
            current_user.profile_picture_url
        ),
        "created_at": current_user.created_at,
    }