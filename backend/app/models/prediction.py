from sqlalchemy import Column, String, ForeignKey, Text, Numeric, DateTime, JSON
from sqlalchemy.orm import relationship
import enum

from .base import BaseModel, GUID


class PredictionType(str, enum.Enum):
    """Prediction type."""
    CAPACITY = "capacity"
    PERFORMANCE = "performance"
    FAILURE = "failure"
    SECURITY = "security"
    COST = "cost"


class PredictionImpact(str, enum.Enum):
    """Prediction impact level."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PredictionStatus(str, enum.Enum):
    """Prediction status."""
    ACTIVE = "active"
    PREVENTED = "prevented"
    OCCURRED = "occurred"
    EXPIRED = "expired"


class Prediction(BaseModel):
    """AI-generated predictions for potential issues."""

    __tablename__ = "predictions"

    organization_id = Column(
        GUID(),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Prediction details
    type = Column(String(50), nullable=False, index=True)
    resource = Column(String(255), nullable=False)
    prediction = Column(Text, nullable=False)
    
    # Confidence and impact
    likelihood = Column(Numeric(3, 2), nullable=False)  # 0.00 to 1.00
    impact = Column(String(20), nullable=False, index=True)
    
    # Timeframe
    timeframe = Column(String(100), nullable=False)
    predicted_date = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    status = Column(String(20), default=PredictionStatus.ACTIVE.value, index=True)
    
    # Recommendations
    recommended_action = Column(Text, nullable=False)
    details = Column(Text, nullable=True)
    prevention_steps = Column(JSON, default=list)
    
    # Action tracking
    action_taken = Column(String(255), nullable=True)
    action_taken_at = Column(DateTime(timezone=True), nullable=True)
    action_taken_by_id = Column(
        GUID(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    
    # AI model info
    model_version = Column(String(50), nullable=True)
    confidence_factors = Column(JSON, default=dict)
    
    # Relationships
    organization = relationship("Organization", back_populates="predictions")

    def __repr__(self) -> str:
        try:
            return f"<Prediction {self.type} - {self.resource}>"
        except:
            return f"<Prediction id={self.id}>"
