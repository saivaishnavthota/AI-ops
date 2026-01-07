from sqlalchemy import Column, String, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship

from .base import BaseModel, GUID


class AuditLog(BaseModel):
    """Audit log for tracking all user actions."""

    __tablename__ = "audit_logs"

    # Organization reference
    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # User who performed the action
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Action details
    action = Column(String(100), nullable=False, index=True)  # create, update, delete, login, etc.
    resource_type = Column(String(100), nullable=False, index=True)  # incident, alert, user, etc.
    resource_id = Column(String(255), nullable=True, index=True)
    resource_name = Column(String(255), nullable=True)

    # What changed
    changes = Column(JSON, nullable=True)  # {field: {old: x, new: y}}

    # Additional context
    description = Column(Text, nullable=True)

    # Request info
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(Text, nullable=True)
    request_id = Column(String(36), nullable=True)

    # Status
    status = Column(String(20), default="success")  # success, failed
    error_message = Column(Text, nullable=True)

    # AI decision tracking (for AI-made decisions)
    ai_decision_id = Column(GUID(), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="audit_logs")
    user = relationship("User", back_populates="audit_logs")

    def __repr__(self) -> str:
        try:
            return f"<AuditLog {self.action} {self.resource_type}>"
        except:
            return f"<AuditLog id={self.id}>"
