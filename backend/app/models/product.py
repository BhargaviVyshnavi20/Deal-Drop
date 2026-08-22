from sqlalchemy import String, Numeric, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class Product(Base):

    __tablename__ = "product_details"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    product_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False
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