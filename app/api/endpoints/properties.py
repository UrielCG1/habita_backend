from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.responses import paginated_response, success_response
from app.db.session import get_db
from app.schemas.common import PaginatedData, SuccessResponse
from app.schemas.property import (
    PropertyCardResponse,
    PropertyCreate,
    PropertyDetailResponse,
    PropertyUpdate,
)
from app.services.property_service import (
    create_property,
    delete_property,
    get_properties,
    get_property_by_id,
    patch_property,
)

router = APIRouter(prefix="/properties", tags=["Properties"])


@router.post("/", response_model=SuccessResponse[PropertyCardResponse], status_code=status.HTTP_201_CREATED)
def create_property_endpoint(payload: PropertyCreate, db: Session = Depends(get_db)):
    property_obj = create_property(db, payload)
    return success_response(property_obj)


@router.get("/", response_model=SuccessResponse[PaginatedData[PropertyCardResponse]])
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
    total, items = get_properties(
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
    return paginated_response(items=items, total=total, skip=skip, limit=limit)


@router.get("/{property_id}", response_model=SuccessResponse[PropertyDetailResponse])
def detail_property(property_id: int, db: Session = Depends(get_db)):
    property_obj = get_property_by_id(db, property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")
    return success_response(property_obj)


@router.patch("/{property_id}", response_model=SuccessResponse[PropertyCardResponse])
def patch_property_endpoint(
    property_id: int,
    payload: PropertyUpdate,
    db: Session = Depends(get_db),
):
    property_obj = get_property_by_id(db, property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    updated_property = patch_property(db, property_obj, payload)
    return success_response(updated_property)


@router.delete("/{property_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_property_endpoint(property_id: int, db: Session = Depends(get_db)):
    property_obj = get_property_by_id(db, property_id)
    if not property_obj:
        raise HTTPException(status_code=404, detail="Property not found")

    delete_property(db, property_obj)
    return None