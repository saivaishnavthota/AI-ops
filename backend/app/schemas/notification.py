"""Notification schemas."""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class NotificationBase(BaseModel):
    """Base notification schema."""
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: str = "info"  # info, warning, error, success, alert, incident, system
    priority: str = "medium"  # low, medium, high, urgent
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None
    expires_at: Optional[datetime] = None


class NotificationCreate(NotificationBase):
    """Schema for creating a notification."""
    user_id: str


class NotificationBulkCreate(BaseModel):
    """Schema for creating notifications for multiple users."""
    user_ids: List[str]
    title: str = Field(..., min_length=1, max_length=255)
    message: str = Field(..., min_length=1)
    type: str = "info"
    priority: str = "medium"
    action_url: Optional[str] = None
    action_label: Optional[str] = None
    related_entity_type: Optional[str] = None
    related_entity_id: Optional[str] = None


class NotificationUpdate(BaseModel):
    """Schema for updating a notification."""
    is_read: Optional[bool] = None


class NotificationResponse(NotificationBase):
    """Notification response schema."""
    id: str
    organization_id: str
    user_id: str
    is_read: bool
    read_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class NotificationListResponse(BaseModel):
    """Paginated notification list response."""
    items: List[NotificationResponse]
    total: int
    page: int
    page_size: int
    unread_count: int


class NotificationMarkReadRequest(BaseModel):
    """Request to mark notifications as read."""
    notification_ids: List[str]


class NotificationStatsResponse(BaseModel):
    """Notification statistics response."""
    total: int
    unread: int
    by_type: dict
    by_priority: dict
