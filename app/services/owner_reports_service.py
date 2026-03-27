from datetime import date, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy import Float, func
from sqlalchemy.orm import Query, Session

from app.models.property import Property
from app.models.rental_request import RentalRequest
from app.models.review import Review
from app.models.user import User
from app.services.owner_report_exports_service import get_owner_recent_reports


REPORT_TYPES = [
    {
        "code": "summary",
        "label": "Resumen general",
        "description": "Panorama ejecutivo del owner.",
    },
    {
        "code": "properties",
        "label": "Propiedades",
        "description": "Inventario, publicación y estado de propiedades.",
    },
    {
        "code": "requests",
        "label": "Solicitudes",
        "description": "Seguimiento operativo de solicitudes.",
    },
    {
        "code": "reputation",
        "label": "Reputación",
        "description": "Favoritos, reseñas y calificación promedio.",
    },
]


def _apply_date_range(query: Query, model, date_from: date | None, date_to: date | None) -> Query:
    if date_from:
        start_dt = datetime.combine(date_from, time.min)
        query = query.filter(model.created_at >= start_dt)

    if date_to:
        end_dt_exclusive = datetime.combine(date_to + timedelta(days=1), time.min)
        query = query.filter(model.created_at < end_dt_exclusive)

    return query


def get_owner_dashboard_reports_summary(
    db: Session,
    owner_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
) -> dict:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(status_code=400, detail="date_from cannot be greater than date_to")

    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    properties_query = db.query(Property).filter(Property.owner_id == owner_id)
    properties_count = properties_query.count()

    owner_properties = properties_query.order_by(Property.id.desc()).all()

    available_properties = [
        {
            "id": prop.id,
            "title": prop.title,
        }
        for prop in owner_properties
    ]

    requests_query = (
        db.query(RentalRequest)
        .join(Property, Property.id == RentalRequest.property_id)
        .filter(Property.owner_id == owner_id)
    )
    requests_query = _apply_date_range(requests_query, RentalRequest, date_from, date_to)
    requests_count = requests_query.count()

    reviews_query = (
        db.query(Review)
        .join(Property, Property.id == Review.property_id)
        .filter(
            Property.owner_id == owner_id,
            Review.is_visible.is_(True),
        )
    )
    reviews_query = _apply_date_range(reviews_query, Review, date_from, date_to)

    reviews_count = reviews_query.count()

    average_rating_value = (
        reviews_query
        .with_entities(func.avg(Review.rating.cast(Float)))
        .scalar()
    )
    average_rating = round(float(average_rating_value or 0), 1)

    summary_cards = {
        "properties_count": properties_count,
        "requests_count": requests_count,
        "reviews_count": reviews_count,
        "average_rating": average_rating,
    }

    recent_reports = get_owner_recent_reports(db=db, owner_id=owner_id, limit=5)

    return {
        "summary_cards": summary_cards,
        "report_types": REPORT_TYPES,
        "available_properties": available_properties,
        "recent_reports": recent_reports,
    }