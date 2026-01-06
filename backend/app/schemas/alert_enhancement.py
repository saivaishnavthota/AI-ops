from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID


# Webhook Endpoint Schemas
class AlertWebhookEndpointBase(BaseModel):
    name: str
    description: Optional[str] = None
    source_type: str = Field(..., description="prometheus, grafana, datadog, pagerduty, generic")
    source_config: Optional[Dict[str, Any]] = None
    field_mapping: Optional[Dict[str, str]] = None
    filters: Optional[Dict[str, Any]] = None
    secret_token: Optional[str] = None


class AlertWebhookEndpointCreate(AlertWebhookEndpointBase):
    pass


class AlertWebhookEndpointResponse(AlertWebhookEndpointBase):
    id: UUID
    organization_id: UUID
    endpoint_url: str
    is_active: bool
    alerts_received: int
    last_alert_received: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AlertWebhookResponse(BaseModel):
    status: str
    alerts_processed: int
    alert_ids: List[str]
    message: str


# Suppression Rule Schemas
class AlertSuppressionRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    criteria: Dict[str, Any] = Field(..., description="Matching criteria for suppression")
    suppression_duration: int = Field(..., description="Duration in seconds")
    max_occurrences: int = Field(1, description="Max alerts before suppression")
    schedule: Optional[Dict[str, Any]] = None
    is_active: bool = True


class AlertSuppressionRuleCreate(AlertSuppressionRuleBase):
    pass


class AlertSuppressionRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None
    suppression_duration: Optional[int] = None
    max_occurrences: Optional[int] = None
    schedule: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class AlertSuppressionRuleResponse(AlertSuppressionRuleBase):
    id: UUID
    organization_id: UUID
    suppressed_count: int
    last_triggered: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Correlation Rule Schemas
class AlertCorrelationRuleBase(BaseModel):
    name: str
    description: Optional[str] = None
    criteria: Dict[str, Any] = Field(..., description="Correlation criteria")
    use_ai_correlation: bool = True
    similarity_threshold: float = Field(0.8, ge=0.0, le=1.0)
    is_active: bool = True
    priority: int = Field(1, description="Higher number = higher priority")


class AlertCorrelationRuleCreate(AlertCorrelationRuleBase):
    pass


class AlertCorrelationRuleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    criteria: Optional[Dict[str, Any]] = None
    use_ai_correlation: Optional[bool] = None
    similarity_threshold: Optional[float] = None
    is_active: Optional[bool] = None
    priority: Optional[int] = None


class AlertCorrelationRuleResponse(AlertCorrelationRuleBase):
    id: UUID
    organization_id: UUID
    correlation_count: int
    last_triggered: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Deduplication Schemas
class AlertDeduplicationResponse(BaseModel):
    id: UUID
    organization_id: UUID
    primary_alert_id: UUID
    duplicate_alert_id: UUID
    similarity_score: float
    deduplication_method: str
    deduplication_criteria: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True


# Alert to Incident Conversion Schemas
class AlertToIncidentConversionResponse(BaseModel):
    id: UUID
    organization_id: UUID
    alert_id: UUID
    incident_id: UUID
    conversion_method: str
    conversion_rule_id: Optional[UUID]
    converted_by_id: Optional[UUID]
    conversion_context: Optional[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True
