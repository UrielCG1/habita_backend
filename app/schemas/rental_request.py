from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.property import PropertyCardResponse


class RentalRequestUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    phone: Optional[str] = None
    role: str
    is_active: bool


class RentalRequestCreate(BaseModel):
    user_id: int
    property_id: int
    message: Optional[str] = None
    move_in_date: Optional[date] = None
    monthly_budget: Optional[Decimal] = None


class RentalRequestPatch(BaseModel):
    status: Optional[str] = Field(default=None, max_length=30)
    message: Optional[str] = None
    move_in_date: Optional[date] = None
    monthly_budget: Optional[Decimal] = None
    owner_notes: Optional[str] = None


class RentalRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    property_id: int
    status: str
    message: Optional[str] = None
    move_in_date: Optional[date] = None
    monthly_budget: Optional[Decimal] = None
    owner_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class RentalRequestDetailResponse(RentalRequestResponse):
    property: Optional[PropertyCardResponse] = None
    user: Optional[RentalRequestUserResponse] = None


class RentalRequestCreateActionResponse(BaseModel):
    id: int
    user_id: int
    property_id: int
    status: str
    message: str
    created: bool