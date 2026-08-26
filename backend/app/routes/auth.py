from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.models.user import User
from app.core.security import hash_password

from app.schemas.auth import UserSignup, UserLogin, Token
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED
)
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

    # Step 1: Find the user by email
    result = await db.execute(
        select(User).where(
            User.email == user_data.email
        )
    )

    user = result.scalar_one_or_none()

    # Step 2: Check email and password
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

    # Step 3: Create JWT token
    access_token = create_access_token(
        subject=str(user.id)
    )

    # Step 4: Return token
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }