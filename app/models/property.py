from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base
from app.models.mixins import TimestampMixin


class Property(TimestampMixin, Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)

    title: Mapped[str] = mapped_column(String(180), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    price: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    property_type: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False, default="available")

    address_line: Mapped[str] = mapped_column(String(255), nullable=False)
    neighborhood: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    city: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(10), nullable=True, index=True)

    bedrooms: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    bathrooms: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    parking_spaces: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    area_m2: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)

    latitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7), nullable=True)
    longitude: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 7), nullable=True)

    is_published: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    owner = relationship("User", back_populates="properties")
    images = relationship("PropertyImage", back_populates="property_obj", cascade="all, delete-orphan")
    favorites = relationship("Favorite", back_populates="property", cascade="all, delete-orphan")
    reviews = relationship("Review", back_populates="property", cascade="all, delete-orphan")
    rental_requests = relationship("RentalRequest", back_populates="property", cascade="all, delete-orphan")

    @property
    def cover_image(self):
        if not self.images:
            return None

        ordered_images = sorted(
            self.images,
            key=lambda img: (not img.is_cover, img.sort_order, img.id),
        )
        return ordered_images[0]