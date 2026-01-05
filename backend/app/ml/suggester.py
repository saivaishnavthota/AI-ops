"""
Resolution Suggester using Anthropic Claude AI

Generates intelligent resolution suggestions for incidents based on:
- Incident details (title, description, category)
- Historical patterns
- Best practices knowledge
"""

import logging
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .client import AnthropicClient
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
    """AI-powered resolution suggester using Anthropic Claude."""

    def __init__(self, client: Optional[AnthropicClient] = None):
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
            return self._default_suggestion(title, description, category, subcategory, severity)

        if not settings.ANTHROPIC_API_KEY:
            logger.info("Using mock AI suggestions (no API key configured)")
            return self._default_suggestion(title, description, category, subcategory, severity)

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
            client = self.client or AnthropicClient()
            async with client:
                result = await client.generate_json(
                    prompt=prompt,
                    system_prompt=SUGGESTION_SYSTEM_PROMPT,
                    temperature=0.3,
                    max_tokens=2048,
                )

            return self._parse_suggestion(result)

        except Exception as e:
            logger.error(f"AI suggestion generation failed: {str(e)}, falling back to mock")
            return self._default_suggestion(title, description, category, subcategory, severity)

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

    def _default_suggestion(
        self,
        title: str = "",
        description: str = "",
        category: str = "other",
        subcategory: str = "general",
        severity: str = "medium",
    ) -> ResolutionSuggestion:
        """
        Return smart mock suggestion based on category when AI is unavailable.
        Provides realistic demo behavior with category-specific resolution steps.
        """
        # Category-specific resolution templates
        category_suggestions = {
            "database": {
                "connection": {
                    "summary": "Resolve database connection pool exhaustion",
                    "steps": [
                        "Check current connection pool usage: SELECT count(*) FROM pg_stat_activity",
                        "Identify long-running queries: SELECT * FROM pg_stat_activity WHERE state != 'idle'",
                        "Terminate idle connections if needed: SELECT pg_terminate_backend(pid)",
                        "Increase connection pool size in application configuration",
                        "Restart application pods to apply new connection settings",
                        "Monitor connection pool metrics for 15 minutes",
                    ],
                    "estimated_time": "15-30 minutes",
                    "risk_level": "medium",
                    "requires_approval": False,
                    "automation_possible": True,
                    "runbooks": ["database-connection-pool", "app-restart"],
                },
                "performance": {
                    "summary": "Optimize database query performance",
                    "steps": [
                        "Identify slow queries using pg_stat_statements or slow query log",
                        "Analyze query execution plan with EXPLAIN ANALYZE",
                        "Check for missing indexes on frequently queried columns",
                        "Review table statistics and run ANALYZE if needed",
                        "Consider query optimization or adding appropriate indexes",
                        "Test changes in staging before applying to production",
                    ],
                    "estimated_time": "30-60 minutes",
                    "risk_level": "low",
                    "requires_approval": False,
                    "automation_possible": False,
                    "runbooks": ["database-performance-tuning"],
                },
                "replication": {
                    "summary": "Address database replication lag",
                    "steps": [
                        "Check replication status: SELECT * FROM pg_stat_replication",
                        "Verify network connectivity between primary and replica",
                        "Check replica disk I/O and CPU usage",
                        "Review write-heavy queries that might be causing lag",
                        "Consider increasing wal_sender_timeout if network is slow",
                        "Monitor replication lag metrics after changes",
                    ],
                    "estimated_time": "20-45 minutes",
                    "risk_level": "medium",
                    "requires_approval": True,
                    "automation_possible": False,
                    "runbooks": ["database-replication-troubleshooting"],
                },
            },
            "infrastructure": {
                "compute": {
                    "summary": "Resolve high CPU utilization",
                    "steps": [
                        "Identify top CPU-consuming processes: top -c or htop",
                        "Check for runaway processes or infinite loops",
                        "Review application logs for errors or unusual activity",
                        "Scale horizontally if legitimate traffic increase",
                        "Consider vertical scaling if consistent high usage",
                        "Set up CPU usage alerts for early warning",
                    ],
                    "estimated_time": "15-30 minutes",
                    "risk_level": "low",
                    "requires_approval": False,
                    "automation_possible": True,
                    "runbooks": ["cpu-troubleshooting", "horizontal-scaling"],
                },
                "memory": {
                    "summary": "Address memory exhaustion issue",
                    "steps": [
                        "Check current memory usage: free -h or top",
                        "Identify memory-heavy processes: ps aux --sort=-%mem | head",
                        "Look for memory leaks in application logs",
                        "Clear caches if safe: sync && echo 3 > /proc/sys/vm/drop_caches",
                        "Restart problematic application if memory leak confirmed",
                        "Consider increasing instance memory or optimizing application",
                    ],
                    "estimated_time": "20-40 minutes",
                    "risk_level": "medium",
                    "requires_approval": True,
                    "automation_possible": True,
                    "runbooks": ["memory-troubleshooting", "service-restart"],
                },
                "storage": {
                    "summary": "Free up disk space",
                    "steps": [
                        "Check disk usage: df -h and du -sh /* | sort -hr | head",
                        "Identify large files and old logs to clean up",
                        "Rotate and compress old log files: logrotate -f /etc/logrotate.conf",
                        "Remove old Docker images: docker system prune -af",
                        "Clean up temporary files: find /tmp -type f -mtime +7 -delete",
                        "Consider expanding disk volume if cleanup insufficient",
                    ],
                    "estimated_time": "10-20 minutes",
                    "risk_level": "low",
                    "requires_approval": False,
                    "automation_possible": True,
                    "runbooks": ["disk-cleanup", "log-rotation"],
                },
                "container": {
                    "summary": "Resolve container/pod issues",
                    "steps": [
                        "Check pod status: kubectl get pods -o wide",
                        "View pod logs: kubectl logs <pod-name> --tail=100",
                        "Describe pod for events: kubectl describe pod <pod-name>",
                        "Check resource limits and current usage",
                        "Restart pod if stuck: kubectl delete pod <pod-name>",
                        "Review deployment configuration for issues",
                    ],
                    "estimated_time": "10-25 minutes",
                    "risk_level": "low",
                    "requires_approval": False,
                    "automation_possible": True,
                    "runbooks": ["kubernetes-troubleshooting"],
                },
            },
            "network": {
                "connectivity": {
                    "summary": "Diagnose and resolve network connectivity issues",
                    "steps": [
                        "Test basic connectivity: ping <target-host>",
                        "Check DNS resolution: nslookup <hostname>",
                        "Trace network path: traceroute <target>",
                        "Verify firewall rules: iptables -L -n",
                        "Check security groups and network ACLs in cloud console",
                        "Review recent network configuration changes",
                    ],
                    "estimated_time": "15-30 minutes",
                    "risk_level": "low",
                    "requires_approval": False,
                    "automation_possible": True,
                    "runbooks": ["network-diagnostics"],
                },
                "loadbalancer": {
                    "summary": "Troubleshoot load balancer issues",
                    "steps": [
                        "Check load balancer health checks status",
                        "Verify backend instances are healthy and responding",
                        "Review load balancer access logs for errors",
                        "Check SSL certificate validity if HTTPS",
                        "Verify listener and target group configuration",
                        "Test direct connectivity to backend instances",
                    ],
                    "estimated_time": "20-40 minutes",
                    "risk_level": "medium",
                    "requires_approval": False,
                    "automation_possible": False,
                    "runbooks": ["loadbalancer-troubleshooting"],
                },
            },
            "application": {
                "error": {
                    "summary": "Investigate and resolve application errors",
                    "steps": [
                        "Check application logs for error stack traces",
                        "Review recent deployments that might have introduced bugs",
                        "Check external dependencies (databases, APIs) status",
                        "Verify environment variables and configuration",
                        "Roll back to previous version if recent deployment caused issue",
                        "Monitor error rates after fix is applied",
                    ],
                    "estimated_time": "20-45 minutes",
                    "risk_level": "medium",
                    "requires_approval": True,
                    "automation_possible": True,
                    "runbooks": ["application-debugging", "rollback-deployment"],
                },
                "performance": {
                    "summary": "Improve application response time",
                    "steps": [
                        "Check APM dashboard for slow transactions",
                        "Profile application to identify bottlenecks",
                        "Review database query performance",
                        "Check cache hit rates and effectiveness",
                        "Analyze external API response times",
                        "Consider scaling or optimization based on findings",
                    ],
                    "estimated_time": "30-60 minutes",
                    "risk_level": "low",
                    "requires_approval": False,
                    "automation_possible": False,
                    "runbooks": ["performance-optimization"],
                },
                "availability": {
                    "summary": "Restore service availability",
                    "steps": [
                        "Check service health endpoints",
                        "Review pod/container status and logs",
                        "Verify dependencies are available",
                        "Restart service if stuck or unresponsive",
                        "Check for resource exhaustion (CPU, memory, connections)",
                        "Monitor recovery and set up availability alerts",
                    ],
                    "estimated_time": "10-30 minutes",
                    "risk_level": "medium",
                    "requires_approval": False,
                    "automation_possible": True,
                    "runbooks": ["service-recovery", "health-check"],
                },
            },
            "security": {
                "access": {
                    "summary": "Investigate unauthorized access attempt",
                    "steps": [
                        "Review authentication logs for suspicious activity",
                        "Check source IP addresses and geolocations",
                        "Verify if compromised credentials were used",
                        "Temporarily block suspicious IP addresses",
                        "Reset passwords for affected accounts",
                        "Enable additional security measures (MFA) if not already",
                        "Document incident for security review",
                    ],
                    "estimated_time": "30-60 minutes",
                    "risk_level": "high",
                    "requires_approval": True,
                    "automation_possible": False,
                    "runbooks": ["security-incident-response"],
                },
                "vulnerability": {
                    "summary": "Address security vulnerability",
                    "steps": [
                        "Assess vulnerability severity and potential impact",
                        "Check if vulnerability is being actively exploited",
                        "Apply security patches or workarounds",
                        "Update affected dependencies or components",
                        "Scan for indicators of compromise",
                        "Schedule follow-up security review",
                    ],
                    "estimated_time": "1-4 hours",
                    "risk_level": "high",
                    "requires_approval": True,
                    "automation_possible": False,
                    "runbooks": ["vulnerability-management", "patch-management"],
                },
            },
            "capacity": {
                "scaling": {
                    "summary": "Scale resources to handle increased load",
                    "steps": [
                        "Review current resource utilization metrics",
                        "Analyze traffic patterns and growth trends",
                        "Scale horizontally: kubectl scale deployment <name> --replicas=<n>",
                        "Verify new instances are healthy and receiving traffic",
                        "Update auto-scaling policies if needed",
                        "Monitor performance after scaling",
                    ],
                    "estimated_time": "10-20 minutes",
                    "risk_level": "low",
                    "requires_approval": False,
                    "automation_possible": True,
                    "runbooks": ["horizontal-scaling", "autoscaling-config"],
                },
                "quota": {
                    "summary": "Address resource quota or limit exhaustion",
                    "steps": [
                        "Identify which quota/limit was exceeded",
                        "Review resource usage trends",
                        "Request quota increase from cloud provider if needed",
                        "Optimize resource usage to stay within limits",
                        "Implement resource cleanup policies",
                        "Set up alerts for quota approaching limits",
                    ],
                    "estimated_time": "15-45 minutes",
                    "risk_level": "low",
                    "requires_approval": True,
                    "automation_possible": False,
                    "runbooks": ["quota-management"],
                },
            },
        }

        # Get category-specific suggestions
        cat_suggestions = category_suggestions.get(category, {})
        subcat_suggestion = cat_suggestions.get(subcategory, cat_suggestions.get("general", None))

        # Fall back to default if no specific suggestion
        if not subcat_suggestion:
            # Generate a generic but contextual suggestion
            text = f"{title} {description}".lower()

            return ResolutionSuggestion(
                summary=f"Investigate and resolve {category} issue",
                steps=[
                    f"1. Review incident details: {title[:50]}...",
                    "2. Check monitoring dashboards for related metrics and alerts",
                    "3. Review recent changes (deployments, config updates) in the timeframe",
                    "4. Check system logs for errors or warnings",
                    "5. Engage subject matter experts if needed",
                    "6. Document findings and apply fix",
                    "7. Verify resolution and monitor for recurrence",
                ],
                estimated_time="30-60 minutes",
                risk_level="medium" if severity != "critical" else "high",
                requires_approval=severity in ["critical", "high"],
                automation_possible=False,
                related_runbooks=[f"{category}-troubleshooting"],
                confidence=0.75,
            )

        # Adjust risk and approval based on severity
        risk_level = subcat_suggestion["risk_level"]
        requires_approval = subcat_suggestion["requires_approval"]

        if severity == "critical":
            risk_level = "high" if risk_level in ["low", "medium"] else risk_level
            requires_approval = True

        return ResolutionSuggestion(
            summary=subcat_suggestion["summary"],
            steps=subcat_suggestion["steps"],
            estimated_time=subcat_suggestion["estimated_time"],
            risk_level=risk_level,
            requires_approval=requires_approval,
            automation_possible=subcat_suggestion["automation_possible"],
            related_runbooks=subcat_suggestion["runbooks"],
            confidence=0.88,  # High confidence for category-matched suggestions
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
