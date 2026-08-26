from datetime import datetime, UTC

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

default=lambda: datetime.now(UTC)
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

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    products: Mapped[list["Product"]] = relationship(
        back_populates="user"
    )