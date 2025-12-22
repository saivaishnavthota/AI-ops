"""WebSocket event types and models."""
from enum import Enum
from typing import Any, Optional
from pydantic import BaseModel
from datetime import datetime


class EventType(str, Enum):
    """WebSocket event types."""
    # Connection events
    CONNECTED = "connected"
    DISCONNECTED = "disconnected"

    # Incident events
    INCIDENT_CREATED = "incident.created"
    INCIDENT_UPDATED = "incident.updated"
    INCIDENT_RESOLVED = "incident.resolved"
    INCIDENT_ASSIGNED = "incident.assigned"

    # Alert events
    ALERT_CREATED = "alert.created"
    ALERT_UPDATED = "alert.updated"
    ALERT_RESOLVED = "alert.resolved"
    ALERT_ESCALATED = "alert.escalated"

    # Playbook events
    PLAYBOOK_STARTED = "playbook.started"
    PLAYBOOK_COMPLETED = "playbook.completed"
    PLAYBOOK_FAILED = "playbook.failed"
    PLAYBOOK_STEP_COMPLETED = "playbook.step_completed"

    # Notification events
    NOTIFICATION_NEW = "notification.new"
    NOTIFICATION_READ = "notification.read"

    # System events
    SYSTEM_STATUS = "system.status"
    SYSTEM_ALERT = "system.alert"

    # AI events
    AI_PREDICTION = "ai.prediction"
    AI_ANALYSIS_COMPLETE = "ai.analysis_complete"
    AI_RECOMMENDATION = "ai.recommendation"

    # Resource events
    RESOURCE_STATUS_CHANGE = "resource.status_change"
    RESOURCE_METRIC_UPDATE = "resource.metric_update"


class WebSocketEvent(BaseModel):
    """WebSocket event model."""
    event_type: EventType
    data: dict[str, Any]
    timestamp: datetime = datetime.utcnow()
    organization_id: Optional[str] = None
    user_id: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class AlertEvent(BaseModel):
    """Alert-specific event data."""
    alert_id: str
    title: str
    severity: str
    source: str
    status: str
    message: Optional[str] = None


class IncidentEvent(BaseModel):
    """Incident-specific event data."""
    incident_id: str
    incident_number: str
    title: str
    status: str
    priority: str
    severity: str
    assigned_to: Optional[str] = None


class PlaybookEvent(BaseModel):
    """Playbook execution event data."""
    execution_id: str
    playbook_id: str
    playbook_name: str
    status: str
    current_step: Optional[int] = None
    total_steps: Optional[int] = None
    error_message: Optional[str] = None


class NotificationEvent(BaseModel):
    """Notification event data."""
    notification_id: str
    title: str
    message: str
    type: str  # info, warning, error, success
    action_url: Optional[str] = None
    read: bool = False
