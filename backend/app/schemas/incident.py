from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseSchema, PaginatedResponse


class IncidentBase(BaseModel):
    """Base incident schema."""

    title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    priority: Optional[str] = Field(None, max_length=20)
    severity: Optional[str] = Field(None, max_length=20)
    impact: Optional[str] = Field(None, max_length=20)
    urgency: Optional[str] = Field(None, max_length=20)
    category: Optional[str] = Field(None, max_length=100)
    subcategory: Optional[str] = Field(None, max_length=100)


class IncidentCreate(IncidentBase):
    """Incident creation schema."""

    title: str = Field(..., min_length=1, max_length=500)
    assigned_team_id: Optional[UUID] = None
    assigned_user_id: Optional[UUID] = None
    affected_services: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class IncidentUpdate(IncidentBase):
    """Incident update schema."""

    status: Optional[str] = None
    assigned_team_id: Optional[UUID] = None
    assigned_user_id: Optional[UUID] = None
    affected_services: Optional[List[str]] = None
    root_cause: Optional[str] = None
    resolution_notes: Optional[str] = None
    tags: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class IncidentAssignRequest(BaseModel):
    """Incident assignment request."""

    assigned_team_id: Optional[UUID] = None
    assigned_user_id: Optional[UUID] = None
    comment: Optional[str] = None


class IncidentResolveRequest(BaseModel):
    """Incident resolve request."""

    resolution_notes: str = Field(..., min_length=1)
    root_cause: Optional[str] = None


class IncidentCommentCreate(BaseModel):
    """Incident comment creation schema."""

    content: str = Field(..., min_length=1)
    is_internal: bool = False
    attachments: Optional[List[Dict[str, str]]] = None


class IncidentCommentResponse(BaseSchema):
    """Incident comment response."""

    id: UUID
    incident_id: UUID
    user_id: Optional[UUID]
    content: str
    is_internal: bool
    is_ai_generated: bool
    attachments: List[Dict[str, str]]
    created_at: datetime

    # User details
    user_name: Optional[str] = None
    user_email: Optional[str] = None


class IncidentTimelineResponse(BaseSchema):
    """Incident timeline event response."""

    id: UUID
    incident_id: UUID
    user_id: Optional[UUID]
    event_type: str
    description: Optional[str]
    changes: Optional[Dict[str, Any]]
    is_automated: bool
    created_at: datetime

    # User details
    user_name: Optional[str] = None


class IncidentResponse(BaseSchema):
    """Incident response schema."""

    id: UUID
    organization_id: UUID
    incident_number: str
    title: str
    description: Optional[str]
    status: str
    priority: str
    severity: str
    impact: Optional[str]
    urgency: Optional[str]
    category: Optional[str]
    subcategory: Optional[str]
    assigned_team_id: Optional[UUID]
    assigned_user_id: Optional[UUID]
    reported_by_id: Optional[UUID]
    affected_services: List[str]
    business_impact_score: Optional[float]
    ai_classification: Optional[Dict[str, Any]]
    ai_suggested_resolution: Optional[str]
    ai_confidence_score: Optional[float]
    root_cause: Optional[str]
    resolution_notes: Optional[str]
    is_predicted: bool
    tags: List[str]
    metadata: Dict[str, Any]
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    closed_at: Optional[datetime]
    sla_breach_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    # Related names
    assigned_team_name: Optional[str] = None
    assigned_user_name: Optional[str] = None
    reported_by_name: Optional[str] = None


class IncidentDetailResponse(IncidentResponse):
    """Incident detail response with related data."""

    comments: List[IncidentCommentResponse] = []
    timeline: List[IncidentTimelineResponse] = []
    related_alerts_count: int = 0


class IncidentListResponse(PaginatedResponse[IncidentResponse]):
    """Paginated incident list response."""

    pass


class IncidentStatistics(BaseSchema):
    """Incident statistics response."""

    total: int
    open: int
    acknowledged: int
    in_progress: int
    resolved: int
    closed: int
    by_priority: Dict[str, int]
    by_severity: Dict[str, int]
    by_category: Dict[str, int]
    avg_resolution_time_hours: Optional[float]
    mttr_hours: Optional[float]  # Mean Time To Resolve


class IncidentTrend(BaseSchema):
    """Incident trend data point."""

    date: str
    total: int
    created: int
    resolved: int


class IncidentTrendsResponse(BaseSchema):
    """Incident trends response."""

    period: str  # daily, weekly, monthly
    data: List[IncidentTrend]
