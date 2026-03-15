from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from sqlalchemy.orm import Session

from app.core.security import decode_token
from app.db.session import get_db
from app.schemas.auth import (
    AuthUserResponse,
    LoginResponse,
    RefreshTokenRequest,
    RefreshTokenResponse,
    RegisterRequest,
)
from app.services.auth_service import (
    get_current_user_by_email,
    login_user,
    refresh_access_token,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/login", response_model=LoginResponse)
def login_endpoint(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    return login_user(db=db, email=form_data.username, password=form_data.password)


@router.post("/register", response_model=LoginResponse, status_code=status.HTTP_201_CREATED)
def register_endpoint(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    return register_user(db=db, payload=payload)


@router.post("/refresh", response_model=RefreshTokenResponse)
def refresh_endpoint(payload: RefreshTokenRequest):
    return refresh_access_token(payload.refresh_token)


@router.get("/me", response_model=AuthUserResponse)
def me_endpoint(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
):
    try:
        payload = decode_token(token)
        email = payload.get("sub")
        token_type = payload.get("type")

        if not email or token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    return get_current_user_by_email(db=db, email=email)