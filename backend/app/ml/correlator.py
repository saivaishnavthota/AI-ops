"""
Alert Correlator using Mistral AI

Correlates alerts to:
- Identify related alerts that might be part of the same incident
- Find root cause alerts
- Reduce alert noise through intelligent grouping
- Suggest incident creation from correlated alerts
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime, timedelta

from .client import MistralClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class AlertInfo:
    """Minimal alert information for correlation."""
    id: str
    title: str
    message: str
    severity: str
    source: str
    host: Optional[str]
    service: Optional[str]
    created_at: datetime
    tags: List[str]


@dataclass
class CorrelationGroup:
    """Group of correlated alerts."""
    alert_ids: List[str]
    root_cause_id: Optional[str]
    correlation_type: str  # temporal, causal, symptomatic
    confidence: float
    reasoning: str
    suggested_incident_title: str
    suggested_incident_priority: str


@dataclass
class CorrelationResult:
    """Result of alert correlation analysis."""
    groups: List[CorrelationGroup]
    uncorrelated_ids: List[str]
    total_alerts: int
    analysis_summary: str


CORRELATION_SYSTEM_PROMPT = """You are an expert in IT infrastructure monitoring and alert correlation.

Your task is to analyze a set of alerts and identify which ones are related, potentially part of the same root cause issue.

Correlation types:
- temporal: Alerts occurring close in time that might be related
- causal: One alert directly causes another (e.g., server down causes service unavailable)
- symptomatic: Multiple alerts that are symptoms of a deeper issue

Guidelines:
1. Look for common hosts, services, or infrastructure components
2. Consider timing - alerts within a few minutes often share a root cause
3. Identify cascade patterns (e.g., database issue → application errors → user-facing problems)
4. Look for patterns in alert titles and messages
5. Consider severity escalation patterns

Always respond with valid JSON."""

CORRELATION_USER_PROMPT = """Analyze these alerts for correlation:

{alerts_json}

Time window: Last {time_window_minutes} minutes

Identify:
1. Groups of related alerts
2. Potential root cause for each group
3. Alerts that appear unrelated

Respond with JSON in this exact format:
{{
    "groups": [
        {{
            "alert_ids": ["id1", "id2", "id3"],
            "root_cause_id": "id1 or null if unclear",
            "correlation_type": "temporal/causal/symptomatic",
            "confidence": 0.0 to 1.0,
            "reasoning": "explanation of why these alerts are related",
            "suggested_incident_title": "descriptive title for incident",
            "suggested_incident_priority": "p1/p2/p3/p4/p5"
        }}
    ],
    "uncorrelated_ids": ["ids of alerts that don't correlate with others"],
    "analysis_summary": "brief summary of the overall alert situation"
}}"""


class AlertCorrelator:
    """AI-powered alert correlator using Mistral."""

    def __init__(self, client: Optional[MistralClient] = None):
        self.client = client

    async def correlate(
        self,
        alerts: List[AlertInfo],
        time_window_minutes: int = 30,
    ) -> CorrelationResult:
        """
        Correlate a list of alerts to find related groups.

        Args:
            alerts: List of AlertInfo objects to correlate
            time_window_minutes: Time window for correlation analysis

        Returns:
            CorrelationResult with grouped alerts and analysis
        """
        if not alerts:
            return CorrelationResult(
                groups=[],
                uncorrelated_ids=[],
                total_alerts=0,
                analysis_summary="No alerts to analyze",
            )

        if len(alerts) == 1:
            return CorrelationResult(
                groups=[],
                uncorrelated_ids=[alerts[0].id],
                total_alerts=1,
                analysis_summary="Single alert, no correlation possible",
            )

        if not settings.AI_CORRELATION_ENABLED:
            return self._default_correlation(alerts)

        if not settings.MISTRAL_API_KEY:
            logger.warning("Mistral API key not configured, using default correlation")
            return self._default_correlation(alerts)

        # Format alerts for AI analysis
        alerts_json = self._format_alerts(alerts)

        prompt = CORRELATION_USER_PROMPT.format(
            alerts_json=alerts_json,
            time_window_minutes=time_window_minutes,
        )

        try:
            client = self.client or MistralClient()
            async with client:
                result = await client.generate_json(
                    prompt=prompt,
                    system_prompt=CORRELATION_SYSTEM_PROMPT,
                    temperature=0.2,
                    max_tokens=4096,
                )

            return self._parse_correlation(result, alerts)

        except Exception as e:
            logger.error(f"AI correlation failed: {str(e)}")
            return self._default_correlation(alerts)

    def _format_alerts(self, alerts: List[AlertInfo]) -> str:
        """Format alerts as JSON string for AI analysis."""
        import json

        formatted = []
        for alert in alerts:
            formatted.append({
                "id": alert.id,
                "title": alert.title,
                "message": alert.message[:500] if alert.message else "",
                "severity": alert.severity,
                "source": alert.source,
                "host": alert.host,
                "service": alert.service,
                "created_at": alert.created_at.isoformat() if alert.created_at else None,
                "tags": alert.tags,
            })

        return json.dumps(formatted, indent=2)

    def _parse_correlation(
        self,
        result: Dict[str, Any],
        alerts: List[AlertInfo]
    ) -> CorrelationResult:
        """Parse and validate AI correlation response."""
        alert_ids = {a.id for a in alerts}
        groups = []

        for group_data in result.get("groups", []):
            # Validate alert IDs exist
            group_ids = [
                aid for aid in group_data.get("alert_ids", [])
                if aid in alert_ids
            ]

            if len(group_ids) < 2:
                continue

            # Validate root cause ID
            root_cause_id = group_data.get("root_cause_id")
            if root_cause_id and root_cause_id not in group_ids:
                root_cause_id = None

            # Normalize correlation type
            corr_type = group_data.get("correlation_type", "temporal").lower()
            if corr_type not in ["temporal", "causal", "symptomatic"]:
                corr_type = "temporal"

            # Normalize priority
            priority = group_data.get("suggested_incident_priority", "p3").lower()
            if priority not in ["p1", "p2", "p3", "p4", "p5"]:
                priority = "p3"

            # Ensure confidence is valid
            confidence = float(group_data.get("confidence", 0.5))
            confidence = max(0.0, min(1.0, confidence))

            groups.append(CorrelationGroup(
                alert_ids=group_ids,
                root_cause_id=root_cause_id,
                correlation_type=corr_type,
                confidence=confidence,
                reasoning=group_data.get("reasoning", "AI correlation"),
                suggested_incident_title=group_data.get(
                    "suggested_incident_title",
                    "Correlated Alert Group"
                ),
                suggested_incident_priority=priority,
            ))

        # Find uncorrelated alerts
        correlated_ids = set()
        for group in groups:
            correlated_ids.update(group.alert_ids)

        uncorrelated_ids = list(alert_ids - correlated_ids)

        return CorrelationResult(
            groups=groups,
            uncorrelated_ids=uncorrelated_ids,
            total_alerts=len(alerts),
            analysis_summary=result.get(
                "analysis_summary",
                f"Analyzed {len(alerts)} alerts, found {len(groups)} correlation groups"
            ),
        )

    def _default_correlation(self, alerts: List[AlertInfo]) -> CorrelationResult:
        """Return default correlation when AI is unavailable."""
        # Simple rule-based correlation by host/service
        groups_by_host: Dict[str, List[str]] = {}

        for alert in alerts:
            key = alert.host or alert.service or "unknown"
            if key not in groups_by_host:
                groups_by_host[key] = []
            groups_by_host[key].append(alert.id)

        groups = []
        correlated_ids = set()

        for key, ids in groups_by_host.items():
            if len(ids) >= 2:
                groups.append(CorrelationGroup(
                    alert_ids=ids,
                    root_cause_id=None,
                    correlation_type="temporal",
                    confidence=0.3,
                    reasoning=f"Grouped by common host/service: {key}",
                    suggested_incident_title=f"Multiple alerts on {key}",
                    suggested_incident_priority="p3",
                ))
                correlated_ids.update(ids)

        uncorrelated = [a.id for a in alerts if a.id not in correlated_ids]

        return CorrelationResult(
            groups=groups,
            uncorrelated_ids=uncorrelated,
            total_alerts=len(alerts),
            analysis_summary="Rule-based correlation (AI unavailable)",
        )

    def to_dict(self, result: CorrelationResult) -> Dict[str, Any]:
        """Convert correlation result to dictionary."""
        return {
            "groups": [
                {
                    "alert_ids": g.alert_ids,
                    "root_cause_id": g.root_cause_id,
                    "correlation_type": g.correlation_type,
                    "confidence": g.confidence,
                    "reasoning": g.reasoning,
                    "suggested_incident_title": g.suggested_incident_title,
                    "suggested_incident_priority": g.suggested_incident_priority,
                }
                for g in result.groups
            ],
            "uncorrelated_ids": result.uncorrelated_ids,
            "total_alerts": result.total_alerts,
            "analysis_summary": result.analysis_summary,
        }
