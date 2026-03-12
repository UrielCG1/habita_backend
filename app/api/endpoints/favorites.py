from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.favorite import FavoriteActionResponse, FavoriteStatusResponse
from app.schemas.property import PropertyCardResponse
from app.services.favorite_service import (
    add_favorite,
    get_favorite_status,
    list_user_favorites,
    remove_favorite,
)

router = APIRouter(tags=["Favorites"])


@router.get(
    "/users/{user_id}/favorites",
    response_model=list[PropertyCardResponse],
)
def list_user_favorites_endpoint(
    user_id: int,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return list_user_favorites(db=db, user_id=user_id, skip=skip, limit=limit)


@router.get(
    "/users/{user_id}/favorites/{property_id}/exists",
    response_model=FavoriteStatusResponse,
)
def favorite_status_endpoint(
    user_id: int,
    property_id: int,
    db: Session = Depends(get_db),
):
    return get_favorite_status(db=db, user_id=user_id, property_id=property_id)


@router.post(
    "/users/{user_id}/favorites/{property_id}",
    response_model=FavoriteActionResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_favorite_endpoint(
    user_id: int,
    property_id: int,
    response: Response,
    db: Session = Depends(get_db),
):
    result, created = add_favorite(db=db, user_id=user_id, property_id=property_id)
    if not created:
        response.status_code = status.HTTP_200_OK
    return result


@router.delete(
    "/users/{user_id}/favorites/{property_id}",
    response_model=FavoriteActionResponse,
)
def remove_favorite_endpoint(
    user_id: int,
    property_id: int,
    db: Session = Depends(get_db),
):
    return remove_favorite(db=db, user_id=user_id, property_id=property_id)