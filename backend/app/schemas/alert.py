from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseSchema, PaginatedResponse


class AlertBase(BaseModel):
    """Base alert schema."""

    title: Optional[str] = Field(None, max_length=500)
    message: Optional[str] = None
    severity: Optional[str] = Field(None, max_length=20)
    host: Optional[str] = Field(None, max_length=255)
    service: Optional[str] = Field(None, max_length=255)


class AlertCreate(AlertBase):
    """Alert creation schema (for webhook ingestion)."""

    alert_id_external: Optional[str] = None
    source: str = Field(..., max_length=100)
    source_type: Optional[str] = Field(None, max_length=50)
    title: str = Field(..., max_length=500)
    severity: str = Field(default="warning", max_length=20)
    metric_name: Optional[str] = None
    metric_value: Optional[float] = None
    threshold_value: Optional[float] = None
    tags: Optional[Dict[str, Any]] = None
    raw_payload: Optional[Dict[str, Any]] = None


class AlertUpdate(AlertBase):
    """Alert update schema."""

    status: Optional[str] = None
    tags: Optional[Dict[str, Any]] = None


class AlertAcknowledgeRequest(BaseModel):
    """Alert acknowledge request."""

    comment: Optional[str] = None


class AlertSuppressRequest(BaseModel):
    """Alert suppression request."""

    reason: str = Field(..., min_length=1)
    duration_hours: Optional[int] = Field(None, ge=1, le=720)  # Max 30 days


class AlertCreateIncidentRequest(BaseModel):
    """Create incident from alert request."""

    title: Optional[str] = None
    description: Optional[str] = None
    priority: str = Field(default="p3")
    severity: str = Field(default="medium")
    assigned_team_id: Optional[UUID] = None


class AlertResponse(BaseSchema):
    """Alert response schema."""

    id: UUID
    organization_id: UUID
    alert_id_external: Optional[str]
    source: str
    source_type: Optional[str]
    title: Optional[str]
    message: Optional[str]
    severity: str
    status: str
    host: Optional[str]
    service: Optional[str]
    metric_name: Optional[str]
    metric_value: Optional[float]
    threshold_value: Optional[float]
    tags: Dict[str, Any]
    correlation_id: Optional[UUID]
    incident_id: Optional[UUID]
    is_suppressed: bool
    suppression_reason: Optional[str]
    ai_correlation_score: Optional[float]
    fingerprint: Optional[str]
    occurrence_count: int
    first_occurrence_at: Optional[datetime]
    last_occurrence_at: Optional[datetime]
    acknowledged_at: Optional[datetime]
    resolved_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class AlertDetailResponse(AlertResponse):
    """Alert detail response with raw payload."""

    raw_payload: Optional[Dict[str, Any]]
    acknowledged_by_name: Optional[str] = None


class AlertListResponse(PaginatedResponse[AlertResponse]):
    """Paginated alert list response."""

    pass


class AlertCorrelationGroupResponse(BaseSchema):
    """Alert correlation group response."""

    correlation_group_id: UUID
    alert_count: int
    severity: str
    root_cause_alert_id: Optional[UUID]
    alerts: List[AlertResponse]
    created_at: datetime


class AlertSourceBase(BaseModel):
    """Base alert source schema."""

    name: Optional[str] = Field(None, max_length=255)
    source_type: Optional[str] = Field(None, max_length=100)
    config: Optional[Dict[str, Any]] = None


class AlertSourceCreate(AlertSourceBase):
    """Alert source creation schema."""

    name: str = Field(..., min_length=1, max_length=255)
    source_type: str = Field(..., max_length=100)


class AlertSourceUpdate(AlertSourceBase):
    """Alert source update schema."""

    is_active: Optional[bool] = None


class AlertSourceResponse(BaseSchema):
    """Alert source response schema."""

    id: UUID
    organization_id: UUID
    name: str
    source_type: str
    config: Dict[str, Any]
    is_active: bool
    last_received_at: Optional[datetime]
    total_alerts_received: int
    created_at: datetime
    updated_at: datetime

    # Computed webhook URL
    webhook_url: Optional[str] = None


class AlertStatistics(BaseSchema):
    """Alert statistics response."""

    total: int
    firing: int
    acknowledged: int
    resolved: int
    suppressed: int
    by_severity: Dict[str, int]
    by_source: Dict[str, int]
    by_service: Dict[str, int]
