from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseSchema, PaginatedResponse


class InvestigationBase(BaseModel):
    """Base investigation schema."""

    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    assignee_name: Optional[str] = None


class InvestigationCreate(InvestigationBase):
    """Investigation creation schema."""

    title: str = Field(..., min_length=1, max_length=500)
    description: str
    priority: str
    assignee_name: str


class InvestigationUpdate(BaseModel):
    """Investigation update schema."""

    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    priority: Optional[str] = None
    assignee_name: Optional[str] = None
    progress: Optional[int] = Field(None, ge=0, le=100)
    findings: Optional[List[str]] = None
    timeline: Optional[List[Dict[str, Any]]] = None


class InvestigationResponse(BaseSchema):
    """Investigation response schema."""

    id: UUID
    organization_id: UUID
    title: str
    description: str
    status: str
    priority: str
    assignee_id: Optional[UUID]
    assignee_name: str
    progress: int
    events_linked: int
    findings: List[str]
    timeline: List[Dict[str, Any]]
    created_by_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class InvestigationListResponse(PaginatedResponse[InvestigationResponse]):
    """Paginated investigation list response."""

    pass
