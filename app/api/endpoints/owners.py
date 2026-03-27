from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.responses import success_response
from app.db.session import get_db
from app.schemas.common import SuccessResponse
from app.schemas.owner_dashboard import OwnerDashboardReputationResponse
from app.services.owner_dashboard_service import get_owner_dashboard_reputation

from datetime import date

from fastapi import APIRouter, Depends, Query

from app.schemas.owner_reports import OwnerDashboardReportsSummaryResponse
from app.services.owner_reports_service import get_owner_dashboard_reports_summary


router = APIRouter(prefix="/owners", tags=["Owners"])


@router.get(
    "/{owner_id}/dashboard/reputation",
    response_model=SuccessResponse[OwnerDashboardReputationResponse],
)
def owner_dashboard_reputation_endpoint(
    owner_id: int,
    db: Session = Depends(get_db),
):
    data = get_owner_dashboard_reputation(db=db, owner_id=owner_id)
    return success_response(data)





from fastapi.responses import FileResponse
from app.services.owner_report_exports_service import (
    get_owner_report_export_or_404,
    validate_report_file_or_404,
)


router = APIRouter(prefix="/owners", tags=["Owners"])


@router.get(
    "/{owner_id}/dashboard/reports-summary",
    response_model=SuccessResponse[OwnerDashboardReportsSummaryResponse],
)
def owner_dashboard_reports_summary_endpoint(
    owner_id: int,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    db: Session = Depends(get_db),
):
    data = get_owner_dashboard_reports_summary(
        db=db,
        owner_id=owner_id,
        date_from=date_from,
        date_to=date_to,
    )
    return success_response(data)


@router.get("/{owner_id}/reports/{report_id}/download")
def owner_report_download_endpoint(
    owner_id: int,
    report_id: str,
    db: Session = Depends(get_db),
):
    report = get_owner_report_export_or_404(
        db=db,
        owner_id=owner_id,
        report_id=report_id,
    )

    file_path = validate_report_file_or_404(report.file_path)

    return FileResponse(
        path=str(file_path),
        media_type=report.mime_type or "application/octet-stream",
        filename=report.file_name,
    )