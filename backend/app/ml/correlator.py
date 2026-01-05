"""
Alert Correlator using Anthropic Claude AI

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

from .client import AnthropicClient
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
    """AI-powered alert correlator using Anthropic Claude."""

    def __init__(self, client: Optional[AnthropicClient] = None):
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

        if not settings.ANTHROPIC_API_KEY:
            logger.info("Using mock AI correlation (no API key configured)")
            return self._default_correlation(alerts)

        # Format alerts for AI analysis
        alerts_json = self._format_alerts(alerts)

        prompt = CORRELATION_USER_PROMPT.format(
            alerts_json=alerts_json,
            time_window_minutes=time_window_minutes,
        )

        try:
            client = self.client or AnthropicClient()
            async with client:
                result = await client.generate_json(
                    prompt=prompt,
                    system_prompt=CORRELATION_SYSTEM_PROMPT,
                    temperature=0.2,
                    max_tokens=4096,
                )

            return self._parse_correlation(result, alerts)

        except Exception as e:
            logger.error(f"AI correlation failed: {str(e)}, falling back to mock")
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
        """
        Return smart mock correlation when AI is unavailable.
        Uses multiple correlation strategies for realistic demo behavior.
        """
        from collections import defaultdict

        # Strategy 1: Group by host
        groups_by_host: Dict[str, List[AlertInfo]] = defaultdict(list)
        # Strategy 2: Group by service
        groups_by_service: Dict[str, List[AlertInfo]] = defaultdict(list)
        # Strategy 3: Group by severity (for cascade detection)
        groups_by_severity: Dict[str, List[AlertInfo]] = defaultdict(list)
        # Strategy 4: Temporal grouping (alerts within 5 minutes)
        temporal_groups: List[List[AlertInfo]] = []

        for alert in alerts:
            if alert.host:
                groups_by_host[alert.host].append(alert)
            if alert.service:
                groups_by_service[alert.service].append(alert)
            groups_by_severity[alert.severity].append(alert)

        # Temporal grouping: sort by time and group nearby alerts
        sorted_alerts = sorted(alerts, key=lambda a: a.created_at if a.created_at else datetime.min)
        current_temporal_group = []

        for i, alert in enumerate(sorted_alerts):
            if not current_temporal_group:
                current_temporal_group.append(alert)
            else:
                last_alert = current_temporal_group[-1]
                if last_alert.created_at and alert.created_at:
                    time_diff = abs((alert.created_at - last_alert.created_at).total_seconds())
                    if time_diff <= 300:  # 5 minutes
                        current_temporal_group.append(alert)
                    else:
                        if len(current_temporal_group) >= 2:
                            temporal_groups.append(current_temporal_group)
                        current_temporal_group = [alert]
                else:
                    current_temporal_group.append(alert)

        if len(current_temporal_group) >= 2:
            temporal_groups.append(current_temporal_group)

        # Build correlation groups with priority:
        # 1. Host + temporal (strongest correlation)
        # 2. Service + temporal
        # 3. Pure host grouping
        # 4. Pure service grouping

        groups = []
        correlated_ids = set()

        # Priority correlation patterns
        correlation_patterns = [
            # Pattern: Critical alert followed by multiple warnings on same host
            {
                "name": "cascade_pattern",
                "check": lambda host_alerts: (
                    any(a.severity == "critical" for a in host_alerts) and
                    sum(1 for a in host_alerts if a.severity == "warning") >= 1
                ),
                "type": "causal",
                "confidence": 0.92,
                "priority": "p1",
            },
            # Pattern: Multiple alerts on same host
            {
                "name": "host_cluster",
                "check": lambda host_alerts: len(host_alerts) >= 2,
                "type": "symptomatic",
                "confidence": 0.85,
                "priority": "p2",
            },
        ]

        # Process host groups first (highest correlation confidence)
        for host, host_alerts in groups_by_host.items():
            if len(host_alerts) < 2:
                continue

            # Check for cascade pattern (critical -> warning)
            critical_alerts = [a for a in host_alerts if a.severity == "critical"]
            warning_alerts = [a for a in host_alerts if a.severity == "warning"]

            if critical_alerts and warning_alerts:
                # This is likely a cascade - critical is root cause
                all_related = critical_alerts + warning_alerts
                alert_ids = [a.id for a in all_related if a.id not in correlated_ids]

                if len(alert_ids) >= 2:
                    root_cause = critical_alerts[0].id if critical_alerts else None

                    groups.append(CorrelationGroup(
                        alert_ids=alert_ids,
                        root_cause_id=root_cause,
                        correlation_type="causal",
                        confidence=0.92,
                        reasoning=f"Cascade detected: Critical alert on {host} triggered subsequent warnings. Root cause appears to be: {critical_alerts[0].title if critical_alerts else 'unknown'}",
                        suggested_incident_title=f"Service degradation cascade on {host}",
                        suggested_incident_priority="p1",
                    ))
                    correlated_ids.update(alert_ids)

            elif len(host_alerts) >= 2:
                # Regular host grouping
                alert_ids = [a.id for a in host_alerts if a.id not in correlated_ids]

                if len(alert_ids) >= 2:
                    # Determine priority based on severities
                    has_critical = any(a.severity == "critical" for a in host_alerts)
                    priority = "p1" if has_critical else "p2"

                    # Try to identify root cause (earliest or most severe)
                    sorted_by_time = sorted(
                        [a for a in host_alerts if a.id in alert_ids],
                        key=lambda a: a.created_at if a.created_at else datetime.max
                    )
                    root_cause = sorted_by_time[0].id if sorted_by_time else None

                    groups.append(CorrelationGroup(
                        alert_ids=alert_ids,
                        root_cause_id=root_cause,
                        correlation_type="symptomatic",
                        confidence=0.85,
                        reasoning=f"Multiple alerts detected on host {host}. These symptoms likely share a common cause.",
                        suggested_incident_title=f"Multiple alerts on {host}",
                        suggested_incident_priority=priority,
                    ))
                    correlated_ids.update(alert_ids)

        # Process service groups (for alerts not already correlated)
        for service, service_alerts in groups_by_service.items():
            uncorrelated_service_alerts = [a for a in service_alerts if a.id not in correlated_ids]

            if len(uncorrelated_service_alerts) >= 2:
                alert_ids = [a.id for a in uncorrelated_service_alerts]

                # Determine priority
                has_critical = any(a.severity == "critical" for a in uncorrelated_service_alerts)
                priority = "p2" if has_critical else "p3"

                groups.append(CorrelationGroup(
                    alert_ids=alert_ids,
                    root_cause_id=None,
                    correlation_type="temporal",
                    confidence=0.78,
                    reasoning=f"Multiple alerts affecting service {service} within correlation window.",
                    suggested_incident_title=f"Service alerts for {service}",
                    suggested_incident_priority=priority,
                ))
                correlated_ids.update(alert_ids)

        # Process temporal groups (for remaining alerts)
        for temp_group in temporal_groups:
            uncorrelated_temp_alerts = [a for a in temp_group if a.id not in correlated_ids]

            if len(uncorrelated_temp_alerts) >= 2:
                alert_ids = [a.id for a in uncorrelated_temp_alerts]

                groups.append(CorrelationGroup(
                    alert_ids=alert_ids,
                    root_cause_id=None,
                    correlation_type="temporal",
                    confidence=0.65,
                    reasoning="Alerts occurred within a 5-minute window, suggesting possible relationship.",
                    suggested_incident_title="Temporally correlated alerts",
                    suggested_incident_priority="p3",
                ))
                correlated_ids.update(alert_ids)

        # Find uncorrelated alerts
        uncorrelated = [a.id for a in alerts if a.id not in correlated_ids]

        # Generate analysis summary
        if groups:
            cascade_count = sum(1 for g in groups if g.correlation_type == "causal")
            symptomatic_count = sum(1 for g in groups if g.correlation_type == "symptomatic")
            temporal_count = sum(1 for g in groups if g.correlation_type == "temporal")

            summary_parts = [f"Analyzed {len(alerts)} alerts"]
            if cascade_count:
                summary_parts.append(f"{cascade_count} cascade pattern(s) detected")
            if symptomatic_count:
                summary_parts.append(f"{symptomatic_count} symptomatic group(s)")
            if temporal_count:
                summary_parts.append(f"{temporal_count} temporal correlation(s)")
            if uncorrelated:
                summary_parts.append(f"{len(uncorrelated)} uncorrelated")

            analysis_summary = ". ".join(summary_parts) + "."
        else:
            analysis_summary = f"Analyzed {len(alerts)} alerts. No strong correlations found based on mock analysis rules."

        return CorrelationResult(
            groups=groups,
            uncorrelated_ids=uncorrelated,
            total_alerts=len(alerts),
            analysis_summary=analysis_summary,
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
