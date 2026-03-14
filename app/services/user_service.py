from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserPatch

VALID_USER_ROLES = {"admin", "owner", "tenant"}


def _normalize_role(role: str) -> str:
    role_value = role.strip().lower()
    if role_value not in VALID_USER_ROLES:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Allowed: {', '.join(sorted(VALID_USER_ROLES))}",
        )
    return role_value


def _get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def _ensure_email_is_unique(db: Session, email: str, current_user_id: int | None = None) -> None:
    query = db.query(User).filter(User.email == email)

    if current_user_id is not None:
        query = query.filter(User.id != current_user_id)

    exists = query.first()
    if exists:
        raise HTTPException(status_code=409, detail="Email already registered")


def create_user(db: Session, payload: UserCreate) -> User:
    _ensure_email_is_unique(db, payload.email)

    new_user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=payload.password_hash,
        phone=payload.phone,
        role=_normalize_role(payload.role),
        is_active=payload.is_active,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def get_users(db: Session, skip: int = 0, limit: int = 20, role: str | None = None, is_active: bool | None = None):
    query = db.query(User)

    if role:
        query = query.filter(User.role == role.strip().lower())

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    return (
        query
        .order_by(User.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_user_by_id(db: Session, user_id: int) -> User:
    return _get_user_or_404(db, user_id)


def patch_user(db: Session, user_obj: User, payload: UserPatch) -> User:
    update_data = payload.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"] is not None:
        _ensure_email_is_unique(db, update_data["email"], current_user_id=user_obj.id)

    if "role" in update_data and update_data["role"] is not None:
        update_data["role"] = _normalize_role(update_data["role"])

    for field, value in update_data.items():
        setattr(user_obj, field, value)

    db.commit()
    db.refresh(user_obj)
    return user_obj