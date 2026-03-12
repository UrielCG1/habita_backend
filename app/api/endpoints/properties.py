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
    db: Session = Depends(get_db),
):
    return get_properties(db, skip=skip, limit=limit)


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