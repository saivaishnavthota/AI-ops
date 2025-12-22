from sqlalchemy import Column, String, Boolean, Text, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel


class Organization(BaseModel):
    """Organization model for multi-tenancy."""

    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    description = Column(Text, nullable=True)

    # Subscription and billing
    subscription_tier = Column(String(50), default="free")  # free, starter, professional, enterprise

    # Settings stored as JSON
    settings = Column(JSON, default=dict)

    # Features and limits
    features = Column(JSON, default=dict)

    # Status
    is_active = Column(Boolean, default=True)

    # Relationships
    users = relationship("User", back_populates="organization", lazy="dynamic")
    teams = relationship("Team", back_populates="organization", lazy="dynamic")
    incidents = relationship("Incident", back_populates="organization", lazy="dynamic")
    alerts = relationship("Alert", back_populates="organization", lazy="dynamic")
    playbooks = relationship("Playbook", back_populates="organization", lazy="dynamic")
    notifications = relationship("Notification", back_populates="organization", lazy="dynamic")
    audit_logs = relationship("AuditLog", back_populates="organization", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Organization {self.name}>"

    @property
    def default_settings(self) -> dict:
        """Default organization settings."""
        return {
            "timezone": "UTC",
            "date_format": "YYYY-MM-DD",
            "time_format": "HH:mm:ss",
            "incident_auto_acknowledge_minutes": 30,
            "alert_retention_days": 90,
            "enable_ai_features": True,
            "enable_auto_remediation": False,
            "notification_preferences": {
                "email": True,
                "slack": False,
                "webhook": False,
            },
        }
