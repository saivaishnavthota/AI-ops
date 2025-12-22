from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Integer, Numeric, DateTime, JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class AlertStatus(str, enum.Enum):
    """Alert status states."""
    FIRING = "firing"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class AlertSeverity(str, enum.Enum):
    """Alert severity levels."""
    CRITICAL = "critical"
    WARNING = "warning"
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
    title = Column(String(500), nullable=True)
    message = Column(Text, nullable=True)
    severity = Column(String(20), default=AlertSeverity.WARNING.value, index=True)
    status = Column(String(50), default=AlertStatus.FIRING.value, index=True)

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

    # Raw payload from source
    raw_payload = Column(JSON, nullable=True)

    # Fingerprint for deduplication
    fingerprint = Column(String(255), nullable=True, index=True)

    # Count of occurrences (for deduplication)
    occurrence_count = Column(Integer, default=1)
    first_occurrence_at = Column(DateTime(timezone=True), nullable=True)
    last_occurrence_at = Column(DateTime(timezone=True), nullable=True)

    # Relationships
    organization = relationship("Organization", back_populates="alerts")
    incident = relationship("Incident", back_populates="alerts")
    correlations = relationship("AlertCorrelation", back_populates="alert", lazy="dynamic")

    def __repr__(self) -> str:
        return f"<Alert {self.id} - {self.title}>"


class AlertCorrelation(BaseModel):
    """Alert correlation groups."""

    __tablename__ = "alert_correlations"

    # Correlation group ID
    correlation_group_id = Column(GUID(), nullable=False, index=True)

    alert_id = Column(
        GUID(),
        ForeignKey("alerts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Correlation type: temporal, topological, causal
    correlation_type = Column(String(50), nullable=True)

    # Confidence score
    confidence_score = Column(Numeric(3, 2), nullable=True)

    # Reason for correlation
    correlation_reason = Column(Text, nullable=True)

    # Is this the root cause alert?
    is_root_cause = Column(Boolean, default=False)

    # Relationships
    alert = relationship("Alert", back_populates="correlations")

    def __repr__(self) -> str:
        return f"<AlertCorrelation {self.correlation_group_id}>"


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
