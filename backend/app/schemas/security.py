from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from .base import BaseSchema, PaginatedResponse


class SecurityEventBase(BaseModel):
    """Base security event schema."""

    type: Optional[str] = None
    severity: Optional[str] = None
    source: Optional[str] = None
    description: Optional[str] = None
    affected_asset: Optional[str] = None
    ip_address: Optional[str] = None
    user: Optional[str] = None
    details: Optional[str] = None


class SecurityEventCreate(SecurityEventBase):
    """Security event creation schema."""

    type: str
    severity: str
    source: str
    description: str


class SecurityEventUpdate(BaseModel):
    """Security event update schema."""

    status: Optional[str] = None
    resolution_notes: Optional[str] = None


class SecurityEventResponse(BaseSchema):
    """Security event response schema."""

    id: UUID
    organization_id: UUID
    type: str
    severity: str
    source: str
    description: str
    status: str
    affected_asset: Optional[str]
    ip_address: Optional[str]
    user: Optional[str]
    details: Optional[str]
    resolved_at: Optional[datetime]
    resolved_by_id: Optional[UUID]
    resolution_notes: Optional[str]
    created_at: datetime
    updated_at: datetime


class SecurityEventListResponse(PaginatedResponse[SecurityEventResponse]):
    """Paginated security event list response."""

    pass


class SecurityEventStatsResponse(BaseModel):
    """Security event statistics response."""

    total_events: int
    critical_count: int
    high_count: int
    open_count: int
    by_severity: dict
    by_status: dict
    by_type: dict
