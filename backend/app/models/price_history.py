from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PriceHistory(Base):

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    product_id: Mapped[int] = mapped_column(
        ForeignKey("product_details.id"),
        nullable=False
    )

    price: Mapped[float] = mapped_column(
        Numeric(12, 2),
        nullable=False
    )

    recorded_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )

    product: Mapped["Product"] = relationship(
        back_populates="price_history"
    )