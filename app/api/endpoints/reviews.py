from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.review import (
    ReviewCreate,
    ReviewCreateActionResponse,
    ReviewDetailResponse,
    ReviewPatch,
)
from app.services.review_service import (
    create_review,
    delete_review,
    get_review_by_id,
    list_property_reviews,
    list_user_reviews,
    patch_review,
)

router = APIRouter(tags=["Reviews"])


@router.post(
    "/reviews",
    response_model=ReviewCreateActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_review_endpoint(
    payload: ReviewCreate,
    response: Response,
    db: Session = Depends(get_db),
):
    result, created = create_review(db=db, payload=payload)

    if not created:
        response.status_code = status.HTTP_200_OK

    return result


@router.get(
    "/reviews/{review_id}",
    response_model=ReviewDetailResponse,
)
def detail_review_endpoint(
    review_id: int,
    db: Session = Depends(get_db),
):
    return get_review_by_id(db=db, review_id=review_id)


@router.get(
    "/properties/{property_id}/reviews",
    response_model=list[ReviewDetailResponse],
)
def list_property_reviews_endpoint(
    property_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    only_visible: bool = Query(default=True),
    db: Session = Depends(get_db),
):
    return list_property_reviews(
        db=db,
        property_id=property_id,
        skip=skip,
        limit=limit,
        only_visible=only_visible,
    )


@router.get(
    "/users/{user_id}/reviews",
    response_model=list[ReviewDetailResponse],
)
def list_user_reviews_endpoint(
    user_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return list_user_reviews(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit,
    )


@router.patch(
    "/reviews/{review_id}",
    response_model=ReviewDetailResponse,
)
def patch_review_endpoint(
    review_id: int,
    payload: ReviewPatch,
    db: Session = Depends(get_db),
):
    review_obj = get_review_by_id(db=db, review_id=review_id)
    return patch_review(db=db, review_obj=review_obj, payload=payload)


@router.delete(
    "/reviews/{review_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_review_endpoint(
    review_id: int,
    db: Session = Depends(get_db),
):
    review_obj = get_review_by_id(db=db, review_id=review_id)
    delete_review(db=db, review_obj=review_obj)
    return None