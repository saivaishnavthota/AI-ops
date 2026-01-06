from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from .base import BaseSchema, PaginatedResponse


class PredictionBase(BaseModel):
    """Base prediction schema."""

    type: Optional[str] = None
    resource: Optional[str] = None
    prediction: Optional[str] = None
    likelihood: Optional[Decimal] = None
    impact: Optional[str] = None
    timeframe: Optional[str] = None
    recommended_action: Optional[str] = None
    details: Optional[str] = None
    prevention_steps: Optional[List[str]] = None


class PredictionCreate(PredictionBase):
    """Prediction creation schema."""

    type: str
    resource: str
    prediction: str
    likelihood: Decimal = Field(..., ge=0, le=1)
    impact: str
    timeframe: str
    recommended_action: str


class PredictionUpdate(BaseModel):
    """Prediction update schema."""

    status: Optional[str] = None
    action_taken: Optional[str] = None


class PredictionActionRequest(BaseModel):
    """Prediction action request."""

    action_taken: str


class PredictionResponse(BaseSchema):
    """Prediction response schema."""

    id: UUID
    organization_id: UUID
    type: str
    resource: str
    prediction: str
    likelihood: float
    impact: str
    timeframe: str
    predicted_date: Optional[datetime]
    status: str
    recommended_action: str
    details: Optional[str]
    prevention_steps: List[str]
    action_taken: Optional[str]
    action_taken_at: Optional[datetime]
    action_taken_by_id: Optional[UUID]
    model_version: Optional[str]
    confidence_factors: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


class PredictionListResponse(PaginatedResponse[PredictionResponse]):
    """Paginated prediction list response."""

    pass


class PredictionStatsResponse(BaseModel):
    """Prediction statistics response."""

    total_predictions: int
    active_predictions: int
    prevented_count: int
    occurred_count: int
    expired_count: int
    avg_likelihood: float
    by_type: Dict[str, int]
    by_impact: Dict[str, int]
