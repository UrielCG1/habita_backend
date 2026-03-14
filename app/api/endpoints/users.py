from typing import Optional

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.user import UserCreate, UserPatch, UserResponse
from app.services.user_service import create_user, get_user_by_id, get_users, patch_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_user_endpoint(payload: UserCreate, db: Session = Depends(get_db)):
    return create_user(db=db, payload=payload)


@router.get("/", response_model=list[UserResponse])
def list_users_endpoint(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    role: Optional[str] = Query(default=None),
    is_active: Optional[bool] = Query(default=None),
    db: Session = Depends(get_db),
):
    return get_users(
        db=db,
        skip=skip,
        limit=limit,
        role=role,
        is_active=is_active,
    )


@router.get("/{user_id}", response_model=UserResponse)
def detail_user_endpoint(user_id: int, db: Session = Depends(get_db)):
    return get_user_by_id(db=db, user_id=user_id)


@router.patch("/{user_id}", response_model=UserResponse)
def patch_user_endpoint(user_id: int, payload: UserPatch, db: Session = Depends(get_db)):
    user_obj = get_user_by_id(db=db, user_id=user_id)
    return patch_user(db=db, user_obj=user_obj, payload=payload)