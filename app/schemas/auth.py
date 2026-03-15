from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional


class AuthUserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    full_name: str
    email: EmailStr
    phone: Optional[str]
    role: str
    is_active: bool


class LoginResponseData(BaseModel):
    access_token: str
    token_type: str
    user: AuthUserResponse


class LoginResponse(BaseModel):
    success: bool = True
    data: LoginResponseData