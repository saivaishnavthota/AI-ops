from sqlalchemy import Column, String, Boolean, ForeignKey, Text, Integer, Numeric, DateTime, JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class PlaybookStatus(str, enum.Enum):
    """Playbook execution status."""
    PENDING = "pending"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class Playbook(BaseModel):
    """Automation playbook for incident remediation."""

    __tablename__ = "playbooks"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)

    # Trigger conditions (when to auto-execute)
    trigger_conditions = Column(JSON, default=dict)
    # Example: {"alert_severity": "critical", "service": "api-gateway"}

    # Playbook steps
    steps = Column(JSON, default=list)
    # Example: [
    #   {"type": "script", "name": "Check service", "command": "systemctl status nginx"},
    #   {"type": "notification", "channel": "slack", "message": "Investigating..."},
    #   {"type": "approval", "roles": ["admin"]},
    #   {"type": "script", "name": "Restart service", "command": "systemctl restart nginx"}
    # ]

    # Approval settings
    requires_approval = Column(Boolean, default=False)
    approval_roles = Column(JSON, default=list)  # ["admin", "operator"]

    # Status
    is_active = Column(Boolean, default=True)

    # Statistics
    execution_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failure_count = Column(Integer, default=0)
    avg_execution_time_seconds = Column(Integer, nullable=True)

    # Created by
    created_by_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Tags for organization
    tags = Column(JSON, default=list)

    # Relationships
    organization = relationship("Organization", back_populates="playbooks")
    executions = relationship("PlaybookExecution", back_populates="playbook", lazy="dynamic")

    def __repr__(self) -> str:
        try:
            return f"<Playbook {self.name}>"
        except:
            return f"<Playbook id={self.id}>"

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        if self.execution_count == 0:
            return 0.0
        return round((self.success_count / self.execution_count) * 100, 2)


class PlaybookExecution(BaseModel):
    """Playbook execution history."""

    __tablename__ = "playbook_executions"

    playbook_id = Column(
        GUID(),
        ForeignKey("playbooks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # What triggered this execution
    incident_id = Column(
        GUID(),
        ForeignKey("incidents.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    alert_id = Column(
        GUID(),
        ForeignKey("alerts.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Status
    status = Column(String(50), default=PlaybookStatus.PENDING.value, index=True)

    # Trigger type: manual, auto, scheduled
    triggered_by = Column(String(50), nullable=True)
    triggered_by_user_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Approval tracking
    approval_required = Column(Boolean, default=False)
    approved_by_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approval_comment = Column(Text, nullable=True)

    # Execution log (step by step)
    execution_log = Column(JSON, default=list)
    # Example: [
    #   {"step": 0, "status": "completed", "output": "nginx running", "duration_ms": 150},
    #   {"step": 1, "status": "failed", "error": "Timeout", "duration_ms": 30000}
    # ]

    # Result summary
    result = Column(JSON, nullable=True)

    # Current step (for in-progress executions)
    current_step = Column(Integer, default=0)

    # Timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    # Error information
    error_message = Column(Text, nullable=True)

    # Relationships
    playbook = relationship("Playbook", back_populates="executions")

    def __repr__(self) -> str:
        return f"<PlaybookExecution {self.id} - {self.status}>"

    @property
    def duration_seconds(self) -> int:
        """Calculate execution duration."""
        if self.started_at and self.completed_at:
            return int((self.completed_at - self.started_at).total_seconds())
        return 0


class PlaybookStep(BaseModel):
    """Individual steps in a playbook (for future extensibility)."""

    __tablename__ = "playbook_steps"

    playbook_id = Column(
        GUID(),
        ForeignKey("playbooks.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Step order
    order = Column(Integer, nullable=False)

    # Step type: script, notification, approval, condition, wait
    step_type = Column(String(50), nullable=False)

    # Step name
    name = Column(String(255), nullable=False)

    # Step configuration
    config = Column(JSON, default=dict)

    # Timeout settings
    timeout_seconds = Column(Integer, default=300)

    # Retry settings
    retry_count = Column(Integer, default=0)
    retry_delay_seconds = Column(Integer, default=30)

    # Is this step optional?
    is_optional = Column(Boolean, default=False)

    def __repr__(self) -> str:
        return f"<PlaybookStep {self.name}>"
