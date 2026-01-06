from sqlalchemy import Column, String, ForeignKey, Text, Integer, JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class InvestigationStatus(str, enum.Enum):
    """Investigation status."""
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"


class InvestigationPriority(str, enum.Enum):
    """Investigation priority."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Investigation(BaseModel):
    """Security investigations."""

    __tablename__ = "investigations"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Investigation details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(20), default=InvestigationStatus.PENDING.value, index=True)
    priority = Column(String(20), nullable=False, index=True)
    
    # Assignment
    assignee_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    assignee_name = Column(String(255), nullable=False)
    
    # Progress tracking
    progress = Column(Integer, default=0)
    events_linked = Column(Integer, default=0)
    
    # Investigation data
    findings = Column(JSON, default=list)
    timeline = Column(JSON, default=list)
    
    # Creator
    created_by_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    organization = relationship("Organization", back_populates="investigations")

    def __repr__(self) -> str:
        return f"<Investigation {self.title}>"
