"""Audit log schemas."""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel


class AuditLogBase(BaseModel):
    """Base audit log schema."""
    action: str
    resource_type: str
    resource_id: Optional[str] = None
    resource_name: Optional[str] = None
    description: Optional[str] = None
    changes: Optional[dict] = None  # {field: {old: x, new: y}}


class AuditLogCreate(AuditLogBase):
    """Schema for creating an audit log."""
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    status: str = "success"
    error_message: Optional[str] = None


class AuditLogResponse(AuditLogBase):
    """Audit log response schema."""
    id: str
    organization_id: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    request_id: Optional[str] = None
    status: str
    error_message: Optional[str] = None
    created_at: datetime

    # Additional computed fields
    user_email: Optional[str] = None
    user_name: Optional[str] = None

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Paginated audit log list response."""
    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int


class AuditLogFilter(BaseModel):
    """Filter parameters for audit logs."""
    action: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    user_id: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class AuditLogStatsResponse(BaseModel):
    """Audit log statistics response."""
    total_actions: int
    actions_today: int
    actions_this_week: int
    by_action: dict
    by_resource_type: dict
    by_user: List[dict]
    recent_activity: List[AuditLogResponse]
