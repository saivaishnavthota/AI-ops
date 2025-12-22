from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID

from .base import BaseSchema, PaginatedResponse


class PlaybookStepBase(BaseModel):
    """Base playbook step schema."""

    type: str  # script, notification, approval, condition, delay
    name: str
    config: Dict[str, Any] = {}


class PlaybookBase(BaseModel):
    """Base playbook schema."""

    name: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    trigger_conditions: Optional[Dict[str, Any]] = None
    requires_approval: Optional[bool] = None
    approval_roles: Optional[List[str]] = None


class PlaybookCreate(PlaybookBase):
    """Playbook creation schema."""

    name: str = Field(..., min_length=1, max_length=255)
    steps: List[Dict[str, Any]] = Field(..., min_length=1)
    tags: Optional[List[str]] = None


class PlaybookUpdate(PlaybookBase):
    """Playbook update schema."""

    steps: Optional[List[Dict[str, Any]]] = None
    is_active: Optional[bool] = None
    tags: Optional[List[str]] = None


class PlaybookExecuteRequest(BaseModel):
    """Playbook manual execution request."""

    incident_id: Optional[UUID] = None
    alert_id: Optional[UUID] = None
    parameters: Optional[Dict[str, Any]] = None


class PlaybookApproveRequest(BaseModel):
    """Playbook execution approval request."""

    comment: Optional[str] = None


class PlaybookResponse(BaseSchema):
    """Playbook response schema."""

    id: UUID
    organization_id: UUID
    name: str
    description: Optional[str]
    trigger_conditions: Dict[str, Any]
    steps: List[Dict[str, Any]]
    requires_approval: bool
    approval_roles: List[str]
    is_active: bool
    execution_count: int
    success_count: int
    failure_count: int
    success_rate: float
    avg_execution_time_seconds: Optional[int]
    tags: List[str]
    created_by_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime


class PlaybookListResponse(PaginatedResponse[PlaybookResponse]):
    """Paginated playbook list response."""

    pass


class PlaybookExecutionStepLog(BaseSchema):
    """Playbook execution step log."""

    step_index: int
    step_name: str
    status: str  # pending, running, completed, failed, skipped
    output: Optional[str]
    error: Optional[str]
    duration_ms: Optional[int]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class PlaybookExecutionResponse(BaseSchema):
    """Playbook execution response."""

    id: UUID
    playbook_id: UUID
    organization_id: UUID
    incident_id: Optional[UUID]
    alert_id: Optional[UUID]
    status: str
    triggered_by: Optional[str]
    triggered_by_user_id: Optional[UUID]
    approval_required: bool
    approved_by_id: Optional[UUID]
    approved_at: Optional[datetime]
    approval_comment: Optional[str]
    execution_log: List[PlaybookExecutionStepLog]
    result: Optional[Dict[str, Any]]
    current_step: int
    error_message: Optional[str]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    duration_seconds: int
    created_at: datetime

    # Related names
    playbook_name: Optional[str] = None
    triggered_by_user_name: Optional[str] = None
    approved_by_name: Optional[str] = None


class PlaybookExecutionListResponse(PaginatedResponse[PlaybookExecutionResponse]):
    """Paginated playbook execution list response."""

    pass
