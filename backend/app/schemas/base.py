from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, List, Optional
from datetime import datetime
from uuid import UUID

T = TypeVar("T")


class BaseSchema(BaseModel):
    """Base schema with common configuration."""

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        json_encoders={
            datetime: lambda v: v.isoformat(),
            UUID: lambda v: str(v),
        },
    )


class PaginatedResponse(BaseSchema, Generic[T]):
    """Generic paginated response."""

    items: List[T]
    total: int
    page: int
    page_size: int
    pages: int

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1


class MessageResponse(BaseSchema):
    """Simple message response."""

    message: str
    success: bool = True


class ErrorResponse(BaseSchema):
    """Error response."""

    error: str
    message: str
    details: Optional[dict] = None


class HealthResponse(BaseSchema):
    """Health check response."""

    status: str
    version: str
    database: str
    redis: str
