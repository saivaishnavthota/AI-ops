"""
Resolution Suggester using Mistral AI

Generates intelligent resolution suggestions for incidents based on:
- Incident details (title, description, category)
- Historical patterns
- Best practices knowledge
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .client import MistralClient
from ..config.settings import settings

logger = logging.getLogger(__name__)


@dataclass
class ResolutionSuggestion:
    """Resolution suggestion result."""
    summary: str
    steps: List[str]
    estimated_time: str
    risk_level: str
    requires_approval: bool
    automation_possible: bool
    related_runbooks: List[str]
    confidence: float


SUGGESTION_SYSTEM_PROMPT = """You are an expert Site Reliability Engineer (SRE) and IT operations specialist.

Your task is to provide actionable resolution suggestions for IT incidents based on the incident details provided.

Guidelines:
1. Provide clear, step-by-step instructions that operations staff can follow
2. Consider safety and rollback procedures
3. Identify if the resolution requires human approval for critical actions
4. Suggest relevant monitoring checks after resolution
5. Estimate time based on typical resolution patterns
6. Identify if automation/playbook execution is possible

Risk levels:
- low: Safe changes, easily reversible
- medium: Some risk, may affect users briefly
- high: Significant risk, requires careful execution
- critical: Major risk, requires approval and careful planning

Always respond with valid JSON."""

SUGGESTION_USER_PROMPT = """Generate resolution suggestions for this incident:

Title: {title}

Description: {description}

Classification:
- Category: {category}
- Subcategory: {subcategory}
- Severity: {severity}
- Priority: {priority}

Affected Services: {affected_services}

Current Status: {status}

Respond with JSON in this exact format:
{{
    "summary": "Brief summary of recommended resolution approach",
    "steps": [
        "Step 1: First action to take",
        "Step 2: Second action to take",
        "Step 3: Continue with numbered steps...",
        "Step N: Verify resolution and monitor"
    ],
    "estimated_time": "e.g., '15-30 minutes' or '1-2 hours'",
    "risk_level": "low/medium/high/critical",
    "requires_approval": true/false,
    "automation_possible": true/false,
    "related_runbooks": ["runbook-1", "runbook-2"],
    "confidence": 0.0 to 1.0
}}"""


class ResolutionSuggester:
    """AI-powered resolution suggester using Mistral."""

    def __init__(self, client: Optional[MistralClient] = None):
        self.client = client

    async def suggest(
        self,
        title: str,
        description: str = "",
        category: str = "other",
        subcategory: str = "general",
        severity: str = "medium",
        priority: str = "p3",
        affected_services: List[str] = None,
        status: str = "open",
    ) -> ResolutionSuggestion:
        """
        Generate resolution suggestions for an incident.

        Args:
            title: Incident title
            description: Incident description
            category: Incident category
            subcategory: Incident subcategory
            severity: Incident severity
            priority: Incident priority
            affected_services: List of affected services
            status: Current incident status

        Returns:
            ResolutionSuggestion with steps, estimated time, etc.
        """
        if not settings.AI_SUGGESTION_ENABLED:
            return self._default_suggestion()

        if not settings.MISTRAL_API_KEY:
            logger.warning("Mistral API key not configured, using default suggestion")
            return self._default_suggestion()

        prompt = SUGGESTION_USER_PROMPT.format(
            title=title,
            description=description or "No description provided",
            category=category,
            subcategory=subcategory,
            severity=severity,
            priority=priority,
            affected_services=", ".join(affected_services or []) or "Unknown",
            status=status,
        )

        try:
            client = self.client or MistralClient()
            async with client:
                result = await client.generate_json(
                    prompt=prompt,
                    system_prompt=SUGGESTION_SYSTEM_PROMPT,
                    temperature=0.3,
                    max_tokens=2048,
                )

            return self._parse_suggestion(result)

        except Exception as e:
            logger.error(f"AI suggestion generation failed: {str(e)}")
            return self._default_suggestion()

    def _parse_suggestion(self, result: Dict[str, Any]) -> ResolutionSuggestion:
        """Parse and validate AI suggestion response."""
        # Normalize risk level
        risk_level = result.get("risk_level", "medium").lower()
        if risk_level not in ["low", "medium", "high", "critical"]:
            risk_level = "medium"

        # Ensure confidence is valid
        confidence = float(result.get("confidence", 0.5))
        confidence = max(0.0, min(1.0, confidence))

        # Ensure steps is a list
        steps = result.get("steps", [])
        if not isinstance(steps, list):
            steps = [str(steps)]

        return ResolutionSuggestion(
            summary=result.get("summary", "Review incident and investigate"),
            steps=steps,
            estimated_time=result.get("estimated_time", "Unknown"),
            risk_level=risk_level,
            requires_approval=bool(result.get("requires_approval", False)),
            automation_possible=bool(result.get("automation_possible", False)),
            related_runbooks=result.get("related_runbooks", []),
            confidence=confidence,
        )

    def _default_suggestion(self) -> ResolutionSuggestion:
        """Return default suggestion when AI is unavailable."""
        return ResolutionSuggestion(
            summary="Manual investigation required",
            steps=[
                "1. Review incident details and gather more information",
                "2. Check monitoring dashboards for related alerts",
                "3. Review recent changes that might be related",
                "4. Engage relevant team members if needed",
                "5. Document findings and resolution steps",
            ],
            estimated_time="Varies",
            risk_level="medium",
            requires_approval=False,
            automation_possible=False,
            related_runbooks=[],
            confidence=0.0,
        )

    def format_as_text(self, suggestion: ResolutionSuggestion) -> str:
        """Format suggestion as human-readable text."""
        lines = [
            f"**Summary:** {suggestion.summary}",
            "",
            "**Resolution Steps:**",
        ]

        for i, step in enumerate(suggestion.steps, 1):
            # Remove existing numbering if present
            step_text = step.lstrip("0123456789.-) ")
            lines.append(f"{i}. {step_text}")

        lines.extend([
            "",
            f"**Estimated Time:** {suggestion.estimated_time}",
            f"**Risk Level:** {suggestion.risk_level.upper()}",
            f"**Requires Approval:** {'Yes' if suggestion.requires_approval else 'No'}",
            f"**Automation Possible:** {'Yes' if suggestion.automation_possible else 'No'}",
        ])

        if suggestion.related_runbooks:
            lines.append(f"**Related Runbooks:** {', '.join(suggestion.related_runbooks)}")

        lines.append(f"\n*AI Confidence: {suggestion.confidence:.0%}*")

        return "\n".join(lines)

    def to_dict(self, suggestion: ResolutionSuggestion) -> Dict[str, Any]:
        """Convert suggestion to dictionary for storage."""
        return {
            "summary": suggestion.summary,
            "steps": suggestion.steps,
            "estimated_time": suggestion.estimated_time,
            "risk_level": suggestion.risk_level,
            "requires_approval": suggestion.requires_approval,
            "automation_possible": suggestion.automation_possible,
            "related_runbooks": suggestion.related_runbooks,
            "confidence": suggestion.confidence,
        }
