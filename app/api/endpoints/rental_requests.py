from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session
from typing import Optional

from app.db.session import get_db
from app.schemas.rental_request import (
    RentalRequestCreate,
    RentalRequestCreateActionResponse,
    RentalRequestDetailResponse,
    RentalRequestPatch,
)
from app.services.rental_request_service import (
    create_rental_request,
    get_rental_request_by_id,
    list_property_rental_requests,
    list_user_rental_requests,
    patch_rental_request,
)

router = APIRouter(tags=["Rental Requests"])


@router.post(
    "/rental-requests",
    response_model=RentalRequestCreateActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_rental_request_endpoint(
    payload: RentalRequestCreate,
    response: Response,
    db: Session = Depends(get_db),
):
    result, created = create_rental_request(db=db, payload=payload)

    if not created:
        response.status_code = status.HTTP_200_OK

    return result


@router.get(
    "/rental-requests/{request_id}",
    response_model=RentalRequestDetailResponse,
)
def detail_rental_request_endpoint(
    request_id: int,
    db: Session = Depends(get_db),
):
    return get_rental_request_by_id(db=db, request_id=request_id)


@router.get(
    "/users/{user_id}/rental-requests",
    response_model=list[RentalRequestDetailResponse],
)
def list_user_rental_requests_endpoint(
    user_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return list_user_rental_requests(db=db, user_id=user_id, skip=skip, limit=limit)


@router.get(
    "/properties/{property_id}/rental-requests",
    response_model=list[RentalRequestDetailResponse],
)
def list_property_rental_requests_endpoint(
    property_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    status_filter: Optional[str] = Query(default=None, alias="status"),
    db: Session = Depends(get_db),
):
    return list_property_rental_requests(
        db=db,
        property_id=property_id,
        skip=skip,
        limit=limit,
        status=status_filter,
    )


@router.patch(
    "/rental-requests/{request_id}",
    response_model=RentalRequestDetailResponse,
)
def patch_rental_request_endpoint(
    request_id: int,
    payload: RentalRequestPatch,
    db: Session = Depends(get_db),
):
    request_obj = get_rental_request_by_id(db=db, request_id=request_id)
    return patch_rental_request(db=db, request_obj=request_obj, payload=payload)