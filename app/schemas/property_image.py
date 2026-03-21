from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PropertyImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int
    file_path: str
    file_url: str
    alt_text: Optional[str] = None
    is_cover: bool
    sort_order: int

    
class PropertyImagePatch(BaseModel):
    alt_text: Optional[str] = Field(default=None, max_length=255)
    is_cover: Optional[bool] = None
    sort_order: Optional[int] = None