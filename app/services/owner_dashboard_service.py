from fastapi import HTTPException
from sqlalchemy import Float, func
from sqlalchemy.orm import Session

from app.models.favorite import Favorite
from app.models.property import Property
from app.models.review import Review
from app.models.user import User


def _build_initials(full_name: str) -> str:
    parts = [part.strip() for part in (full_name or "").split() if part.strip()]
    if not parts:
        return "?"
    if len(parts) == 1:
        return parts[0][:2].upper()
    return f"{parts[0][0]}{parts[1][0]}".upper()


def _format_datetime(dt) -> str:
    if not dt:
        return ""
    return dt.strftime("%d/%m/%Y • %H:%M")


def get_owner_dashboard_reputation(db: Session, owner_id: int) -> dict:
    owner = db.query(User).filter(User.id == owner_id).first()
    if not owner:
        raise HTTPException(status_code=404, detail="Owner not found")

    owner_property_ids_subq = (
        db.query(Property.id)
        .filter(Property.owner_id == owner_id)
        .subquery()
    )

    favorites_count = (
        db.query(func.count(Favorite.property_id))
        .filter(Favorite.property_id.in_(owner_property_ids_subq))
        .scalar()
        or 0
    )

    review_stats = (
        db.query(
            func.count(Review.id).label("reviews_count"),
            func.avg(Review.rating.cast(Float)).label("average_rating"),
        )
        .filter(Review.property_id.in_(owner_property_ids_subq))
        .one()
    )

    reviews_count = int(review_stats.reviews_count or 0)
    average_rating = round(float(review_stats.average_rating or 0), 1)

    breakdown_rows = (
        db.query(
            Review.rating,
            func.count(Review.id),
        )
        .filter(Review.property_id.in_(owner_property_ids_subq))
        .group_by(Review.rating)
        .all()
    )

    rating_breakdown = {
        "5": 0,
        "4": 0,
        "3": 0,
        "2": 0,
        "1": 0,
    }

    for rating, count in breakdown_rows:
        key = str(int(rating))
        if key in rating_breakdown:
            rating_breakdown[key] = int(count)

    latest_reviews_rows = (
        db.query(
            Review.id,
            Review.property_id,
            Property.title.label("property_title"),
            User.full_name.label("reviewer_name"),
            Review.rating,
            Review.comment,
            Review.created_at,
        )
        .join(Property, Property.id == Review.property_id)
        .join(User, User.id == Review.user_id)
        .filter(Property.owner_id == owner_id)
        .order_by(Review.created_at.desc(), Review.id.desc())
        .limit(5)
        .all()
    )

    latest_reviews = [
        {
            "id": row.id,
            "property_id": row.property_id,
            "property_title": row.property_title,
            "reviewer_name": row.reviewer_name,
            "reviewer_initials": _build_initials(row.reviewer_name),
            "rating": int(row.rating),
            "comment": row.comment,
            "created_at": row.created_at,
            "created_at_display": _format_datetime(row.created_at),
        }
        for row in latest_reviews_rows
    ]

    review_stats_subq = (
        db.query(
            Review.property_id.label("property_id"),
            func.count(Review.id).label("reviews_count"),
            func.avg(Review.rating.cast(Float)).label("average_rating"),
        )
        .group_by(Review.property_id)
        .subquery()
    )

    favorite_stats_subq = (
        db.query(
            Favorite.property_id.label("property_id"),
            func.count(Favorite.property_id).label("favorites_count"),
        )
        .group_by(Favorite.property_id)
        .subquery()
    )

    property_summary_rows = (
        db.query(
            Property.id.label("property_id"),
            Property.title.label("property_title"),
            func.coalesce(review_stats_subq.c.reviews_count, 0).label("reviews_count"),
            func.coalesce(review_stats_subq.c.average_rating, 0).label("average_rating"),
            func.coalesce(favorite_stats_subq.c.favorites_count, 0).label("favorites_count"),
        )
        .outerjoin(review_stats_subq, review_stats_subq.c.property_id == Property.id)
        .outerjoin(favorite_stats_subq, favorite_stats_subq.c.property_id == Property.id)
        .filter(Property.owner_id == owner_id)
        .order_by(
            func.coalesce(review_stats_subq.c.reviews_count, 0).desc(),
            func.coalesce(favorite_stats_subq.c.favorites_count, 0).desc(),
            Property.id.desc(),
        )
        .all()
    )

    property_review_summary = [
        {
            "property_id": row.property_id,
            "property_title": row.property_title,
            "reviews_count": int(row.reviews_count or 0),
            "average_rating": round(float(row.average_rating or 0), 1),
            "favorites_count": int(row.favorites_count or 0),
        }
        for row in property_summary_rows
    ]

    return {
        "favorites_count": int(favorites_count),
        "reviews_count": reviews_count,
        "average_rating": average_rating,
        "rating_breakdown": rating_breakdown,
        "latest_reviews": latest_reviews,
        "property_review_summary": property_review_summary,
    }