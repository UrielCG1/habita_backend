from pathlib import Path

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.owner_report_export import OwnerReportExport


REPORT_TYPE_LABELS = {
    "summary": "Resumen general",
    "properties": "Propiedades",
    "requests": "Solicitudes",
    "reputation": "Reputación",
}


def _format_datetime(dt) -> str:
    if not dt:
        return ""
    return dt.strftime("%d/%m/%Y %H:%M")


def get_owner_recent_reports(db: Session, owner_id: int, limit: int = 5) -> list[dict]:
    rows = (
        db.query(OwnerReportExport)
        .filter(OwnerReportExport.owner_id == owner_id)
        .order_by(OwnerReportExport.created_at.desc(), OwnerReportExport.id.desc())
        .limit(limit)
        .all()
    )

    return [
        {
            "id": row.id,
            "name": row.name,
            "report_type": row.report_type,
            "report_type_label": REPORT_TYPE_LABELS.get(row.report_type, row.report_type),
            "created_at": row.created_at,
            "created_at_display": _format_datetime(row.created_at),
            "download_url": f"/api/owners/{owner_id}/reports/{row.id}/download",
        }
        for row in rows
    ]


def get_owner_report_export_or_404(db: Session, owner_id: int, report_id: str) -> OwnerReportExport:
    row = (
        db.query(OwnerReportExport)
        .filter(
            OwnerReportExport.id == report_id,
            OwnerReportExport.owner_id == owner_id,
        )
        .first()
    )

    if not row:
        raise HTTPException(status_code=404, detail="Report not found")

    return row


def validate_report_file_or_404(file_path: str) -> Path:
    path = Path(file_path)

    if not path.exists() or not path.is_file():
        raise HTTPException(status_code=404, detail="Report file not found")

    return path