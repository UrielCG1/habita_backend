from decimal import Decimal
from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate
from app.services.geocoding_service import geocode_location_preview

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
    owner_id: Optional[int] = None,
):
    query = db.query(Property).options(
        selectinload(Property.images),
        selectinload(Property.owner),
    )

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
    
    if owner_id is not None:
        query = query.filter(Property.owner_id == owner_id)

    total = query.count()

    items = (
        query
        .order_by(Property.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )

    for property_obj in items:
        property_obj.images.sort(key=lambda img: (not img.is_cover, img.sort_order, img.id))

    return total, items


def get_property_by_id(db: Session, property_id: int):
    property_obj = (
        db.query(Property)
        .options(
            selectinload(Property.images),
            selectinload(Property.owner)
        )
        .filter(Property.id == property_id)
        .first()
    )

    if property_obj:
        property_obj.images.sort(key=lambda img: (not img.is_cover, img.sort_order, img.id))

    return property_obj


def delete_property(db: Session, property_obj: Property) -> None:
    db.delete(property_obj)
    db.commit()
    
    
def _apply_geocoding_to_data(data: dict) -> dict:
    geocoded = geocode_location_preview(
        address_line=data.get("address_line"),
        neighborhood=data.get("neighborhood"),
        city=data.get("city"),
        state=data.get("state"),
        postal_code=data.get("postal_code"),
    )

    if geocoded:
        data["latitude"] = geocoded["latitude"]
        data["longitude"] = geocoded["longitude"]

    return data


def create_property(db: Session, payload: PropertyCreate) -> Property:
    data = payload.model_dump()
    data = _apply_geocoding_to_data(data)

    new_property = Property(**data)
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


def patch_property(db: Session, property_obj: Property, payload: PropertyUpdate) -> Property:
    update_data = payload.model_dump(exclude_unset=True)

    location_fields = {"address_line", "neighborhood", "city", "state", "postal_code"}
    should_regeocode = any(field in update_data for field in location_fields)

    if should_regeocode:
        merged = {
            "address_line": update_data.get("address_line", property_obj.address_line),
            "neighborhood": update_data.get("neighborhood", property_obj.neighborhood),
            "city": update_data.get("city", property_obj.city),
            "state": update_data.get("state", property_obj.state),
            "postal_code": update_data.get("postal_code", property_obj.postal_code),
        }

        geocoded = geocode_location_preview(**merged)
        if geocoded:
            update_data["latitude"] = geocoded["latitude"]
            update_data["longitude"] = geocoded["longitude"]

    for field, value in update_data.items():
        setattr(property_obj, field, value)

    db.commit()
    db.refresh(property_obj)
    return property_obj