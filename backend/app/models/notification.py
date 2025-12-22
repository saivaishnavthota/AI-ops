"""Notification model for user notifications."""
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, Text, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class NotificationType(str, enum.Enum):
    """Notification type enumeration."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    ALERT = "alert"
    INCIDENT = "incident"
    SYSTEM = "system"


class NotificationPriority(str, enum.Enum):
    """Notification priority enumeration."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class Notification(BaseModel):
    """Notification model."""
    __tablename__ = "notifications"

    # Foreign keys
    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Notification details
    title = Column(String(255), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(50), default=NotificationType.INFO.value, nullable=False)
    priority = Column(String(50), default=NotificationPriority.MEDIUM.value, nullable=False)

    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)

    # Action link (optional)
    action_url = Column(String(500), nullable=True)
    action_label = Column(String(100), nullable=True)

    # Related entity (optional)
    related_entity_type = Column(String(50), nullable=True)  # incident, alert, playbook, etc.
    related_entity_id = Column(String(36), nullable=True)

    # Timestamps
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="notifications")
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification {self.id}: {self.title}>"

    def mark_as_read(self):
        """Mark notification as read."""
        self.is_read = True
        self.read_at = datetime.utcnow()
