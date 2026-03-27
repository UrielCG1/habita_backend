from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class OwnerLatestReviewItem(BaseModel):
    id: int
    property_id: int
    property_title: str
    reviewer_name: str
    reviewer_initials: str
    rating: int
    comment: Optional[str] = None
    created_at: datetime
    created_at_display: str


class OwnerPropertyReviewSummaryItem(BaseModel):
    property_id: int
    property_title: str
    reviews_count: int
    average_rating: float
    favorites_count: int


class OwnerDashboardReputationResponse(BaseModel):
    favorites_count: int
    reviews_count: int
    average_rating: float
    rating_breakdown: dict[str, int]
    latest_reviews: list[OwnerLatestReviewItem]
    property_review_summary: list[OwnerPropertyReviewSummaryItem]