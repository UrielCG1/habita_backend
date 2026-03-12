from decimal import Decimal
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate


def create_property(db: Session, payload: PropertyCreate) -> Property:
    new_property = Property(**payload.model_dump())
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


def get_properties(
    db: Session,
    skip: int = 0,
    limit: int = 20,
    q: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    property_type: Optional[str] = None,
    status: Optional[str] = None,
    min_price: Optional[Decimal] = None,
    max_price: Optional[Decimal] = None,
    bedrooms: Optional[int] = None,
    bathrooms: Optional[int] = None,
    is_published: Optional[bool] = None,
):
    query = db.query(Property)

    if q:
        term = f"%{q.strip()}%"
        query = query.filter(
            or_(
                Property.title.like(term),
                Property.description.like(term),
                Property.address_line.like(term),
                Property.neighborhood.like(term),
                Property.city.like(term),
                Property.state.like(term),
            )
        )

    if city:
        query = query.filter(Property.city == city)

    if state:
        query = query.filter(Property.state == state)

    if property_type:
        query = query.filter(Property.property_type == property_type)

    if status:
        query = query.filter(Property.status == status)

    if min_price is not None:
        query = query.filter(Property.price >= min_price)

    if max_price is not None:
        query = query.filter(Property.price <= max_price)

    if bedrooms is not None:
        query = query.filter(Property.bedrooms >= bedrooms)

    if bathrooms is not None:
        query = query.filter(Property.bathrooms >= bathrooms)

    if is_published is not None:
        query = query.filter(Property.is_published == is_published)

    return (
        query
        .order_by(Property.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_property_by_id(db: Session, property_id: int):
    return db.query(Property).filter(Property.id == property_id).first()


def patch_property(db: Session, property_obj: Property, payload: PropertyUpdate) -> Property:
    update_data = payload.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(property_obj, field, value)

    db.commit()
    db.refresh(property_obj)
    return property_obj


def delete_property(db: Session, property_obj: Property) -> None:
    db.delete(property_obj)
    db.commit()