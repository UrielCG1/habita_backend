from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.responses import paginated_response, success_response
from app.db.session import get_db
from app.services.user_service import create_user, get_user_by_id, get_users, patch_user
from app.schemas.common import PaginatedData, SuccessResponse
from app.schemas.user import UserCreate, UserPatch, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user_endpoint(payload: UserCreate, db: Session = Depends(get_db)):
    user = create_user(db=db, payload=payload)
    return success_response(user)


@router.get("/", response_model=SuccessResponse[PaginatedData[UserResponse]])
def list_users_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    role: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
):
    total, items = get_users(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
    )
    return paginated_response(items=items, total=total, skip=skip, limit=limit)


@router.get("/{user_id}", response_model=SuccessResponse[UserResponse])
def detail_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    user = get_user_by_id(db=db, user_id=user_id)
    return success_response(user)


@router.patch("/{user_id}", response_model=SuccessResponse[UserResponse])
def patch_user_endpoint(user_id: int, payload: UserPatch, db: Session = Depends(get_db)):
    user_obj = get_user_by_id(db=db, user_id=user_id)
    updated_user = patch_user(db=db, user_obj=user_obj, payload=payload)
    return success_response(updated_user)