"""
Incident Classifier using Anthropic Claude AI

Automatically classifies incidents based on title and description into:
- Category (infrastructure, application, security, network, database, etc.)
- Subcategory (more specific classification)
- Priority suggestion
- Severity assessment
"""

import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass

from .client import AnthropicClient
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
    """AI-powered incident classifier using Anthropic Claude."""

    def __init__(self, client: Optional[AnthropicClient] = None):
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
            return self._default_classification(title, description)

        if not settings.ANTHROPIC_API_KEY:
            logger.info("Using mock AI classification (no API key configured)")
            return self._default_classification(title, description)

        prompt = CLASSIFICATION_USER_PROMPT.format(
            title=title,
            description=description or "No description provided",
            affected_services=", ".join(affected_services or []) or "Unknown",
            tags=", ".join(tags or []) or "None",
            source=source,
        )

        try:
            client = self.client or AnthropicClient()
            async with client:
                result = await client.generate_json(
                    prompt=prompt,
                    system_prompt=CLASSIFICATION_SYSTEM_PROMPT,
                    temperature=0.1,
                )

            # Validate and normalize response
            return self._parse_classification(result)

        except Exception as e:
            logger.error(f"AI classification failed: {str(e)}, falling back to mock")
            return self._default_classification(title, description)

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

    def _default_classification(
        self,
        title: str = "",
        description: str = ""
    ) -> ClassificationResult:
        """
        Return smart mock classification based on keywords when AI is unavailable.
        This provides realistic demo behavior without requiring an API key.
        """
        text = f"{title} {description}".lower()

        # Keyword-based classification rules
        classification_rules = {
            "database": {
                "keywords": ["database", "db", "postgres", "mysql", "mongodb", "redis", "sql",
                            "query", "replication", "backup", "connection pool", "deadlock",
                            "slow query", "table lock", "index"],
                "subcategories": {
                    "connection": ["connection", "pool", "timeout"],
                    "performance": ["slow", "query", "performance", "latency"],
                    "replication": ["replication", "replica", "sync", "lag"],
                    "backup": ["backup", "restore", "recovery"],
                },
                "default_subcategory": "general",
            },
            "infrastructure": {
                "keywords": ["server", "cpu", "memory", "disk", "storage", "vm", "container",
                            "kubernetes", "k8s", "pod", "node", "cluster", "ec2", "instance",
                            "host", "hardware", "oom", "out of memory", "swap"],
                "subcategories": {
                    "compute": ["cpu", "processor", "compute", "cores"],
                    "memory": ["memory", "ram", "oom", "heap", "swap"],
                    "storage": ["disk", "storage", "volume", "space", "iops"],
                    "container": ["container", "docker", "kubernetes", "k8s", "pod"],
                },
                "default_subcategory": "general",
            },
            "network": {
                "keywords": ["network", "dns", "loadbalancer", "lb", "nginx", "haproxy",
                            "timeout", "latency", "packet", "firewall", "vpc", "subnet",
                            "routing", "gateway", "proxy", "ssl", "tls", "certificate"],
                "subcategories": {
                    "connectivity": ["connection", "timeout", "unreachable", "refused"],
                    "dns": ["dns", "resolve", "nameserver", "domain"],
                    "loadbalancer": ["loadbalancer", "lb", "nginx", "haproxy", "balancer"],
                    "security": ["firewall", "ssl", "tls", "certificate"],
                },
                "default_subcategory": "general",
            },
            "application": {
                "keywords": ["api", "error", "500", "503", "exception", "crash", "bug",
                            "deployment", "release", "service", "endpoint", "request",
                            "response", "http", "rest", "graphql", "microservice"],
                "subcategories": {
                    "error": ["error", "exception", "500", "503", "crash", "failed"],
                    "performance": ["slow", "latency", "timeout", "performance"],
                    "deployment": ["deploy", "release", "rollback", "version"],
                    "availability": ["down", "unavailable", "health", "outage"],
                },
                "default_subcategory": "general",
            },
            "security": {
                "keywords": ["security", "unauthorized", "breach", "attack", "vulnerability",
                            "cve", "exploit", "intrusion", "malware", "suspicious", "login",
                            "authentication", "permission", "access denied", "forbidden"],
                "subcategories": {
                    "access": ["unauthorized", "permission", "forbidden", "access denied"],
                    "vulnerability": ["vulnerability", "cve", "exploit", "patch"],
                    "attack": ["attack", "breach", "intrusion", "ddos", "malware"],
                    "audit": ["audit", "compliance", "policy"],
                },
                "default_subcategory": "general",
            },
            "monitoring": {
                "keywords": ["monitoring", "alert", "metric", "prometheus", "grafana",
                            "datadog", "newrelic", "apm", "logging", "trace", "observability"],
                "subcategories": {
                    "alerting": ["alert", "notification", "trigger"],
                    "metrics": ["metric", "prometheus", "grafana", "dashboard"],
                    "logging": ["log", "logging", "elk", "splunk"],
                },
                "default_subcategory": "general",
            },
            "capacity": {
                "keywords": ["capacity", "scale", "scaling", "quota", "limit", "exhausted",
                            "threshold", "burst", "traffic", "load", "spike"],
                "subcategories": {
                    "scaling": ["scale", "scaling", "autoscale"],
                    "quota": ["quota", "limit", "exhausted", "exceeded"],
                    "traffic": ["traffic", "load", "spike", "burst"],
                },
                "default_subcategory": "general",
            },
        }

        # Severity keywords
        severity_rules = {
            "critical": ["critical", "outage", "down", "crash", "breach", "data loss",
                        "production down", "complete failure", "security breach"],
            "high": ["high", "major", "severe", "urgent", "degraded", "impacted",
                    "failing", "error rate", "spike"],
            "medium": ["medium", "moderate", "elevated", "warning", "increased"],
            "low": ["low", "minor", "informational", "notice"],
        }

        # Priority keywords
        priority_rules = {
            "p1": ["critical", "outage", "emergency", "production down", "data loss"],
            "p2": ["high", "major", "urgent", "severely", "significant"],
            "p3": ["medium", "moderate", "impacting"],
            "p4": ["low", "minor", "cosmetic"],
            "p5": ["planning", "enhancement", "feature request"],
        }

        # Determine category
        detected_category = "other"
        max_matches = 0
        detected_subcategory = "general"
        detected_keywords = []

        for category, rules in classification_rules.items():
            matches = sum(1 for kw in rules["keywords"] if kw in text)
            if matches > max_matches:
                max_matches = matches
                detected_category = category
                detected_keywords = [kw for kw in rules["keywords"] if kw in text][:5]

                # Determine subcategory
                for subcat, subcat_kws in rules.get("subcategories", {}).items():
                    if any(kw in text for kw in subcat_kws):
                        detected_subcategory = subcat
                        break
                else:
                    detected_subcategory = rules.get("default_subcategory", "general")

        # Determine severity
        detected_severity = "medium"
        for severity, keywords in severity_rules.items():
            if any(kw in text for kw in keywords):
                detected_severity = severity
                break

        # Determine priority
        detected_priority = "p3"
        for priority, keywords in priority_rules.items():
            if any(kw in text for kw in keywords):
                detected_priority = priority
                break

        # Adjust priority based on severity
        if detected_severity == "critical" and detected_priority not in ["p1"]:
            detected_priority = "p1"
        elif detected_severity == "high" and detected_priority not in ["p1", "p2"]:
            detected_priority = "p2"

        # Extract affected components from text
        component_patterns = [
            "api", "database", "server", "service", "cache", "queue",
            "loadbalancer", "gateway", "cluster", "node", "pod"
        ]
        affected_components = [c for c in component_patterns if c in text][:3]

        # Calculate confidence based on matches
        confidence = min(0.95, 0.70 + (max_matches * 0.05)) if max_matches > 0 else 0.50

        # Generate reasoning
        if max_matches > 0:
            reasoning = f"Mock AI classified as {detected_category}/{detected_subcategory} based on keywords: {', '.join(detected_keywords[:3])}"
        else:
            reasoning = "Mock AI classification - no specific keywords detected, using defaults"

        return ClassificationResult(
            category=detected_category,
            subcategory=detected_subcategory,
            suggested_priority=detected_priority,
            suggested_severity=detected_severity,
            confidence=confidence,
            reasoning=reasoning,
            keywords=detected_keywords,
            affected_components=affected_components,
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
