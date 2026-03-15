from sqlalchemy import func
from sqlalchemy.orm import Session, selectinload

from app.models.property import Property
from app.models.rental_request import RentalRequest
from app.models.user import User


def get_admin_dashboard_data(db: Session) -> dict:
    total_properties = db.query(Property).count()
    active_requests = (
        db.query(RentalRequest)
        .filter(RentalRequest.status == "pending")
        .count()
    )
    total_users = db.query(User).count()

    projected_income = (
        db.query(func.coalesce(func.sum(Property.price), 0))
        .filter(Property.is_published == True, Property.status == "available")
        .scalar()
    )

    recent_properties = (
        db.query(Property)
        .options(
            selectinload(Property.images),
            selectinload(Property.owner),
        )
        .order_by(Property.id.desc())
        .limit(5)
        .all()
    )

    for property_obj in recent_properties:
        if property_obj.images:
            property_obj.images.sort(key=lambda img: (not img.is_cover, img.sort_order, img.id))

    recent_requests = (
        db.query(RentalRequest)
        .options(
            selectinload(RentalRequest.user),
            selectinload(RentalRequest.property).selectinload(Property.images),
            selectinload(RentalRequest.property).selectinload(Property.owner),
        )
        .order_by(RentalRequest.id.desc())
        .limit(5)
        .all()
    )

    for request_obj in recent_requests:
        if request_obj.property and request_obj.property.images:
            request_obj.property.images.sort(
                key=lambda img: (not img.is_cover, img.sort_order, img.id)
            )

    return {
        "summary": {
            "total_properties": total_properties,
            "active_requests": active_requests,
            "total_users": total_users,
            "projected_income": projected_income or 0,
        },
        "recent_properties": recent_properties,
        "recent_requests": recent_requests,
    }