from datetime import datetime
from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.owner_report_export import OwnerReportExport
from app.models.user import User
from app.schemas.owner_reports import OwnerReportExportRequest
from app.services.owner_report_pdf_service import (
    build_report_file_name,
    build_report_name,
    generate_owner_report_pdf,
)
from app.services.owner_reports_service import get_owner_dashboard_reports_summary


REPORTS_STORAGE_ROOT = Path("storage/reports/owners")


def _format_datetime(dt: datetime) -> str:
    return dt.strftime("%d/%m/%Y %H:%M")


def export_owner_dashboard_report(
    db: Session,
    owner_id: int,
    payload: OwnerReportExportRequest,
) -> dict:
    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    if payload.format != "pdf":
        raise HTTPException(status_code=400, detail="Only pdf format is supported")

    # Por ahora reutilizamos reports-summary como base del PDF.
    # Luego, si quieres, separamos contenido especializado por report_type.
    report_payload = get_owner_dashboard_reports_summary(
        db=db,
        owner_id=owner_id,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )

    report_name = build_report_name(
        report_type=payload.report_type,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )
    file_name = build_report_file_name(
        report_type=payload.report_type,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )

    generated_at = datetime.now()
    owner_dir = REPORTS_STORAGE_ROOT / str(owner_id)
    file_path = owner_dir / file_name

    generate_owner_report_pdf(
        file_path=file_path,
        report_name=report_name,
        report_type=payload.report_type,
        owner_name=getattr(owner, "full_name", f"Owner {owner_id}"),
        generated_at=generated_at,
        payload=report_payload,
        date_from=payload.date_from,
        date_to=payload.date_to,
    )

    export_row = OwnerReportExport(
        owner_id=owner_id,
        name=report_name,
        report_type=payload.report_type,
        file_name=file_name,
        file_path=str(file_path),
        mime_type="application/pdf",
        date_from=payload.date_from,
        date_to=payload.date_to,
    )

    db.add(export_row)
    db.commit()
    db.refresh(export_row)

    return {
        "report_id": export_row.id,
        "report_name": export_row.name,
        "report_type": export_row.report_type,
        "format": payload.format,
        "generated_at": export_row.created_at,
        "generated_at_display": _format_datetime(export_row.created_at),
        "download_url": f"/api/owners/{owner_id}/reports/{export_row.id}/download",
    }