from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.schemas.property import PropertyCardResponse


class AdminSimpleUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: str
    phone: Optional[str] = None


class AdminDashboardSummaryResponse(BaseModel):
    total_properties: int
    active_requests: int
    total_users: int
    projected_income: Decimal


class AdminRecentRequestResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    status: str
    message: Optional[str] = None
    created_at: datetime
    user: Optional[AdminSimpleUserResponse] = None
    property: Optional[PropertyCardResponse] = None


class AdminDashboardDataResponse(BaseModel):
    summary: AdminDashboardSummaryResponse
    recent_properties: list[PropertyCardResponse]
    recent_requests: list[AdminRecentRequestResponse]