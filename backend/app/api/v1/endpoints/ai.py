"""
AI-related API endpoints.

Provides REST API access to AI capabilities:
- Incident classification
- Resolution suggestions
- Alert correlation
- AI status and configuration
"""

from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import (
    get_current_user,
    get_current_organization,
    get_db,
    CurrentUser,
    CurrentOrganization,
    DBSession,
)
from app.ml.service import AIService
from app.models.user import UserRole

router = APIRouter(prefix="/ai", tags=["AI"])


# Request/Response Models
class ClassifyIncidentRequest(BaseModel):
    """Request to classify an incident."""
    update_incident: bool = Field(default=True, description="Update incident with classification")


class ClassificationResponse(BaseModel):
    """Classification result response."""
    incident_id: str
    classification: dict
    updated: bool


class SuggestResolutionRequest(BaseModel):
    """Request for resolution suggestions."""
    update_incident: bool = Field(default=True, description="Update incident with suggestions")


class SuggestionResponse(BaseModel):
    """Resolution suggestion response."""
    incident_id: str
    suggestion: dict
    suggestion_text: str
    updated: bool


class AnalyzeIncidentRequest(BaseModel):
    """Request for full incident analysis."""
    update_incident: bool = Field(default=True, description="Update incident with analysis")


class AnalysisResponse(BaseModel):
    """Full analysis response."""
    incident_id: str
    classification: dict
    suggestion: dict
    suggestion_text: str
    updated: bool


class CorrelateAlertsRequest(BaseModel):
    """Request for alert correlation."""
    time_window_minutes: int = Field(default=30, ge=5, le=1440)
    status_filter: Optional[List[str]] = Field(default=None)


class CorrelationResponse(BaseModel):
    """Alert correlation response."""
    organization_id: str
    correlation: dict
    time_window_minutes: int


class AIStatusResponse(BaseModel):
    """AI service status response."""
    enabled: bool
    classification_enabled: bool
    suggestion_enabled: bool
    correlation_enabled: bool
    model: str
    confidence_threshold: float


class ClassifyTextRequest(BaseModel):
    """Request to classify text without an incident."""
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(default="", max_length=5000)
    affected_services: Optional[List[str]] = Field(default=None)
    tags: Optional[List[str]] = Field(default=None)


class SuggestTextRequest(BaseModel):
    """Request for suggestions without an incident."""
    title: str = Field(..., min_length=1, max_length=500)
    description: str = Field(default="", max_length=5000)
    category: str = Field(default="other")
    subcategory: str = Field(default="general")
    severity: str = Field(default="medium")
    priority: str = Field(default="p3")
    affected_services: Optional[List[str]] = Field(default=None)


# Endpoints
@router.get("/status", response_model=AIStatusResponse)
async def get_ai_status(
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Get AI service status and configuration.
    """
    async with AIService(db) as ai:
        status = await ai.get_ai_status()
    return AIStatusResponse(**status)


@router.post("/incidents/{incident_id}/classify", response_model=ClassificationResponse)
async def classify_incident(
    incident_id: UUID,
    request: ClassifyIncidentRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """
    Classify an incident using AI.

    Uses Mistral AI to analyze the incident and suggest:
    - Category and subcategory
    - Priority and severity levels
    - Keywords and affected components
    """
    # Verify incident belongs to organization
    from sqlalchemy import select
    from app.models.incident import Incident

    result = await db.execute(
        select(Incident)
        .where(Incident.id == incident_id)
        .where(Incident.organization_id == current_org.id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    async with AIService(db) as ai:
        classification = await ai.classify_incident(
            incident_id=incident_id,
            update_incident=request.update_incident,
        )

    return ClassificationResponse(**classification)


@router.post("/incidents/{incident_id}/suggest", response_model=SuggestionResponse)
async def suggest_resolution(
    incident_id: UUID,
    request: SuggestResolutionRequest,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """
    Generate resolution suggestions for an incident using AI.

    Uses Mistral AI to provide:
    - Step-by-step resolution instructions
    - Estimated resolution time
    - Risk assessment
    - Related runbooks
    """
    # Verify incident belongs to organization
    from sqlalchemy import select
    from app.models.incident import Incident

    result = await db.execute(
        select(Incident)
        .where(Incident.id == incident_id)
        .where(Incident.organization_id == current_org.id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    async with AIService(db) as ai:
        suggestion = await ai.suggest_resolution(
            incident_id=incident_id,
            update_incident=request.update_incident,
        )

    return SuggestionResponse(**suggestion)


@router.post("/incidents/{incident_id}/analyze", response_model=AnalysisResponse)
async def analyze_incident(
    incident_id: UUID,
    request: AnalyzeIncidentRequest,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """
    Perform full AI analysis on an incident.

    Combines classification and resolution suggestions in one call.
    """
    # Verify incident belongs to organization
    from sqlalchemy import select
    from app.models.incident import Incident

    result = await db.execute(
        select(Incident)
        .where(Incident.id == incident_id)
        .where(Incident.organization_id == current_org.id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    async with AIService(db) as ai:
        analysis = await ai.analyze_incident(
            incident_id=incident_id,
            update_incident=request.update_incident,
        )

    return AnalysisResponse(**analysis)


@router.post("/alerts/correlate", response_model=CorrelationResponse)
async def correlate_alerts(
    request: CorrelateAlertsRequest,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """
    Correlate alerts using AI.

    Analyzes recent alerts to find related groups and identify root causes.
    """
    async with AIService(db) as ai:
        correlation = await ai.correlate_alerts(
            organization_id=current_org.id,
            time_window_minutes=request.time_window_minutes,
            status_filter=request.status_filter,
        )

    return CorrelationResponse(**correlation)


@router.post("/classify", response_model=dict)
async def classify_text(
    request: ClassifyTextRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Classify text without creating an incident.

    Useful for previewing classification before creating an incident.
    """
    from app.ml.classifier import IncidentClassifier
    from app.ml.client import AnthropicClient

    client = AnthropicClient()
    async with client:
        classifier = IncidentClassifier(client)
        result = await classifier.classify(
            title=request.title,
            description=request.description,
            affected_services=request.affected_services or [],
            tags=request.tags or [],
        )

    return classifier.to_dict(result)


@router.post("/suggest", response_model=dict)
async def suggest_text(
    request: SuggestTextRequest,
    current_user: CurrentUser,
    db: DBSession,
):
    """
    Generate suggestions without an incident.

    Useful for getting AI suggestions before creating an incident.
    """
    from app.ml.suggester import ResolutionSuggester
    from app.ml.client import AnthropicClient

    client = AnthropicClient()
    async with client:
        suggester = ResolutionSuggester(client)
        result = await suggester.suggest(
            title=request.title,
            description=request.description,
            category=request.category,
            subcategory=request.subcategory,
            severity=request.severity,
            priority=request.priority,
            affected_services=request.affected_services or [],
        )

    return {
        "suggestion": suggester.to_dict(result),
        "suggestion_text": suggester.format_as_text(result),
    }


@router.post("/incidents/{incident_id}/analyze-async")
async def analyze_incident_async(
    incident_id: UUID,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """
    Queue an incident for async AI analysis.

    Returns immediately and processes in background via Celery.
    """
    # Verify incident belongs to organization
    from sqlalchemy import select
    from app.models.incident import Incident

    result = await db.execute(
        select(Incident)
        .where(Incident.id == incident_id)
        .where(Incident.organization_id == current_org.id)
    )
    incident = result.scalar_one_or_none()

    if not incident:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Incident not found"
        )

    # Queue the task
    from app.workers.tasks.incidents import analyze_incident as analyze_task
    task = analyze_task.delay(str(incident_id))

    return {
        "message": "Analysis queued",
        "incident_id": str(incident_id),
        "task_id": task.id,
    }


@router.post("/alerts/correlate-async")
async def correlate_alerts_async(
    request: CorrelateAlertsRequest,
    background_tasks: BackgroundTasks,
    current_user: CurrentUser,
    current_org: CurrentOrganization,
    db: DBSession,
):
    """
    Queue alert correlation for async processing.

    Returns immediately and processes in background via Celery.
    """
    from app.workers.tasks.alerts import correlate_alerts as correlate_task
    task = correlate_task.delay(
        str(current_org.id),
        request.time_window_minutes,
    )

    return {
        "message": "Correlation queued",
        "organization_id": str(current_org.id),
        "task_id": task.id,
    }
