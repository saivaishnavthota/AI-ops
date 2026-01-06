from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Integer, Numeric, DateTime, JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class AlertStatus(str, enum.Enum):
    """Alert status states."""
    OPEN = "open"
    FIRING = "firing"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"
    CONVERTED_TO_INCIDENT = "converted_to_incident"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    WARNING = "warning"
    LOW = "low"
    INFO = "info"


class Alert(BaseModel):
    """Alert model for monitoring alerts."""

    __tablename__ = "alerts"

    # Organization reference
    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # External alert ID (from monitoring system)
    alert_id_external = Column(String(255), nullable=True, index=True)

    # Source information
    source = Column(String(100), nullable=False, index=True)  # prometheus, datadog, custom, etc.
    source_type = Column(String(50), nullable=True)  # metric, log, event

    # Alert details
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=True)
    message = Column(Text, nullable=True)
    severity = Column(String(20), default=AlertSeverity.WARNING.value, index=True)
    status = Column(String(50), default=AlertStatus.OPEN.value, index=True)
    
    # Environment
    environment = Column(String(100), nullable=True, index=True)

    # Target information
    host = Column(String(255), nullable=True, index=True)
    service = Column(String(255), nullable=True, index=True)

    # Metric information
    metric_name = Column(String(255), nullable=True)
    metric_value = Column(Numeric(20, 5), nullable=True)
    threshold_value = Column(Numeric(20, 5), nullable=True)

    # Tags and labels
    tags = Column(JSON, default=dict)

    # Correlation
    correlation_id = Column(GUID(), nullable=True, index=True)

    # Link to incident
    incident_id = Column(
        GUID(),
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Suppression
    is_suppressed = Column(Boolean, default=False)
    suppression_reason = Column(Text, nullable=True)
    suppressed_until = Column(DateTime(timezone=True), nullable=True)

    # AI correlation score
    ai_correlation_score = Column(Numeric(3, 2), nullable=True)

    # Timestamps
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    acknowledged_by_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolved_by_id = Column(GUID(), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)

    # Raw payload from source
    raw_payload = Column(JSON, nullable=True)
    raw_data = Column(JSON, nullable=True)  # Alias for compatibility
    external_id = Column(String(255), nullable=True, index=True)  # External system ID

    # Fingerprint for deduplication
    fingerprint = Column(String(255), nullable=True, index=True)

    # Count of occurrences (for deduplication)
    occurrence_count = Column(Integer, default=1)
    first_occurrence = Column(DateTime(timezone=True), nullable=True)
    first_occurrence_at = Column(DateTime(timezone=True), nullable=True)  # Alias
    last_occurrence = Column(DateTime(timezone=True), nullable=True)
    last_occurrence_at = Column(DateTime(timezone=True), nullable=True)  # Alias

    # Relationships
    organization = relationship("Organization", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")
    correlations = relationship(
        "AlertCorrelation",
        foreign_keys="[AlertCorrelation.alert_id]",
        back_populates="alert",
        lazy="dynamic"
    )

    def __repr__(self) -> str:
        return f"<Alert {self.id} - {self.title}>"


class AlertCorrelation(BaseModel):
    """Alert correlation groups."""

    __tablename__ = "alert_correlations"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Correlation group ID
    correlation_group_id = Column(GUID(), nullable=True, index=True)

    alert_id = Column(
        GUID(),
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    
    related_alert_id = Column(
        GUID(),
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Correlation type: temporal, topological, causal, ai, rule
    correlation_type = Column(String(50), nullable=True)

    # Confidence score
    confidence_score = Column(Numeric(3, 2), nullable=True)

    # Reason for correlation
    correlation_reason = Column(Text, nullable=True)

    # Is this the root cause alert?
    is_root_cause = Column(Boolean, default=False)

    # Relationships
    organization = relationship("Organization")
    alert = relationship("Alert", foreign_keys=[alert_id], back_populates="correlations")
    related_alert = relationship("Alert", foreign_keys=[related_alert_id])

    def __repr__(self) -> str:
        return f"<AlertCorrelation {self.alert_id} -> {self.related_alert_id}>"


class AlertSource(BaseModel):
    """Configuration for alert sources."""

    __tablename__ = "alert_sources"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(255), nullable=False)
    source_type = Column(String(100), nullable=False)  # prometheus, datadog, webhook, etc.

    # Configuration
    config = Column(JSON, default=dict)

    # Authentication
    api_key = Column(String(255), nullable=True)  # Encrypted in production
    webhook_secret = Column(String(255), nullable=True)

    # Status
    is_active = Column(Boolean, default=True)
    last_received_at = Column(DateTime(timezone=True), nullable=True)

    # Alert count
    total_alerts_received = Column(Integer, default=0)

    def __repr__(self) -> str:
        return f"<AlertSource {self.name}>"
