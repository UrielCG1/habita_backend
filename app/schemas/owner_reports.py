from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field, model_validator


class OwnerReportsSummaryCards(BaseModel):
    properties_count: int
    requests_count: int
    reviews_count: int
    average_rating: float


class OwnerReportTypeItem(BaseModel):
    code: str
    label: str
    description: str


class OwnerAvailablePropertyItem(BaseModel):
    id: int
    title: str


class OwnerRecentReportItem(BaseModel):
    id: str
    name: str
    report_type: str
    report_type_label: str
    created_at: datetime
    created_at_display: str
    download_url: str


class OwnerDashboardReportsSummaryResponse(BaseModel):
    summary_cards: OwnerReportsSummaryCards
    report_types: list[OwnerReportTypeItem]
    available_properties: list[OwnerAvailablePropertyItem]
    recent_reports: list[OwnerRecentReportItem]



class OwnerReportExportRequest(BaseModel):
    report_type: Literal["summary", "properties", "requests", "reputation"]
    date_from: Optional[date] = None
    date_to: Optional[date] = None
    property_id: Optional[int] = None
    format: Literal["pdf"] = "pdf"

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError("date_from cannot be greater than date_to")
        return self


class OwnerReportExportResponse(BaseModel):
    report_id: str
    report_name: str
    report_type: str
    format: str
    generated_at: datetime
    generated_at_display: str
    download_url: str