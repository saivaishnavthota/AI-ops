"""
Unified AI Service for AI-Ops Platform

Provides a high-level interface for all AI capabilities:
- Incident classification
- Resolution suggestions
- Alert correlation
- Combined analysis

Powered by Anthropic Claude AI.
"""

import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from .client import AnthropicClient
from .classifier import IncidentClassifier, ClassificationResult
from .suggester import ResolutionSuggester, ResolutionSuggestion
from .correlator import AlertCorrelator, AlertInfo, CorrelationResult
from ..config.settings import settings
from ..models.incident import Incident
from ..models.alert import Alert

logger = logging.getLogger(__name__)


class AIService:
    """
    Unified AI service providing all AI capabilities.
    Powered by Anthropic Claude AI.

    Usage:
        async with AIService(db) as ai:
            classification = await ai.classify_incident(incident_id)
            suggestion = await ai.suggest_resolution(incident_id)
    """

    def __init__(self, db: AsyncSession):
        self.db = db
        self._client: Optional[AnthropicClient] = None
        self.classifier: Optional[IncidentClassifier] = None
        self.suggester: Optional[ResolutionSuggester] = None
        self.correlator: Optional[AlertCorrelator] = None

    async def __aenter__(self):
        if settings.ANTHROPIC_API_KEY:
            self._client = AnthropicClient()
            await self._client.__aenter__()
            self.classifier = IncidentClassifier(self._client)
            self.suggester = ResolutionSuggester(self._client)
            self.correlator = AlertCorrelator(self._client)
        else:
            self.classifier = IncidentClassifier()
            self.suggester = ResolutionSuggester()
            self.correlator = AlertCorrelator()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._client:
            await self._client.__aexit__(exc_type, exc_val, exc_tb)

    async def classify_incident(
        self,
        incident_id: UUID,
        update_incident: bool = True,
    ) -> Dict[str, Any]:
        """
        Classify an incident and optionally update it with results.

        Args:
            incident_id: UUID of the incident to classify
            update_incident: Whether to update the incident record

        Returns:
            Classification result dictionary
        """
        # Fetch incident
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        incident = result.scalar_one_or_none()

        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        # Perform classification
        classification = await self.classifier.classify(
            title=incident.title,
            description=incident.description or "",
            affected_services=incident.affected_services or [],
            tags=incident.tags or [],
            source="incident",
        )

        classification_dict = self.classifier.to_dict(classification)

        # Update incident if requested
        if update_incident and classification.confidence >= settings.AI_CONFIDENCE_THRESHOLD:
            incident.ai_classification = classification_dict
            incident.ai_confidence_score = classification.confidence
            incident.category = classification.category
            incident.subcategory = classification.subcategory

            # Only update priority/severity if not already set or if AI is more severe
            if not incident.priority or incident.priority == "p3":
                incident.priority = classification.suggested_priority
            if not incident.severity or incident.severity == "medium":
                incident.severity = classification.suggested_severity

            await self.db.commit()
            await self.db.refresh(incident)

        return {
            "incident_id": str(incident_id),
            "classification": classification_dict,
            "updated": update_incident,
        }

    async def suggest_resolution(
        self,
        incident_id: UUID,
        update_incident: bool = True,
    ) -> Dict[str, Any]:
        """
        Generate resolution suggestions for an incident.

        Args:
            incident_id: UUID of the incident
            update_incident: Whether to update the incident record

        Returns:
            Resolution suggestion dictionary
        """
        # Fetch incident
        result = await self.db.execute(
            select(Incident).where(Incident.id == incident_id)
        )
        incident = result.scalar_one_or_none()

        if not incident:
            raise ValueError(f"Incident {incident_id} not found")

        # Generate suggestion
        suggestion = await self.suggester.suggest(
            title=incident.title,
            description=incident.description or "",
            category=incident.category or "other",
            subcategory=incident.subcategory or "general",
            severity=incident.severity or "medium",
            priority=incident.priority or "p3",
            affected_services=incident.affected_services or [],
            status=incident.status,
        )

        suggestion_text = self.suggester.format_as_text(suggestion)
        suggestion_dict = self.suggester.to_dict(suggestion)

        # Update incident if requested
        if update_incident and suggestion.confidence >= settings.AI_CONFIDENCE_THRESHOLD:
            incident.ai_suggested_resolution = suggestion_text
            if not incident.ai_confidence_score:
                incident.ai_confidence_score = suggestion.confidence
            await self.db.commit()
            await self.db.refresh(incident)

        return {
            "incident_id": str(incident_id),
            "suggestion": suggestion_dict,
            "suggestion_text": suggestion_text,
            "updated": update_incident,
        }

    async def analyze_incident(
        self,
        incident_id: UUID,
        update_incident: bool = True,
    ) -> Dict[str, Any]:
        """
        Perform full AI analysis on an incident (classification + suggestions).

        Args:
            incident_id: UUID of the incident
            update_incident: Whether to update the incident record

        Returns:
            Combined analysis results
        """
        classification_result = await self.classify_incident(
            incident_id, update_incident=update_incident
        )

        suggestion_result = await self.suggest_resolution(
            incident_id, update_incident=update_incident
        )

        return {
            "incident_id": str(incident_id),
            "classification": classification_result["classification"],
            "suggestion": suggestion_result["suggestion"],
            "suggestion_text": suggestion_result["suggestion_text"],
            "updated": update_incident,
        }

    async def correlate_alerts(
        self,
        organization_id: UUID,
        time_window_minutes: int = 30,
        status_filter: List[str] = None,
    ) -> Dict[str, Any]:
        """
        Correlate recent alerts for an organization.

        Args:
            organization_id: UUID of the organization
            time_window_minutes: Time window for alert correlation
            status_filter: Filter alerts by status (default: open, acknowledged)

        Returns:
            Correlation result dictionary
        """
        from datetime import timedelta

        if status_filter is None:
            status_filter = ["open", "acknowledged"]

        # Calculate time window
        cutoff_time = datetime.utcnow() - timedelta(minutes=time_window_minutes)

        # Fetch recent alerts
        result = await self.db.execute(
            select(Alert)
            .where(Alert.organization_id == organization_id)
            .where(Alert.status.in_(status_filter))
            .where(Alert.created_at >= cutoff_time)
            .order_by(Alert.created_at.desc())
            .limit(100)  # Limit to prevent overwhelming the AI
        )
        alerts = result.scalars().all()

        if not alerts:
            return {
                "organization_id": str(organization_id),
                "correlation": {
                    "groups": [],
                    "uncorrelated_ids": [],
                    "total_alerts": 0,
                    "analysis_summary": "No alerts in time window",
                },
                "time_window_minutes": time_window_minutes,
            }

        # Convert to AlertInfo objects
        alert_infos = [
            AlertInfo(
                id=str(alert.id),
                title=alert.title,
                message=alert.message or "",
                severity=alert.severity or "medium",
                source=alert.source or "unknown",
                host=alert.host,
                service=alert.service,
                created_at=alert.created_at,
                tags=alert.tags or [],
            )
            for alert in alerts
        ]

        # Perform correlation
        correlation = await self.correlator.correlate(
            alerts=alert_infos,
            time_window_minutes=time_window_minutes,
        )

        return {
            "organization_id": str(organization_id),
            "correlation": self.correlator.to_dict(correlation),
            "time_window_minutes": time_window_minutes,
        }

    async def get_ai_status(self) -> Dict[str, Any]:
        """Get AI service status and configuration."""
        return {
            "enabled": bool(settings.ANTHROPIC_API_KEY),
            "provider": "anthropic",
            "classification_enabled": settings.AI_CLASSIFICATION_ENABLED,
            "suggestion_enabled": settings.AI_SUGGESTION_ENABLED,
            "correlation_enabled": settings.AI_CORRELATION_ENABLED,
            "model": settings.ANTHROPIC_MODEL,
            "confidence_threshold": settings.AI_CONFIDENCE_THRESHOLD,
        }


async def get_ai_service(db: AsyncSession) -> AIService:
    """Factory function to create AI service instance."""
    return AIService(db)
