from datetime import date, datetime
from pathlib import Path
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from textwrap import shorten

from reportlab.lib import colors


PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN_X = 42
TOP_Y = PAGE_HEIGHT - 42

COLOR_PRIMARY = colors.HexColor("#004C6D")
COLOR_ACCENT = colors.HexColor("#F6C324")
COLOR_TEXT = colors.HexColor("#3A3A3A")
COLOR_MUTED = colors.HexColor("#6B7280")
COLOR_BG_SOFT = colors.HexColor("#F2F2F2")
COLOR_BLUE_SOFT = colors.HexColor("#C9E8FF")
COLOR_WHITE = colors.white
COLOR_BORDER = colors.HexColor("#D8DEE4")

REPORTS_LOGO_PATH = Path("storage/branding/habita_logo.png")

def _new_page_if_needed(pdf, y, needed_height):
    if y - needed_height < 60:
        pdf.showPage()
        return TOP_Y
    return y

def _new_page_if_needed(pdf, y, needed_height):
    if y - needed_height < 55:
        _draw_footer(pdf)
        pdf.showPage()
        return TOP_Y
    return y

def _draw_footer(pdf):
    pdf.setStrokeColor(COLOR_BORDER)
    pdf.line(MARGIN_X, 32, PAGE_WIDTH - MARGIN_X, 32)

    pdf.setFillColor(COLOR_MUTED)
    pdf.setFont("Helvetica", 8)
    pdf.drawString(MARGIN_X, 20, "HABITA · Owner Portal")

    page_number = pdf.getPageNumber()
    pdf.drawRightString(PAGE_WIDTH - MARGIN_X, 20, f"Página {page_number}")


def _draw_header(pdf, report_name, owner_name, generated_at, period_label):
    y = TOP_Y

    # Marca
    if REPORTS_LOGO_PATH.exists():
        try:
            logo = ImageReader(str(REPORTS_LOGO_PATH))
            pdf.drawImage(
                logo,
                MARGIN_X,
                y - 2,
                width=80,
                height=30,
                mask="auto",
                preserveAspectRatio=True,
            )
        except Exception:
            pass

    # Badge derecha
    badge_w = 104
    badge_h = 22
    badge_x = PAGE_WIDTH - MARGIN_X - badge_w
    badge_y = y + 2

    pdf.setFillColor(COLOR_ACCENT)
    pdf.roundRect(badge_x, badge_y - badge_h, badge_w, badge_h, 8, fill=1, stroke=0)

    pdf.setFillColor(COLOR_TEXT)
    pdf.setFont("Helvetica-Bold", 8)
    pdf.drawCentredString(badge_x + badge_w / 2, badge_y - 14, "Reporte HABITA")

    # Título
    title_y = y - 44
    pdf.setFillColor(COLOR_TEXT)
    pdf.setFont("Helvetica-Bold", 24)
    pdf.drawString(MARGIN_X, title_y, report_name)

    # Meta en bloque
    meta_y = title_y - 26
    pdf.setFont("Helvetica", 10)
    pdf.setFillColor(COLOR_TEXT)
    pdf.drawString(MARGIN_X, meta_y, f"Owner: {owner_name}")
    pdf.drawString(MARGIN_X, meta_y - 16, f"Generado: {generated_at.strftime('%d/%m/%Y %H:%M')}")
    pdf.drawString(MARGIN_X, meta_y - 32, f"Periodo: {period_label}")

    # Línea divisoria con más aire
    line_y = meta_y - 48
    pdf.setStrokeColor(COLOR_BORDER)
    pdf.setLineWidth(1)
    pdf.line(MARGIN_X, line_y, PAGE_WIDTH - MARGIN_X, line_y)

    return line_y - 26

def _draw_kpi_cards(pdf, y, cards):
    card_width = 112
    card_height = 68
    gap_x = 12
    gap_y = 12
    x = MARGIN_X
    start_x = MARGIN_X
    max_x = PAGE_WIDTH - MARGIN_X

    for index, (label, value) in enumerate(cards):
        bg = COLOR_BG_SOFT if index % 2 == 0 else COLOR_BLUE_SOFT

        if x + card_width > max_x:
            x = start_x
            y -= card_height + gap_y

        pdf.setFillColor(bg)
        pdf.roundRect(x, y - card_height, card_width, card_height, 10, fill=1, stroke=0)

        pdf.setFillColor(COLOR_TEXT)
        pdf.setFont("Helvetica-Bold", 17)
        pdf.drawString(x + 10, y - 25, str(value))

        pdf.setFillColor(COLOR_MUTED)
        pdf.setFont("Helvetica", 8)
        pdf.drawString(x + 10, y - 45, label)

        x += card_width + gap_x

    return y - card_height - 24

def _draw_section_title(pdf, y, title):
    y -= 6
    pdf.setFillColor(COLOR_PRIMARY)
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(MARGIN_X, y, title)

    pdf.setStrokeColor(COLOR_BORDER)
    pdf.setLineWidth(0.8)
    pdf.line(MARGIN_X, y - 10, PAGE_WIDTH - MARGIN_X, y - 10)

    return y - 28

def _draw_table(pdf, y, columns, rows, col_widths):
    table_width = sum(col_widths)
    row_height = 24

    y = _new_page_if_needed(pdf, y, 44)

    # Header tabla
    pdf.setFillColor(COLOR_PRIMARY)
    pdf.roundRect(MARGIN_X, y - row_height, table_width, row_height, 6, fill=1, stroke=0)

    current_x = MARGIN_X
    pdf.setFillColor(COLOR_WHITE)
    pdf.setFont("Helvetica-Bold", 9)

    for idx, col in enumerate(columns):
        pdf.drawString(current_x + 6, y - 15, col)
        current_x += col_widths[idx]

    y -= row_height + 4

    # Filas
    for row_index, row in enumerate(rows):
        y = _new_page_if_needed(pdf, y, row_height + 10)

        fill_color = COLOR_WHITE if row_index % 2 == 0 else COLOR_BG_SOFT
        pdf.setFillColor(fill_color)
        pdf.roundRect(MARGIN_X, y - row_height + 2, table_width, row_height, 4, fill=1, stroke=0)

        current_x = MARGIN_X
        pdf.setFillColor(COLOR_TEXT)
        pdf.setFont("Helvetica", 8.5)

        for idx, value in enumerate(row):
            text = shorten(str(value or ""), width=30, placeholder="...")
            pdf.drawString(current_x + 6, y - 14, text)
            current_x += col_widths[idx]

        y -= row_height + 4

    return y - 16

def _draw_properties_report(pdf, y, payload):
    summary = payload.get("summary_cards", {})
    items = payload.get("items", [])

    y = _draw_kpi_cards(pdf, y, [
        ("Propiedades", summary.get("properties_count", 0)),
        ("Publicadas", summary.get("published_count", 0)),
        ("No publicadas", summary.get("unpublished_count", 0)),
    ])

    y = _draw_section_title(pdf, y, "Listado de propiedades")

    rows = [
        [
            item.get("title"),
            item.get("location"),
            item.get("price"),
            item.get("status_label"),
            "Sí" if item.get("is_published") else "No",
            item.get("requests_count"),
        ]
        for item in items
    ]

    return _draw_table(
        pdf,
        y,
        ["Propiedad", "Ubicación", "Precio", "Estado", "Publicada", "Solicitudes"],
        rows,
        [130, 130, 70, 70, 65, 65],
    )
    
    
def _draw_requests_report(pdf, y, payload):
    summary = payload.get("summary_cards", {})
    items = payload.get("items", [])

    y = _draw_kpi_cards(pdf, y, [
        ("Solicitudes", summary.get("requests_count", 0)),
        ("Pendientes", summary.get("pending_count", 0)),
        ("Aceptadas", summary.get("accepted_count", 0)),
        ("Rechazadas", summary.get("rejected_count", 0)),
    ])

    y = _draw_section_title(pdf, y, "Solicitudes del periodo")

    rows = [
        [
            item.get("property_title"),
            item.get("user_name"),
            item.get("status_label"),
            item.get("created_at_display"),
        ]
        for item in items
    ]

    return _draw_table(
        pdf,
        y,
        ["Propiedad", "Solicitante", "Estado", "Fecha"],
        rows,
        [180, 140, 90, 110],
    )
    
def _draw_rating_breakdown(pdf, y, breakdown):
    y = _draw_section_title(pdf, y, "Distribución de calificaciones")

    for stars in ["5", "4", "3", "2", "1"]:
        count = breakdown.get(stars, 0)

        pdf.setFillColor(COLOR_BG_SOFT)
        pdf.roundRect(MARGIN_X, y - 14, 210, 14, 6, fill=1, stroke=0)

        bar_width = min(210, 28 * count)
        if bar_width > 0:
            pdf.setFillColor(COLOR_ACCENT)
            pdf.roundRect(MARGIN_X, y - 14, bar_width, 14, 6, fill=1, stroke=0)

        pdf.setFillColor(COLOR_TEXT)
        pdf.setFont("Helvetica", 9)
        pdf.drawString(MARGIN_X + 220, y - 11, f"{stars} estrellas")
        pdf.drawRightString(PAGE_WIDTH - MARGIN_X, y - 11, str(count))

        y -= 24

    return y - 14
    
def _draw_reputation_report(pdf, y, payload):
    summary = payload.get("summary_cards", {})
    breakdown = payload.get("rating_breakdown", {})
    top_properties = payload.get("property_review_summary", [])
    latest_reviews = payload.get("latest_reviews", [])

    y = _draw_kpi_cards(pdf, y, [
        ("Favoritos", summary.get("favorites_count", 0)),
        ("Reseñas", summary.get("reviews_count", 0)),
        ("Promedio", summary.get("average_rating", 0)),
    ])

    y = _draw_section_title(pdf, y, "Distribución de calificaciones")

    for stars in ["5", "4", "3", "2", "1"]:
        pdf.setFont("Helvetica", 10)
        pdf.setFillColor(COLOR_TEXT)
        pdf.drawString(MARGIN_X, y, f"{stars} estrellas")
        pdf.drawRightString(PAGE_WIDTH - MARGIN_X, y, str(breakdown.get(stars, 0)))
        y -= 18

    y -= 8
    y = _draw_section_title(pdf, y, "Propiedades mejor valoradas")

    rows = [
        [
            item.get("property_title"),
            item.get("average_rating"),
            item.get("reviews_count"),
            item.get("favorites_count"),
        ]
        for item in top_properties
    ]

    y = _draw_table(
        pdf,
        y,
        ["Propiedad", "Promedio", "Reseñas", "Favoritos"],
        rows,
        [230, 80, 80, 90],
    )

    y = _new_page_if_needed(pdf, y, 120)
    y = _draw_section_title(pdf, y, "Últimas reseñas")

    rows = [
        [
            item.get("reviewer_name"),
            item.get("property_title"),
            item.get("rating"),
            item.get("comment"),
        ]
        for item in latest_reviews
    ]

    return _draw_table(
        pdf,
        y,
        ["Usuario", "Propiedad", "Rating", "Comentario"],
        rows,
        [120, 130, 50, 180],
    )
    
def _draw_summary_report(pdf, y, payload):
    summary = payload.get("summary_cards", {})
    properties = payload.get("available_properties", [])
    recent_reports = payload.get("recent_reports", [])

    y = _draw_kpi_cards(pdf, y, [
        ("Propiedades", summary.get("properties_count", 0)),
        ("Publicadas", summary.get("published_count", 0)),
        ("Solicitudes", summary.get("requests_count", 0)),
        ("Favoritos", summary.get("favorites_count", 0)),
        ("Reseñas", summary.get("reviews_count", 0)),
        ("Promedio", summary.get("average_rating", 0)),
    ])

    y = _draw_section_title(pdf, y, "Propiedades disponibles")

    rows = [
        [item.get("id"), item.get("title"), item.get("location")]
        for item in properties
    ]

    y = _draw_table(
        pdf,
        y,
        ["ID", "Propiedad", "Ubicación"],
        rows,
        [50, 220, 200],
    )

    y = _new_page_if_needed(pdf, y, 120)
    y = _draw_section_title(pdf, y, "Reportes recientes")

    rows = [
        [
            item.get("name"),
            item.get("report_type_label"),
            item.get("created_at_display"),
        ]
        for item in recent_reports
    ]

    return _draw_table(
        pdf,
        y,
        ["Reporte", "Tipo", "Fecha"],
        rows,
        [260, 120, 90],
    )


def generate_owner_report_pdf(
    file_path,
    report_name,
    report_type,
    owner_name,
    generated_at,
    payload,
    date_from=None,
    date_to=None,
):
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)

    pdf = canvas.Canvas(str(file_path), pagesize=A4)
    meta = payload.get("meta", {})
    period_label = meta.get("period_label", "Periodo general")

    y = _draw_header(pdf, report_name, owner_name, generated_at, period_label)

    if report_type == "summary":
        y = _draw_summary_report(pdf, y, payload)
    elif report_type == "properties":
        y = _draw_properties_report(pdf, y, payload)
    elif report_type == "requests":
        y = _draw_requests_report(pdf, y, payload)
    elif report_type == "reputation":
        y = _draw_reputation_report(pdf, y, payload)

    _draw_footer(pdf)
    pdf.save()