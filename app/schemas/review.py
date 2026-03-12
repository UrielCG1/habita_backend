from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.property import PropertyCardResponse


class ReviewUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str


class ReviewCreate(BaseModel):
    user_id: int
    property_id: int
    rating: int = Field(..., ge=1, le=5)
    comment: Optional[str] = None


class ReviewPatch(BaseModel):
    rating: Optional[int] = Field(default=None, ge=1, le=5)
    comment: Optional[str] = None
    is_visible: Optional[bool] = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    property_id: int
    rating: int
    comment: Optional[str] = None
    is_visible: bool
    created_at: datetime
    updated_at: datetime


class ReviewDetailResponse(ReviewResponse):
    user: Optional[ReviewUserResponse] = None
    property: Optional[PropertyCardResponse] = None


class ReviewCreateActionResponse(BaseModel):
    id: int
    user_id: int
    property_id: int
    rating: int
    message: str
    created: bool