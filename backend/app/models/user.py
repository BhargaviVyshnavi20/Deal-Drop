from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
        index=True
    )

    # Used for normal email/password authentication.
    # Google-only users will have this as None.
    password_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # Google's unique user identifier.
    # Normal email/password users will have this as None.
    google_id: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True
    )

    auth_provider: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="local"
    )

    profile_picture_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True
    )

    # =========================================================
    # PASSWORD RESET
    # =========================================================

    # Stores the HASH of the password reset token.
    # The actual token is never stored in the database.
    password_reset_token_hash: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    # Time at which the password reset token expires.
    password_reset_expires_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # =========================================================
    # ACCOUNT CREATION
    # =========================================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="user"
    )