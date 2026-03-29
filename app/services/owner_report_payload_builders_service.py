from datetime import date, datetime, time, timedelta

from fastapi import HTTPException
from sqlalchemy import Float, func
from sqlalchemy.orm import Query, Session

from app.models.favorite import Favorite
from app.models.property import Property
from app.models.rental_request import RentalRequest
from app.models.review import Review
from app.models.user import User
from app.services.owner_report_exports_service import get_owner_recent_reports


REPORT_TYPE_LABELS = {
    "summary": "Resumen general",
    "properties": "Propiedades",
    "requests": "Solicitudes",
    "reputation": "Reputación",
}


def _apply_date_range(query: Query, model, date_from: date | None, date_to: date | None) -> Query:
    if date_from:
        start_dt = datetime.combine(date_from, time.min)
        query = query.filter(model.created_at >= start_dt)

    if date_to:
        end_dt_exclusive = datetime.combine(date_to + timedelta(days=1), time.min)
        query = query.filter(model.created_at < end_dt_exclusive)

    return query


def _format_datetime(dt) -> str:
    if not dt:
        return ""
    return dt.strftime("%d/%m/%Y %H:%M")


def _build_period_label(date_from: date | None, date_to: date | None) -> str:
    if date_from and date_to:
        if date_from.month == date_to.month and date_from.year == date_to.year:
            return date_from.strftime("%B %Y").capitalize()
        return f"{date_from.strftime('%d-%m-%Y')} a {date_to.strftime('%d-%m-%Y')}"
    if date_from:
        return f"Desde {date_from.strftime('%d-%m-%Y')}"
    if date_to:
        return f"Hasta {date_to.strftime('%d-%m-%Y')}"
    return "Periodo general"


def _get_owner_or_404(db: Session, owner_id: int) -> User:
    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")
    return owner


def _get_owner_properties_query(db: Session, owner_id: int):
    return db.query(Property).filter(Property.owner_id == owner_id)


def _base_meta(
    owner: User,
    report_type: str,
    date_from: date | None,
    date_to: date | None,
) -> dict:
    return {
        "owner_id": owner.id,
        "owner_name": getattr(owner, "full_name", f"Owner {owner.id}"),
        "report_type": report_type,
        "report_type_label": REPORT_TYPE_LABELS.get(report_type, report_type),
        "generated_at": datetime.now(),
        "period_label": _build_period_label(date_from, date_to),
        "date_from": date_from,
        "date_to": date_to,
    }


def build_summary_report_payload(
    db: Session,
    owner_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    property_id: int | None = None,
) -> dict:
    owner = _get_owner_or_404(db, owner_id)

    properties_query = _get_owner_properties_query(db, owner_id)
    if property_id:
        properties_query = properties_query.filter(Property.id == property_id)

    properties = properties_query.order_by(Property.id.desc()).all()
    property_ids = [p.id for p in properties]

    requests_query = db.query(RentalRequest).filter(RentalRequest.property_id.in_(property_ids)) if property_ids else db.query(RentalRequest).filter(False)
    requests_query = _apply_date_range(requests_query, RentalRequest, date_from, date_to)
    requests = requests_query.order_by(RentalRequest.created_at.desc()).all()

    reviews_query = db.query(Review).filter(
        Review.property_id.in_(property_ids) if property_ids else False,
        Review.is_visible.is_(True),
    )
    reviews_query = _apply_date_range(reviews_query, Review, date_from, date_to)
    reviews = reviews_query.all()

    favorites_count = (
        db.query(Favorite)
        .filter(Favorite.property_id.in_(property_ids) if property_ids else False)
        .count()
    )

    average_rating_value = (
        db.query(func.avg(Review.rating.cast(Float)))
        .filter(
            Review.property_id.in_(property_ids) if property_ids else False,
            Review.is_visible.is_(True),
        )
    )
    average_rating_value = _apply_date_range(average_rating_value, Review, date_from, date_to).scalar()
    average_rating = round(float(average_rating_value or 0), 1)

    summary_cards = {
        "properties_count": len(properties),
        "published_count": sum(1 for p in properties if getattr(p, "is_published", False)),
        "unpublished_count": sum(1 for p in properties if not getattr(p, "is_published", False)),
        "requests_count": len(requests),
        "favorites_count": favorites_count,
        "reviews_count": len(reviews),
        "average_rating": average_rating,
    }

    available_properties = [
        {
            "id": p.id,
            "title": p.title,
            "location": getattr(p, "city", None) or getattr(p, "address", "") or "",
        }
        for p in properties
    ]

    recent_reports = get_owner_recent_reports(db=db, owner_id=owner_id, limit=5)

    return {
        "meta": _base_meta(owner, "summary", date_from, date_to),
        "summary_cards": summary_cards,
        "available_properties": available_properties,
        "recent_reports": recent_reports,
    }


def build_properties_report_payload(
    db: Session,
    owner_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    property_id: int | None = None,
) -> dict:
    owner = _get_owner_or_404(db, owner_id)

    properties_query = _get_owner_properties_query(db, owner_id)
    if property_id:
        properties_query = properties_query.filter(Property.id == property_id)

    properties = properties_query.order_by(Property.created_at.desc(), Property.id.desc()).all()
    property_ids = [p.id for p in properties]

    request_counts = {}
    if property_ids:
        rows = (
            db.query(RentalRequest.property_id, func.count(RentalRequest.id))
            .filter(RentalRequest.property_id.in_(property_ids))
        )
        rows = _apply_date_range(rows, RentalRequest, date_from, date_to)
        rows = rows.group_by(RentalRequest.property_id).all()
        request_counts = {property_id: count for property_id, count in rows}

    items = []
    for p in properties:
        items.append(
            {
                "id": p.id,
                "title": p.title,
                "location": getattr(p, "city", None) or getattr(p, "address", "") or "",
                "price": getattr(p, "price", None),
                "status_code": getattr(p, "status", None),
                "status_label": getattr(p, "status", None) or "Sin estado",
                "is_published": bool(getattr(p, "is_published", False)),
                "property_type_label": getattr(p, "property_type", None) or "Propiedad",
                "requests_count": request_counts.get(p.id, 0),
                "created_at_display": _format_datetime(getattr(p, "created_at", None)),
            }
        )

    return {
        "meta": _base_meta(owner, "properties", date_from, date_to),
        "summary_cards": {
            "properties_count": len(items),
            "published_count": sum(1 for item in items if item["is_published"]),
            "unpublished_count": sum(1 for item in items if not item["is_published"]),
        },
        "items": items,
    }


def build_requests_report_payload(
    db: Session,
    owner_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    property_id: int | None = None,
) -> dict:
    owner = _get_owner_or_404(db, owner_id)

    requests_query = (
        db.query(RentalRequest, Property, User)
        .join(Property, Property.id == RentalRequest.property_id)
        .join(User, User.id == RentalRequest.user_id)
        .filter(Property.owner_id == owner_id)
    )

    if property_id:
        requests_query = requests_query.filter(Property.id == property_id)

    requests_query = _apply_date_range(requests_query, RentalRequest, date_from, date_to)
    rows = requests_query.order_by(RentalRequest.created_at.desc(), RentalRequest.id.desc()).all()

    items = []
    status_breakdown = {
        "pending": 0,
        "accepted": 0,
        "rejected": 0,
        "resolved": 0,
    }

    for rental_request, property_obj, user_obj in rows:
        status_code = getattr(rental_request, "status", None) or "pending"
        if status_code in status_breakdown:
            status_breakdown[status_code] += 1
        elif status_code not in {"pending", "accepted", "rejected"}:
            status_breakdown["resolved"] += 1

        items.append(
            {
                "id": rental_request.id,
                "property_title": property_obj.title,
                "user_name": getattr(user_obj, "full_name", None) or f"Usuario {user_obj.id}",
                "status_code": status_code,
                "status_label": status_code.capitalize(),
                "created_at_display": _format_datetime(rental_request.created_at),
            }
        )

    return {
        "meta": _base_meta(owner, "requests", date_from, date_to),
        "summary_cards": {
            "requests_count": len(items),
            "pending_count": status_breakdown["pending"],
            "accepted_count": status_breakdown["accepted"],
            "rejected_count": status_breakdown["rejected"],
            "resolved_count": status_breakdown["resolved"],
        },
        "status_breakdown": status_breakdown,
        "items": items,
    }


def build_reputation_report_payload(
    db: Session,
    owner_id: int,
    date_from: date | None = None,
    date_to: date | None = None,
    property_id: int | None = None,
) -> dict:
    owner = _get_owner_or_404(db, owner_id)

    properties_query = _get_owner_properties_query(db, owner_id)
    if property_id:
        properties_query = properties_query.filter(Property.id == property_id)

    properties = properties_query.all()
    property_ids = [p.id for p in properties]

    favorites_count = (
        db.query(Favorite)
        .filter(Favorite.property_id.in_(property_ids) if property_ids else False)
        .count()
    )

    reviews_query = (
        db.query(Review, Property, User)
        .join(Property, Property.id == Review.property_id)
        .join(User, User.id == Review.user_id)
        .filter(
            Property.id.in_(property_ids) if property_ids else False,
            Review.is_visible.is_(True),
        )
    )
    reviews_query = _apply_date_range(reviews_query, Review, date_from, date_to)
    rows = reviews_query.order_by(Review.created_at.desc(), Review.id.desc()).all()

    rating_breakdown = {"5": 0, "4": 0, "3": 0, "2": 0, "1": 0}
    latest_reviews = []
    property_accumulator = {}

    for review_obj, property_obj, user_obj in rows:
        rating_key = str(int(review_obj.rating or 0))
        if rating_key in rating_breakdown:
            rating_breakdown[rating_key] += 1

        latest_reviews.append(
            {
                "reviewer_name": getattr(user_obj, "full_name", None) or f"Usuario {user_obj.id}",
                "property_title": property_obj.title,
                "rating": review_obj.rating,
                "comment": getattr(review_obj, "comment", "") or "",
                "created_at_display": _format_datetime(review_obj.created_at),
            }
        )

        bucket = property_accumulator.setdefault(
            property_obj.id,
            {
                "property_title": property_obj.title,
                "reviews_count": 0,
                "rating_sum": 0,
                "favorites_count": 0,
            },
        )
        bucket["reviews_count"] += 1
        bucket["rating_sum"] += float(review_obj.rating or 0)

    if property_ids:
        favorite_rows = (
            db.query(Favorite.property_id, func.count(Favorite.id))
            .filter(Favorite.property_id.in_(property_ids))
            .group_by(Favorite.property_id)
            .all()
        )
        for prop_id, count in favorite_rows:
            if prop_id in property_accumulator:
                property_accumulator[prop_id]["favorites_count"] = count

    reviews_count = len(rows)
    average_rating = round(
        sum(float(review.rating or 0) for review, _, _ in rows) / reviews_count, 1
    ) if reviews_count else 0

    property_review_summary = []
    for prop_id, data in property_accumulator.items():
        property_review_summary.append(
            {
                "property_id": prop_id,
                "property_title": data["property_title"],
                "reviews_count": data["reviews_count"],
                "average_rating": round(data["rating_sum"] / data["reviews_count"], 1) if data["reviews_count"] else 0,
                "favorites_count": data["favorites_count"],
            }
        )

    property_review_summary.sort(
        key=lambda item: (item["average_rating"], item["reviews_count"], item["favorites_count"]),
        reverse=True,
    )

    return {
        "meta": _base_meta(owner, "reputation", date_from, date_to),
        "summary_cards": {
            "favorites_count": favorites_count,
            "reviews_count": reviews_count,
            "average_rating": average_rating,
        },
        "rating_breakdown": rating_breakdown,
        "latest_reviews": latest_reviews[:8],
        "property_review_summary": property_review_summary[:8],
    }


def build_owner_report_payload(
    db: Session,
    owner_id: int,
    report_type: str,
    date_from: date | None = None,
    date_to: date | None = None,
    property_id: int | None = None,
) -> dict:
    if report_type == "summary":
        return build_summary_report_payload(db, owner_id, date_from, date_to, property_id)
    if report_type == "properties":
        return build_properties_report_payload(db, owner_id, date_from, date_to, property_id)
    if report_type == "requests":
        return build_requests_report_payload(db, owner_id, date_from, date_to, property_id)
    if report_type == "reputation":
        return build_reputation_report_payload(db, owner_id, date_from, date_to, property_id)

    raise HTTPException(status_code=400, detail="Unsupported report type")