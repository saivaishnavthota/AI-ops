"""Audit log model for tracking all system actions."""
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, JSON, Enum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel


class AuditAction(str, enum.Enum):
    """Audit action types."""
    # Auth actions
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGED = "password_changed"
    PASSWORD_RESET = "password_reset"

    # User actions
    USER_CREATED = "user_created"
    USER_UPDATED = "user_updated"
    USER_DELETED = "user_deleted"
    USER_ROLE_CHANGED = "user_role_changed"

    # Organization actions
    ORG_CREATED = "org_created"
    ORG_UPDATED = "org_updated"
    ORG_SETTINGS_CHANGED = "org_settings_changed"

    # Team actions
    TEAM_CREATED = "team_created"
    TEAM_UPDATED = "team_updated"
    TEAM_DELETED = "team_deleted"
    TEAM_MEMBER_ADDED = "team_member_added"
    TEAM_MEMBER_REMOVED = "team_member_removed"

    # Incident actions
    INCIDENT_CREATED = "incident_created"
    INCIDENT_UPDATED = "incident_updated"
    INCIDENT_ASSIGNED = "incident_assigned"
    INCIDENT_ACKNOWLEDGED = "incident_acknowledged"
    INCIDENT_RESOLVED = "incident_resolved"
    INCIDENT_CLOSED = "incident_closed"
    INCIDENT_REOPENED = "incident_reopened"
    INCIDENT_ESCALATED = "incident_escalated"

    # Alert actions
    ALERT_CREATED = "alert_created"
    ALERT_ACKNOWLEDGED = "alert_acknowledged"
    ALERT_RESOLVED = "alert_resolved"
    ALERT_SUPPRESSED = "alert_suppressed"
    ALERT_ESCALATED = "alert_escalated"

    # Playbook actions
    PLAYBOOK_CREATED = "playbook_created"
    PLAYBOOK_UPDATED = "playbook_updated"
    PLAYBOOK_DELETED = "playbook_deleted"
    PLAYBOOK_EXECUTED = "playbook_executed"
    PLAYBOOK_APPROVED = "playbook_approved"
    PLAYBOOK_REJECTED = "playbook_rejected"

    # Integration actions
    INTEGRATION_ENABLED = "integration_enabled"
    INTEGRATION_DISABLED = "integration_disabled"
    INTEGRATION_CONFIGURED = "integration_configured"

    # Resource actions
    RESOURCE_STARTED = "resource_started"
    RESOURCE_STOPPED = "resource_stopped"
    RESOURCE_REBOOTED = "resource_rebooted"
    RESOURCE_DELETED = "resource_deleted"

    # System actions
    SETTINGS_CHANGED = "settings_changed"
    API_KEY_CREATED = "api_key_created"
    API_KEY_REVOKED = "api_key_revoked"


class AuditLog(BaseModel):
    """Audit log model for tracking all actions."""
    __tablename__ = "audit_logs"

    # Foreign keys
    organization_id = Column(String(36), ForeignKey("organizations.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True, index=True)

    # Action details
    action = Column(Enum(AuditAction), nullable=False, index=True)
    resource_type = Column(String(50), nullable=False, index=True)  # user, incident, alert, etc.
    resource_id = Column(String(36), nullable=True, index=True)
    resource_name = Column(String(255), nullable=True)

    # Change details
    description = Column(Text, nullable=True)
    old_values = Column(JSON, nullable=True)  # Previous state
    new_values = Column(JSON, nullable=True)  # New state
    metadata = Column(JSON, nullable=True)  # Additional context

    # Request context
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    request_id = Column(String(36), nullable=True)

    # Result
    status = Column(String(20), default="success")  # success, failed
    error_message = Column(Text, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self):
        return f"<AuditLog {self.id}: {self.action} by {self.user_id}>"

    @classmethod
    def create_log(
        cls,
        organization_id: str,
        action: AuditAction,
        resource_type: str,
        user_id: str = None,
        resource_id: str = None,
        resource_name: str = None,
        description: str = None,
        old_values: dict = None,
        new_values: dict = None,
        metadata: dict = None,
        ip_address: str = None,
        user_agent: str = None,
        request_id: str = None,
        status: str = "success",
        error_message: str = None,
    ):
        """Create a new audit log entry."""
        return cls(
            organization_id=organization_id,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            resource_name=resource_name,
            description=description,
            old_values=old_values,
            new_values=new_values,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent,
            request_id=request_id,
            status=status,
            error_message=error_message,
        )
