from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, EmailStr

from app.schemas.property_image import PropertyImageResponse


class PropertyBase(BaseModel):
    title: str = Field(..., max_length=180)
    description: Optional[str] = None
    price: Decimal
    property_type: str
    status: str = "available"

    address_line: str = Field(..., max_length=255)
    neighborhood: Optional[str] = Field(default=None, max_length=120)
    city: str = Field(..., max_length=100)
    state: str = Field(..., max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=10)

    bedrooms: int
    bathrooms: int
    parking_spaces: Optional[int] = None
    area_m2: Optional[Decimal] = None

    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    is_published: bool = True


class PropertyCreate(PropertyBase):
    owner_id: int


class PropertyUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=180)
    description: Optional[str] = None
    price: Optional[Decimal] = None
    property_type: Optional[str] = Field(default=None, max_length=50)
    status: Optional[str] = Field(default=None, max_length=30)

    address_line: Optional[str] = Field(default=None, max_length=255)
    neighborhood: Optional[str] = Field(default=None, max_length=120)
    city: Optional[str] = Field(default=None, max_length=100)
    state: Optional[str] = Field(default=None, max_length=100)
    postal_code: Optional[str] = Field(default=None, max_length=10)

    bedrooms: Optional[int] = None
    bathrooms: Optional[int] = None
    parking_spaces: Optional[int] = None
    area_m2: Optional[Decimal] = None

    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None

    is_published: Optional[bool] = None


class PropertyGeocodePreviewResponse(BaseModel):
    latitude: Decimal
    longitude: Decimal
    display_name: str
    query_used: dict[str, str] | None = None
    
class PropertyCardResponse(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    owner: Optional["PropertyOwnerResponse"] = None
    cover_image: Optional[PropertyImageResponse] = None


class PropertyDetailResponse(PropertyBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    owner_id: int
    owner: Optional["PropertyOwnerResponse"] = None
    images: list[PropertyImageResponse] = []
    
    
### admin 

class PropertyOwnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    full_name: str
    email: EmailStr