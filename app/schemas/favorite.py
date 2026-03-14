from pydantic import BaseModel
from typing import Optional


class FavoriteStatusResponse(BaseModel):
    user_id: int
    property_id: int
    is_favorite: bool


class FavoriteActionResponse(FavoriteStatusResponse):
    message: str
    favorite_id: Optional[int] = None