from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.property import PropertyCreate, PropertyResponse, PropertyUpdate
from app.services.property_service import (
    create_property,
    delete_property,
    get_properties,
    get_property_by_id,
    patch_property,
)

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("/", response_model=PropertyResponse, status_code=status.HTTP_201_CREATED)
def create_property_endpoint(payload: PropertyCreate, db: Session = Depends(get_db)):
    return create_property(db, payload)


@router.get("/", response_model=list[PropertyResponse])
def list_properties(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    q: Optional[str] = Query(default=None),
    city: Optional[str] = Query(default=None),
    state: Optional[str] = Query(default=None),
    property_type: Optional[str] = Query(default=None),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    min_price: Optional[Decimal] = Query(default=None, ge=0),
    max_price: Optional[Decimal] = Query(default=None, ge=0),
    bedrooms: Optional[int] = Query(default=None, ge=0),
    bathrooms: Optional[int] = Query(default=None, ge=0),
    is_published: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_properties(
        db=db,
        skip=skip,
        limit=limit,
        q=q,
        city=city,
        state=state,
        property_type=property_type,
        status=status_filter,
        min_price=min_price,
        max_price=max_price,
        bedrooms=bedrooms,
        bathrooms=bathrooms,
        is_published=is_published,
    )


@router.get("/{property_id}", response_model=PropertyResponse)
def detail_property(property_id: int, db: Session = Depends(get_db)):
    property_obj = get_property_by_id(db, property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    return property_obj


@router.patch("/{property_id}", response_model=PropertyResponse)
def patch_property_endpoint(
    property_id: int,
    payload: PropertyUpdate,
    db: Session = Depends(get_db),
):
    property_obj = get_property_by_id(db, property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    return patch_property(db, property_obj, payload)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property_endpoint(property_id: int, db: Session = Depends(get_db)):
    property_obj = get_property_by_id(db, property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    delete_property(db, property_obj)
    return None