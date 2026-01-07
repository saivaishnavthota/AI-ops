from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class UserRole(str, enum.Enum):
    """User roles for RBAC."""
    SUPER_ADMIN = "super_admin"
    ADMIN = "admin"
    OPERATOR = "operator"
    VIEWER = "viewer"


class User(BaseModel):
    """User model."""

    __tablename__ = "users"

    # Organization reference
    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Basic info
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=True)  # Nullable for SSO users
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)

    # Role and permissions
    role = Column(String(50), default=UserRole.VIEWER.value)
    permissions = Column(JSON, default=list)  # Additional granular permissions

    # Profile
    avatar_url = Column(String(500), nullable=True)
    phone = Column(String(50), nullable=True)
    job_title = Column(String(100), nullable=True)

    # Preferences
    preferences = Column(JSON, default=dict)

    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # SSO
    sso_provider = Column(String(50), nullable=True)
    sso_id = Column(String(255), nullable=True)

    # MFA
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String(255), nullable=True)

    # Tracking
    last_login = Column(DateTime(timezone=True), nullable=True)
    password_changed_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="users")
    team_memberships = relationship("TeamMember", back_populates="user", lazy="dynamic")
    assigned_incidents = relationship(
        "Incident",
        back_populates="assigned_user",
        foreign_keys="Incident.assigned_user_id",
        lazy="dynamic",
    )
    reported_incidents = relationship(
        "Incident",
        back_populates="reported_by",
        foreign_keys="Incident.reported_by_id",
        lazy="dynamic",
    )
    notifications = relationship("Notification", back_populates="user", lazy="dynamic")
    audit_logs = relationship("AuditLog", back_populates="user", lazy="dynamic")

    def __repr__(self) -> str:
        try:
            return f"<User {self.email}>"
        except:
            return f"<User id={self.id}>"

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.first_name or self.last_name or self.email.split("@")[0]

    @property
    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role in [UserRole.ADMIN.value, UserRole.SUPER_ADMIN.value]

    @property
    def default_preferences(self) -> dict:
        """Default user preferences."""
        return {
            "theme": "light",
            "language": "en",
            "timezone": "UTC",
            "notifications": {
                "email_incidents": True,
                "email_alerts": False,
                "browser_notifications": True,
            },
            "dashboard_layout": [],
        }

    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        # Super admin and admin have all permissions
        if self.role in [UserRole.SUPER_ADMIN.value, UserRole.ADMIN.value]:
            return True
        return permission in (self.permissions or [])
