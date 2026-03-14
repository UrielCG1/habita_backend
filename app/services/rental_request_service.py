from sqlalchemy.orm import Session, selectinload
from fastapi import HTTPException
from typing import Optional

from app.models.property import Property
from app.models.rental_request import RentalRequest
from app.models.user import User
from app.schemas.rental_request import RentalRequestCreate, RentalRequestPatch


VALID_REQUEST_STATUSES = {"pending", "accepted", "rejected", "cancelled"}


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _get_property_or_404(db: Session, property_id: int) -> Property:
    property_obj = db.query(Property).filter(Property.id == property_id).first()
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    return property_obj


def _get_rental_request_or_404(db: Session, request_id: int) -> RentalRequest:
    request_obj = (
        db.query(RentalRequest)
        .options(
            selectinload(RentalRequest.property).selectinload(Property.images),
            selectinload(RentalRequest.user),
        )
        .filter(RentalRequest.id == request_id)
        .first()
    )
    if not request_obj:
        raise HTTPException(status_code=404, detail="Rental request not found")

    if request_obj.property and request_obj.property.images:
        request_obj.property.images.sort(
            key=lambda img: (not img.is_cover, img.sort_order, img.id)
        )

    return request_obj


def create_rental_request(db: Session, payload: RentalRequestCreate):
    _get_user_or_404(db, payload.user_id)
    _get_property_or_404(db, payload.property_id)

    existing_pending = (
        db.query(RentalRequest)
        .filter(
            RentalRequest.user_id == payload.user_id,
            RentalRequest.property_id == payload.property_id,
            RentalRequest.status == "pending",
        )
        .first()
    )

    if existing_pending:
        return {
            "id": existing_pending.id,
            "user_id": existing_pending.user_id,
            "property_id": existing_pending.property_id,
            "status": existing_pending.status,
            "message": "A pending rental request already exists for this property",
            "created": False,
        }, False

    new_request = RentalRequest(
        user_id=payload.user_id,
        property_id=payload.property_id,
        message=payload.message,
        move_in_date=payload.move_in_date,
        monthly_budget=payload.monthly_budget,
        status="pending",
    )

    db.add(new_request)
    db.commit()
    db.refresh(new_request)

    return {
        "id": new_request.id,
        "user_id": new_request.user_id,
        "property_id": new_request.property_id,
        "status": new_request.status,
        "message": "Rental request created successfully",
        "created": True,
    }, True


def get_rental_request_by_id(db: Session, request_id: int):
    return _get_rental_request_or_404(db, request_id)


def list_user_rental_requests(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    _get_user_or_404(db, user_id)

    requests = (
        db.query(RentalRequest)
        .options(
            selectinload(RentalRequest.property).selectinload(Property.images),
            selectinload(RentalRequest.user),
        )
        .filter(RentalRequest.user_id == user_id)
        .order_by(RentalRequest.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    for request_obj in requests:
        if request_obj.property and request_obj.property.images:
            request_obj.property.images.sort(
                key=lambda img: (not img.is_cover, img.sort_order, img.id)
            )

    return requests


def list_property_rental_requests(
    db: Session,
    property_id: int,
    skip: int = 0,
    limit: int = 20,
    status: Optional[str] = None,
):
    _get_property_or_404(db, property_id)

    query = (
        db.query(RentalRequest)
        .options(
            selectinload(RentalRequest.property).selectinload(Property.images),
            selectinload(RentalRequest.user),
        )
        .filter(RentalRequest.property_id == property_id)
    )

    if status:
        query = query.filter(RentalRequest.status == status)

    requests = (
        query
        .order_by(RentalRequest.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    for request_obj in requests:
        if request_obj.property and request_obj.property.images:
            request_obj.property.images.sort(
                key=lambda img: (not img.is_cover, img.sort_order, img.id)
            )

    return requests


def patch_rental_request(
    db: Session,
    request_obj: RentalRequest,
    payload: RentalRequestPatch,
) -> RentalRequest:
    update_data = payload.model_dump(exclude_unset=True)

    if "status" in update_data and update_data["status"] is not None:
        new_status = update_data["status"].strip().lower()
        if new_status not in VALID_REQUEST_STATUSES:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid status. Allowed: {', '.join(sorted(VALID_REQUEST_STATUSES))}",
            )
        update_data["status"] = new_status

    for field, value in update_data.items():
        setattr(request_obj, field, value)

    db.commit()
    db.refresh(request_obj)

    refreshed = _get_rental_request_or_404(db, request_obj.id)
    return refreshed