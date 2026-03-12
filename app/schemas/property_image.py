from typing import Optional

from pydantic import BaseModel, ConfigDict


class PropertyImageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    property_id: int
    file_path: str
    file_url: str
    alt_text: Optional[str] = None
    is_cover: bool
    sort_order: int