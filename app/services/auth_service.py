from fastapi import HTTPException, status
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.schemas.auth import RegisterRequest

PUBLIC_REGISTER_ROLES = {"owner", "tenant"}


def _normalize_public_role(role: str) -> str:
    role_value = role.strip().lower()
    if role_value not in PUBLIC_REGISTER_ROLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role for registration",
        )
    return role_value


def _ensure_email_is_unique(db: Session, email: str) -> None:
    exists = db.query(User).filter(User.email == email).first()
    if exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )

    if not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return user


def _build_auth_payload(user: User) -> dict:
    access_token = create_access_token(subject=user.email)
    refresh_token = create_refresh_token(subject=user.email)

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": user,
        },
    }


def login_user(db: Session, email: str, password: str) -> dict:
    user = authenticate_user(db, email=email, password=password)
    return _build_auth_payload(user)


def register_user(db: Session, payload: RegisterRequest) -> dict:
    _ensure_email_is_unique(db, payload.email)

    new_user = User(
        full_name=payload.full_name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        phone=payload.phone,
        role=_normalize_public_role(payload.role),
        is_active=True,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return _build_auth_payload(new_user)


def refresh_access_token(refresh_token: str) -> dict:
    try:
        payload = decode_token(refresh_token)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    token_type = payload.get("type")
    email = payload.get("sub")

    if token_type != "refresh" or not email:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    access_token = create_access_token(subject=email)

    return {
        "success": True,
        "data": {
            "access_token": access_token,
            "token_type": "bearer",
        },
    }


def get_current_user_by_email(db: Session, email: str) -> User:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive user")

    return user