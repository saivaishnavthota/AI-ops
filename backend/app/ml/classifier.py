"""
Incident Classifier using Mistral AI

Automatically classifies incidents based on title and description into:
- Category (infrastructure, application, security, network, database, etc.)
- Subcategory (more specific classification)
- Priority suggestion
- Severity assessment
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .client import MistralClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class ClassificationResult:
    """Result of incident classification."""
    category: str
    subcategory: str
    suggested_priority: str
    suggested_severity: str
    confidence: float
    reasoning: str
    keywords: list[str]
    affected_components: list[str]


CLASSIFICATION_SYSTEM_PROMPT = """You are an expert IT operations analyst specializing in incident classification for managed services.

Your task is to analyze incident details and provide accurate classification to help operations teams respond effectively.

Categories available:
- infrastructure: Server, VM, container, storage, compute resource issues
- application: Application errors, crashes, performance issues, deployment problems
- security: Security incidents, vulnerabilities, unauthorized access, compliance issues
- network: Network connectivity, latency, DNS, load balancer, firewall issues
- database: Database performance, replication, backup, query issues
- monitoring: Monitoring system issues, false alerts, metric collection problems
- authentication: Login issues, SSO, MFA, identity provider problems
- integration: API failures, third-party service issues, webhook problems
- capacity: Resource exhaustion, scaling issues, quota limits
- other: Issues that don't fit other categories

Priority levels (P1-P5):
- P1 (Critical): Complete service outage, data loss, security breach
- P2 (High): Major feature unavailable, significant degradation
- P3 (Medium): Partial impact, workaround available
- P4 (Low): Minor issue, minimal impact
- P5 (Planning): No immediate impact, future consideration

Severity levels:
- critical: Immediate action required, business-critical impact
- high: Urgent attention needed, significant impact
- medium: Important but not urgent, moderate impact
- low: Minor impact, can be scheduled
- info: Informational, no action required

Always respond with valid JSON."""

CLASSIFICATION_USER_PROMPT = """Analyze this incident and provide classification:

Title: {title}

Description: {description}

Additional Context:
- Affected Services: {affected_services}
- Tags: {tags}
- Source: {source}

Respond with JSON in this exact format:
{{
    "category": "one of the categories listed",
    "subcategory": "more specific classification within category",
    "suggested_priority": "p1/p2/p3/p4/p5",
    "suggested_severity": "critical/high/medium/low/info",
    "confidence": 0.0 to 1.0,
    "reasoning": "brief explanation of classification decision",
    "keywords": ["extracted", "relevant", "keywords"],
    "affected_components": ["identified", "components", "or systems"]
}}"""


class IncidentClassifier:
    """AI-powered incident classifier using Mistral."""

    def __init__(self, client: Optional[MistralClient] = None):
        self.client = client
        self._categories = [
            "infrastructure", "application", "security", "network",
            "database", "monitoring", "authentication", "integration",
            "capacity", "other"
        ]

    async def classify(
        self,
        title: str,
        description: str = "",
        affected_services: list[str] = None,
        tags: list[str] = None,
        source: str = "manual",
    ) -> ClassificationResult:
        """
        Classify an incident using AI.

        Args:
            title: Incident title
            description: Incident description
            affected_services: List of affected service names
            tags: Associated tags
            source: Source of the incident

        Returns:
            ClassificationResult with category, priority, severity, etc.
        """
        if not settings.AI_CLASSIFICATION_ENABLED:
            return self._default_classification()

        if not settings.MISTRAL_API_KEY:
            logger.warning("Mistral API key not configured, using default classification")
            return self._default_classification()

        prompt = CLASSIFICATION_USER_PROMPT.format(
            title=title,
            description=description or "No description provided",
            affected_services=", ".join(affected_services or []) or "Unknown",
            tags=", ".join(tags or []) or "None",
            source=source,
        )

        try:
            client = self.client or MistralClient()
            async with client:
                result = await client.generate_json(
                    prompt=prompt,
                    system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
                    temperature=0.1,
                )

            # Validate and normalize response
            return self._parse_classification(result)

        except Exception as e:
            logger.error(f"AI classification failed: {str(e)}")
            return self._default_classification()

    def _parse_classification(self, result: Dict[str, Any]) -> ClassificationResult:
        """Parse and validate AI classification response."""
        # Normalize category
        category = result.get("category", "other").lower()
        if category not in self._categories:
            category = "other"

        # Normalize priority
        priority = result.get("suggested_priority", "p3").lower()
        if priority not in ["p1", "p2", "p3", "p4", "p5"]:
            priority = "p3"

        # Normalize severity
        severity = result.get("suggested_severity", "medium").lower()
        if severity not in ["critical", "high", "medium", "low", "info"]:
            severity = "medium"

        # Ensure confidence is valid
        confidence = float(result.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))

        return ClassificationResult(
            category=category,
            subcategory=result.get("subcategory", "general"),
            suggested_priority=priority,
            suggested_severity=severity,
            confidence=confidence,
            reasoning=result.get("reasoning", "AI classification applied"),
            keywords=result.get("keywords", []),
            affected_components=result.get("affected_components", []),
        )

    def _default_classification(self) -> ClassificationResult:
        """Return default classification when AI is unavailable."""
        return ClassificationResult(
            category="other",
            subcategory="unclassified",
            suggested_priority="p3",
            suggested_severity="medium",
            confidence=0.0,
            reasoning="Default classification - AI unavailable",
            keywords=[],
            affected_components=[],
        )

    def to_dict(self, result: ClassificationResult) -> Dict[str, Any]:
        """Convert classification result to dictionary for storage."""
        return {
            "category": result.category,
            "subcategory": result.subcategory,
            "suggested_priority": result.suggested_priority,
            "suggested_severity": result.suggested_severity,
            "confidence": result.confidence,
            "reasoning": result.reasoning,
            "keywords": result.keywords,
            "affected_components": result.affected_components,
        }
