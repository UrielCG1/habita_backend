from pydantic import BaseModel, ConfigDict, EmailStr, Field
from typing import Optional


class AuthUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    role: str
    is_active: bool


class LoginResponseData(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: AuthUserResponse


class LoginResponse(BaseModel):
    success: bool = True
    data: LoginResponseData


class RegisterRequest(BaseModel):
    full_name: str = Field(..., max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: str = Field(default="tenant", max_length=20)


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class RefreshTokenData(BaseModel):
    access_token: str
    token_type: str


class RefreshTokenResponse(BaseModel):
    success: bool = True
    data: RefreshTokenData