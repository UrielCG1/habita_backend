from sqlalchemy.orm import Session

from app.models.property import Property
from app.schemas.property import PropertyCreate, PropertyUpdate


def create_property(db: Session, payload: PropertyCreate) -> Property:
    new_property = Property(**payload.model_dump())
    db.add(new_property)
    db.commit()
    db.refresh(new_property)
    return new_property


def get_properties(db: Session, skip: int = 0, limit: int = 20):
    return (
        db.query(Property)
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