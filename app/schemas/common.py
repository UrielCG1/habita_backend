from typing import Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class PaginationMeta(BaseModel):
    total: int
    skip: int
    limit: int
    returned: int


class PaginatedData(BaseModel, Generic[T]):
    items: list[T]
    pagination: PaginationMeta


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    data: T


class ErrorDetailResponse(BaseModel):
    type: str
    message: str
    details: object Optional[object] = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: ErrorDetailResponse