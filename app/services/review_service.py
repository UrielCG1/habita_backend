from typing import Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.models.property import Property
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate, ReviewPatch


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


def _sort_property_images(property_obj: Optional[Property]) -> None:
    if property_obj and property_obj.images:
        property_obj.images.sort(key=lambda img: (not img.is_cover, img.sort_order, img.id))


def _get_review_or_404(db: Session, review_id: int) -> Review:
    review = (
        db.query(Review)
        .options(
            selectinload(Review.user),
            selectinload(Review.property).selectinload(Property.images),
        )
        .filter(Review.id == review_id)
        .first()
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")

    _sort_property_images(review.property)
    return review


def create_review(db: Session, payload: ReviewCreate):
    _get_user_or_404(db, payload.user_id)
    _get_property_or_404(db, payload.property_id)

    existing_review = (
        db.query(Review)
        .filter(
            Review.user_id == payload.user_id,
            Review.property_id == payload.property_id,
        )
        .first()
    )

    if existing_review:
        return {
            "id": existing_review.id,
            "user_id": existing_review.user_id,
            "property_id": existing_review.property_id,
            "rating": existing_review.rating,
            "message": "A review already exists for this property and user",
            "created": False,
        }, False

    new_review = Review(
        user_id=payload.user_id,
        property_id=payload.property_id,
        rating=payload.rating,
        comment=payload.comment,
        is_visible=True,
    )

    db.add(new_review)
    db.commit()
    db.refresh(new_review)

    return {
        "id": new_review.id,
        "user_id": new_review.user_id,
        "property_id": new_review.property_id,
        "rating": new_review.rating,
        "message": "Review created successfully",
        "created": True,
    }, True


def get_review_by_id(db: Session, review_id: int) -> Review:
    return _get_review_or_404(db, review_id)


def list_property_reviews(
    db: Session,
    property_id: int,
    skip: int = 0,
    limit: int = 20,
    only_visible: bool = True,
):
    _get_property_or_404(db, property_id)

    query = (
        db.query(Review)
        .options(
            selectinload(Review.user),
            selectinload(Review.property).selectinload(Property.images),
        )
        .filter(Review.property_id == property_id)
    )

    if only_visible:
        query = query.filter(Review.is_visible == True)

    reviews = (
        query
        .order_by(Review.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    for review in reviews:
        _sort_property_images(review.property)

    return reviews


def list_user_reviews(
    db: Session,
    user_id: int,
    skip: int = 0,
    limit: int = 20,
):
    _get_user_or_404(db, user_id)

    reviews = (
        db.query(Review)
        .options(
            selectinload(Review.user),
            selectinload(Review.property).selectinload(Property.images),
        )
        .filter(Review.user_id == user_id)
        .order_by(Review.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    for review in reviews:
        _sort_property_images(review.property)

    return reviews


def patch_review(db: Session, review_obj: Review, payload: ReviewPatch) -> Review:
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(review_obj, field, value)

    db.commit()
    db.refresh(review_obj)

    return _get_review_or_404(db, review_obj.id)


def delete_review(db: Session, review_obj: Review) -> None:
    db.delete(review_obj)
    db.commit()