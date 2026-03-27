from datetime import datetime
from pydantic import BaseModel


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