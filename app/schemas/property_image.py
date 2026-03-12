from typing import Optional

from pydantic import BaseModel


class PropertyImageResponse(BaseModel):
    id: int
    property_id: int
    file_path: str
    file_url: str
    alt_text: Optional[str] = None
    is_cover: bool
    sort_order: int