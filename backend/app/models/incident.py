from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Integer, Numeric, DateTime, JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class IncidentStatus(str, enum.Enum):
    """Incident status states."""
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class IncidentPriority(str, enum.Enum):
    """Incident priority levels."""
    P1 = "p1"  # Critical
    P2 = "p2"  # High
    P3 = "p3"  # Medium
    P4 = "p4"  # Low
    P5 = "p5"  # Planning


class IncidentSeverity(str, enum.Enum):
    """Incident severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Incident(BaseModel):
    """Incident model for tracking operational issues."""

    __tablename__ = "incidents"

    # Organization reference
    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Incident identification
    incident_number = Column(String(50), unique=True, nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)

    # Status and classification
    status = Column(String(50), default=IncidentStatus.OPEN.value, nullable=False, index=True)
    priority = Column(String(20), default=IncidentPriority.P3.value, index=True)
    severity = Column(String(20), default=IncidentSeverity.MEDIUM.value, index=True)
    impact = Column(String(20), nullable=True)  # high, medium, low
    urgency = Column(String(20), nullable=True)  # high, medium, low

    # Categorization
    category = Column(String(100), nullable=True, index=True)
    subcategory = Column(String(100), nullable=True)

    # Assignment
    assigned_team_id = Column(
        GUID(),
        ForeignKey("teams.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    assigned_user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    reported_by_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Affected services/components
    affected_services = Column(JSON, default=list)  # List of affected service names

    # Business impact
    business_impact_score = Column(Numeric(5, 2), nullable=True)

    # AI Classification and suggestions
    ai_classification = Column(JSON, nullable=True)  # {category, confidence, features}
    ai_suggested_resolution = Column(Text, nullable=True)
    ai_confidence_score = Column(Numeric(3, 2), nullable=True)

    # Root cause and resolution
    root_cause = Column(Text, nullable=True)
    resolution_notes = Column(Text, nullable=True)

    # Prediction tracking
    is_predicted = Column(Boolean, default=False)
    prediction_source_id = Column(GUID(), nullable=True)

    # Timestamps
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    closed_at = Column(DateTime(timezone=True), nullable=True)
    sla_breach_at = Column(DateTime(timezone=True), nullable=True)

    # Additional metadata
    extra_data = Column(JSON, default=dict)
    tags = Column(JSON, default=list)

    # Relationships
    organization = relationship("Organization", back_populates="incidents")
    assigned_team = relationship("Team", back_populates="assigned_incidents")
    assigned_user = relationship(
        "User",
        back_populates="assigned_incidents",
        foreign_keys=[assigned_user_id],
    )
    reported_by = relationship(
        "User",
        back_populates="reported_incidents",
        foreign_keys=[reported_by_id],
    )
    comments = relationship("IncidentComment", back_populates="incident", lazy="dynamic")
    timeline = relationship("IncidentTimeline", back_populates="incident", lazy="dynamic")
    alerts = relationship("Alert", back_populates="incident", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Incident {self.incident_number}>"


class IncidentComment(BaseModel):
    """Comments on incidents."""

    __tablename__ = "incident_comments"

    incident_id = Column(
        GUID(),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    content = Column(Text, nullable=False)
    is_internal = Column(Boolean, default=False)  # Internal notes vs customer-visible

    # AI-generated flag
    is_ai_generated = Column(Boolean, default=False)

    # Attachments
    attachments = Column(JSON, default=list)  # [{name, url, type, size}]

    # Relationships
    incident = relationship("Incident", back_populates="comments")

    def __repr__(self) -> str:
        return f"<IncidentComment {self.id}>"


class IncidentTimeline(BaseModel):
    """Timeline events for incidents."""

    __tablename__ = "incident_timeline"

    incident_id = Column(
        GUID(),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Event type: created, updated, assigned, acknowledged, resolved, etc.
    event_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)

    # What changed
    changes = Column(JSON, nullable=True)  # {field: {old: x, new: y}}

    # Automation flag
    is_automated = Column(Boolean, default=False)

    # Relationships
    incident = relationship("Incident", back_populates="timeline")

    def __repr__(self) -> str:
        return f"<IncidentTimeline {self.event_type}>"
