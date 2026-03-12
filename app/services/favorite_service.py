from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.models.favorite import Favorite
from app.models.property import Property
from app.models.user import User


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


def _sort_property_images(property_obj: Property) -> None:
    if property_obj.images:
        property_obj.images.sort(key=lambda img: (not img.is_cover, img.sort_order, img.id))


def add_favorite(db: Session, user_id: int, property_id: int):
    _get_user_or_404(db, user_id)
    _get_property_or_404(db, property_id)

    favorite = (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.property_id == property_id)
        .first()
    )

    if favorite:
        return {
            "user_id": user_id,
            "property_id": property_id,
            "is_favorite": True,
            "favorite_id": favorite.id,
            "message": "Property already in favorites",
        }, False

    favorite = Favorite(user_id=user_id, property_id=property_id)
    db.add(favorite)
    db.commit()
    db.refresh(favorite)

    return {
        "user_id": user_id,
        "property_id": property_id,
        "is_favorite": True,
        "favorite_id": favorite.id,
        "message": "Property added to favorites",
    }, True


def remove_favorite(db: Session, user_id: int, property_id: int):
    _get_user_or_404(db, user_id)
    _get_property_or_404(db, property_id)

    favorite = (
        db.query(Favorite)
        .filter(Favorite.user_id == user_id, Favorite.property_id == property_id)
        .first()
    )

    if not favorite:
        return {
            "user_id": user_id,
            "property_id": property_id,
            "is_favorite": False,
            "favorite_id": None,
            "message": "Property was not in favorites",
        }

    favorite_id = favorite.id
    db.delete(favorite)
    db.commit()

    return {
        "user_id": user_id,
        "property_id": property_id,
        "is_favorite": False,
        "favorite_id": favorite_id,
        "message": "Property removed from favorites",
    }


def get_favorite_status(db: Session, user_id: int, property_id: int):
    _get_user_or_404(db, user_id)
    _get_property_or_404(db, property_id)

    exists = (
        db.query(Favorite.id)
        .filter(Favorite.user_id == user_id, Favorite.property_id == property_id)
        .first()
        is not None
    )

    return {
        "user_id": user_id,
        "property_id": property_id,
        "is_favorite": exists,
    }


def list_user_favorites(db: Session, user_id: int, skip: int = 0, limit: int = 20):
    _get_user_or_404(db, user_id)

    properties = (
        db.query(Property)
        .join(Favorite, Favorite.property_id == Property.id)
        .options(selectinload(Property.images))
        .filter(Favorite.user_id == user_id)
        .order_by(Favorite.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    for property_obj in properties:
        _sort_property_images(property_obj)

    return properties