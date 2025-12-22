from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseSchema


class OrganizationBase(BaseModel):
    """Base organization schema."""

    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None


class OrganizationCreate(OrganizationBase):
    """Organization creation schema."""

    name: str = Field(..., min_length=2, max_length=255)


class OrganizationUpdate(OrganizationBase):
    """Organization update schema."""

    settings: Optional[Dict[str, Any]] = None
    features: Optional[Dict[str, Any]] = None


class OrganizationResponse(BaseSchema):
    """Organization response schema."""

    id: UUID
    name: str
    slug: str
    description: Optional[str]
    subscription_tier: str
    settings: Dict[str, Any]
    features: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OrganizationStatsResponse(BaseSchema):
    """Organization statistics response."""

    total_users: int
    total_teams: int
    total_incidents: int
    total_alerts: int
    open_incidents: int
    active_alerts: int
