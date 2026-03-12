from datetime import date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Date, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.mixins import TimestampMixin


class RentalRequest(TimestampMixin, Base):
    __tablename__ = "rental_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"), nullable=False, index=True)

    status: Mapped[str] = mapped_column(String(30), nullable=False, default="pending")  # pending, accepted, rejected, cancelled
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    move_in_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    monthly_budget: Mapped[Optional[Decimal]] = mapped_column(Numeric(12, 2), nullable=True)
    owner_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    user = relationship("User", back_populates="rental_requests")
    property = relationship("Property", back_populates="rental_requests")