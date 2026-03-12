from pydantic import BaseModel


class FavoriteStatusResponse(BaseModel):
    user_id: int
    property_id: int
    is_favorite: bool


class FavoriteActionResponse(FavoriteStatusResponse):
    message: str
    favorite_id: int | None = None