from datetime import date, datetime
from pathlib import Path
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas


REPORT_TYPE_LABELS = {
    "summary": "Resumen general",
    "properties": "Propiedades",
    "requests": "Solicitudes",
    "reputation": "Reputación",
}

SPANISH_MONTHS = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}


def _safe_filename(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "report"


def build_report_period_label(date_from: date | None, date_to: date | None) -> str:
    if date_from and date_to and date_from.year == date_to.year and date_from.month == date_to.month:
        return f"{SPANISH_MONTHS[date_from.month]} {date_from.year}"

    if date_from and date_to:
        return f"{date_from.strftime('%d-%m-%Y')} a {date_to.strftime('%d-%m-%Y')}"

    if date_from:
        return f"Desde {date_from.strftime('%d-%m-%Y')}"

    if date_to:
        return f"Hasta {date_to.strftime('%d-%m-%Y')}"

    return "Histórico"


def build_report_name(report_type: str, date_from: date | None, date_to: date | None) -> str:
    label = REPORT_TYPE_LABELS.get(report_type, report_type)
    period = build_report_period_label(date_from, date_to)
    return f"{label} - {period}"


def build_report_file_name(report_type: str, date_from: date | None, date_to: date | None) -> str:
    name = build_report_name(report_type, date_from, date_to)
    return f"{_safe_filename(name)}.pdf"


def _draw_wrapped_text(pdf: canvas.Canvas, text: str, x: float, y: float, max_width: float, line_height: float = 14) -> float:
    if not text:
        return y

    words = text.split()
    current_line = ""

    for word in words:
        test_line = f"{current_line} {word}".strip()
        if pdf.stringWidth(test_line, "Helvetica", 10) <= max_width:
            current_line = test_line
        else:
            pdf.drawString(x, y, current_line)
            y -= line_height
            current_line = word

    if current_line:
        pdf.drawString(x, y, current_line)
        y -= line_height

    return y


def _ensure_space(pdf: canvas.Canvas, y: float, needed: float = 70) -> float:
    if y < needed:
        pdf.showPage()
        pdf.setFont("Helvetica", 10)
        return A4[1] - 2.2 * cm
    return y


def generate_owner_report_pdf(
    file_path: Path,
    report_name: str,
    report_type: str,
    owner_name: str,
    generated_at: datetime,
    payload: dict,
    date_from: date | None = None,
    date_to: date | None = None,
) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(file_path), pagesize=A4)
    width, height = A4

    y = height - 2.2 * cm

    pdf.setTitle(report_name)
    pdf.setAuthor("HABITA")
    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(2 * cm, y, report_name)
    y -= 0.8 * cm

    pdf.setFont("Helvetica", 10)
    pdf.drawString(2 * cm, y, f"Owner: {owner_name}")
    y -= 0.5 * cm
    pdf.drawString(2 * cm, y, f"Tipo de reporte: {REPORT_TYPE_LABELS.get(report_type, report_type)}")
    y -= 0.5 * cm
    pdf.drawString(2 * cm, y, f"Generado: {generated_at.strftime('%d/%m/%Y %H:%M')}")
    y -= 0.5 * cm
    pdf.drawString(2 * cm, y, f"Periodo: {build_report_period_label(date_from, date_to)}")
    y -= 1.0 * cm

    pdf.setFont("Helvetica-Bold", 13)
    pdf.drawString(2 * cm, y, "Resumen")
    y -= 0.6 * cm

    summary_cards = payload.get("summary_cards") or {}
    pdf.setFont("Helvetica", 10)
    for label, key in [
        ("Propiedades", "properties_count"),
        ("Solicitudes", "requests_count"),
        ("Reseñas", "reviews_count"),
        ("Calificación promedio", "average_rating"),
    ]:
        y = _ensure_space(pdf, y)
        pdf.drawString(2 * cm, y, f"{label}: {summary_cards.get(key, 0)}")
        y -= 0.45 * cm

    report_types = payload.get("report_types") or []
    if report_types:
        y -= 0.4 * cm
        y = _ensure_space(pdf, y)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(2 * cm, y, "Tipos de reporte disponibles")
        y -= 0.6 * cm
        pdf.setFont("Helvetica", 10)

        for item in report_types:
            y = _ensure_space(pdf, y)
            pdf.drawString(2 * cm, y, f"- {item.get('label', '')}: {item.get('description', '')}")
            y -= 0.45 * cm

    available_properties = payload.get("available_properties") or []
    if available_properties:
        y -= 0.4 * cm
        y = _ensure_space(pdf, y)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(2 * cm, y, "Propiedades disponibles")
        y -= 0.6 * cm
        pdf.setFont("Helvetica", 10)

        for item in available_properties:
            y = _ensure_space(pdf, y)
            pdf.drawString(2 * cm, y, f"- #{item.get('id')} · {item.get('title', '')}")
            y -= 0.45 * cm

    recent_reports = payload.get("recent_reports") or []
    if recent_reports:
        y -= 0.4 * cm
        y = _ensure_space(pdf, y)
        pdf.setFont("Helvetica-Bold", 13)
        pdf.drawString(2 * cm, y, "Reportes recientes")
        y -= 0.6 * cm
        pdf.setFont("Helvetica", 10)

        for item in recent_reports:
            y = _ensure_space(pdf, y)
            pdf.drawString(
                2 * cm,
                y,
                f"- {item.get('name', '')} | {item.get('report_type_label', '')} | {item.get('created_at_display', '')}",
            )
            y -= 0.45 * cm

    pdf.save()