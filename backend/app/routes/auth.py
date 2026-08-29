from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)
from app.db.database import get_db
from app.models.user import User
from app.schemas.auth import (
    UserSignup,
    UserLogin,
    Token,
    GoogleAuthRequest
)

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    verify_access_token,
)

from app.services.google_auth_service import GoogleAuthService



router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

security = HTTPBearer()

@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED
)

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
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
            detail="User not found"
        )

    return user


async def signup(
    user_data: UserSignup,
    db: AsyncSession = Depends(get_db)
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
            detail="Email is already registered"
        )

    # Create the user
    user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        auth_provider="local"
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
                "authProvider": user.auth_provider
            }
        }

    except Exception as e:
        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post(
    "/login",
    response_model=Token
)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
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
            user.password_hash
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    # Create JWT token
    access_token = create_access_token(
        subject=str(user.id)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.post(
    "/google",
    response_model=Token
)
async def google_login(
    google_data: GoogleAuthRequest,
    db: AsyncSession = Depends(get_db)
):

    google_auth_service = GoogleAuthService()

    # Verify Google ID token
    try:
        user_info = google_auth_service.verify_google_token(
            google_data.token
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Google authentication token"
        )

    google_id = user_info["google_id"]
    email = user_info["email"]
    name = user_info["name"]
    profile_picture_url = user_info["profile_picture_url"]

    # Check whether this Google account already exists
    result = await db.execute(
        select(User).where(
            User.google_id == google_id
        )
    )

    user = result.scalar_one_or_none()

    if not user:

        # Check if a user already exists with the same email
        result = await db.execute(
            select(User).where(
                User.email == email
            )
        )

        user = result.scalar_one_or_none()

        if user:
            # Link existing account to Google
            user.google_id = google_id
            user.auth_provider = "google"

            if profile_picture_url:
                user.profile_picture_url = profile_picture_url

        else:
            # Create a new Google user
            user = User(
                name=name or email.split("@")[0],
                email=email,
                google_id=google_id,
                auth_provider="google",
                profile_picture_url=profile_picture_url,
                password_hash=None
            )

            db.add(user)

        await db.commit()
        await db.refresh(user)

    # Create DealDrop JWT
    access_token = create_access_token(
        subject=str(user.id)
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router.get("/me")
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "auth_provider": current_user.auth_provider,
        "profile_picture_url": current_user.profile_picture_url,
        "created_at": current_user.created_at,
    }