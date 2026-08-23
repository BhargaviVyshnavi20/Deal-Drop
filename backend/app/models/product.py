from datetime import datetime

from sqlalchemy import String, Numeric, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Product(Base):

    __tablename__ = "product_details"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )
    
    user_id: Mapped[int] = mapped_column(
    ForeignKey("users.id"),
    nullable=False
    )

    product_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    # Exact product listing URL being tracked
    product_url: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        unique=True
    )

    current_price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    currency_code: Mapped[str] = mapped_column(
        String(3),
        nullable=False
    )

    product_image_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    price_history: Mapped[list["PriceHistory"]] = relationship(
        back_populates="product",
        cascade="all, delete-orphan"
    )
    
    user: Mapped["User"] = relationship(
    back_populates="products"
    )