from datetime import datetime, timedelta, timezone
from typing import Optional

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import (
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_ALGORITHM,
    JWT_REFRESH_TOKEN_EXPIRE_DAYS,
    JWT_SECRET_KEY,
)

password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def _create_token(subject: str, token_type: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    payload = {
        "sub": subject,
        "type": token_type,
        "exp": expire,
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    expire_delta = timedelta(
        minutes=expires_minutes or JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )
    return _create_token(subject=subject, token_type="access", expires_delta=expire_delta)


def create_refresh_token(subject: str, expires_days: Optional[int] = None) -> str:
    expire_delta = timedelta(days=expires_days or JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    return _create_token(subject=subject, token_type="refresh", expires_delta=expire_delta)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])


def get_token_subject(token: str) -> Optional[str]:
    try:
        payload = decode_token(token)
        return payload.get("sub")
    except InvalidTokenError:
        return None