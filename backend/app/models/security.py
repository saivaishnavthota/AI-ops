from sqlalchemy import Column, String, ForeignKey, Text, Integer, DateTime
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class SecurityEventSeverity(str, enum.Enum):
    """Security event severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class SecurityEventStatus(str, enum.Enum):
    """Security event status."""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    FALSE_POSITIVE = "false_positive"


class SecurityEvent(BaseModel):
    """Security events and incidents."""

    __tablename__ = "security_events"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Event details
    type = Column(String(100), nullable=False)
    severity = Column(String(20), nullable=False, index=True)
    source = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default=SecurityEventStatus.OPEN.value, index=True)
    
    # Affected resources
    affected_asset = Column(String(255), nullable=True)
    ip_address = Column(String(50), nullable=True)
    user = Column(String(255), nullable=True)
    
    # Additional details
    details = Column(Text, nullable=True)
    
    # Resolution tracking
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    resolution_notes = Column(Text, nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="security_events")

    def __repr__(self) -> str:
        try:
            return f"<SecurityEvent {self.type} - {self.severity}>"
        except:
            return f"<SecurityEvent id={self.id}>"
