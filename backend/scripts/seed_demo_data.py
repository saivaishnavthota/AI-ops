#!/usr/bin/env python3
"""
Seed Demo Data Script for AI-Ops Platform

This script generates realistic demo data for showcasing the platform to team leads.
Run with: python -m scripts.seed_demo_data

Demo Users Created:
- super.admin@demo.com (Super Admin)
- admin@demo.com (Admin)
- operator@demo.com (Operator)
- operator2@demo.com (Operator)
- viewer@demo.com (Viewer)
- viewer2@demo.com (Viewer)

All users have password: Demo@123!
"""

import asyncio
import uuid
import random
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Dict, Any

# Add parent directory to path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

# Compatibility: Use sessionmaker with class_=AsyncSession for older SQLAlchemy
try:
    from sqlalchemy.ext.asyncio import async_sessionmaker
except ImportError:
    # For SQLAlchemy < 2.0, use sessionmaker with AsyncSession
    async_sessionmaker = lambda bind, **kwargs: sessionmaker(bind=bind, **kwargs)

from app.config.settings import settings
from app.core.security import get_password_hash
from app.models.base import Base
from app.models.organization import Organization
from app.models.user import User, UserRole
from app.models.team import Team, TeamMember
from app.models.incident import Incident, IncidentComment, IncidentTimeline
from app.models.alert import Alert, AlertCorrelation, AlertSource
from app.models.playbook import Playbook, PlaybookExecution
from app.models.notification import Notification, NotificationType, NotificationPriority
from app.models.audit import AuditLog


# Constants
DEMO_PASSWORD = "Demo@123!"
ORGANIZATION_NAME = "TechOps Demo Company"
ORGANIZATION_SLUG = "techops-demo"

# Realistic server names
SERVERS = [
    "api-server-01", "api-server-02", "api-server-03",
    "web-server-01", "web-server-02", "web-server-03",
    "db-primary-01", "db-replica-01", "db-replica-02",
    "cache-redis-01", "cache-redis-02",
    "queue-rabbitmq-01", "queue-rabbitmq-02",
    "search-elastic-01", "search-elastic-02",
    "lb-nginx-01", "lb-nginx-02",
    "monitor-prometheus-01", "log-elastic-01",
]

# Realistic services
SERVICES = [
    "payment-api", "auth-service", "user-service", "notification-service",
    "order-service", "inventory-service", "search-api", "recommendation-engine",
    "checkout-service", "cart-api", "product-catalog", "image-processor",
    "email-service", "sms-gateway", "analytics-pipeline", "reporting-service",
]

# Incident templates for realistic data
INCIDENT_TEMPLATES = [
    {
        "title": "High CPU utilization on {server}",
        "description": "CPU usage has exceeded 90% on {server} for more than 15 minutes. This is causing slow response times for the {service} service.",
        "category": "infrastructure",
        "subcategory": "compute",
        "severity": "high",
        "priority": "p2",
        "tags": ["cpu", "performance", "infrastructure"],
    },
    {
        "title": "Memory leak detected in {service}",
        "description": "Memory usage for {service} has been steadily increasing. Current heap size is at 85% and growing. Restart may be required.",
        "category": "application",
        "subcategory": "memory",
        "severity": "high",
        "priority": "p2",
        "tags": ["memory", "leak", "application"],
    },
    {
        "title": "Database connection pool exhausted on {server}",
        "description": "All database connections in the pool are currently in use on {server}. New requests are failing with connection timeout errors.",
        "category": "database",
        "subcategory": "connection",
        "severity": "critical",
        "priority": "p1",
        "tags": ["database", "connection", "critical"],
    },
    {
        "title": "SSL certificate expiring in 7 days for {service}",
        "description": "The SSL certificate for {service}.techops.com will expire on {date}. Please renew before expiration to prevent service disruption.",
        "category": "security",
        "subcategory": "certificate",
        "severity": "medium",
        "priority": "p3",
        "tags": ["ssl", "certificate", "security"],
    },
    {
        "title": "Disk space critical on {server}",
        "description": "Disk utilization on {server} has reached 92%. Log rotation and cleanup required urgently.",
        "category": "infrastructure",
        "subcategory": "storage",
        "severity": "high",
        "priority": "p2",
        "tags": ["disk", "storage", "cleanup"],
    },
    {
        "title": "API latency spike on {service}",
        "description": "P95 latency for {service} has increased from 150ms to 2500ms in the last 30 minutes. User complaints increasing.",
        "category": "application",
        "subcategory": "performance",
        "severity": "high",
        "priority": "p2",
        "tags": ["latency", "api", "performance"],
    },
    {
        "title": "Failed health checks for {service}",
        "description": "Health check endpoint for {service} is returning 503 status. Service appears to be down or unresponsive.",
        "category": "application",
        "subcategory": "availability",
        "severity": "critical",
        "priority": "p1",
        "tags": ["healthcheck", "downtime", "critical"],
    },
    {
        "title": "Replication lag on {server}",
        "description": "Database replication lag on {server} has exceeded 60 seconds. Read replicas may be serving stale data.",
        "category": "database",
        "subcategory": "replication",
        "severity": "medium",
        "priority": "p3",
        "tags": ["replication", "database", "lag"],
    },
    {
        "title": "Redis cache hit rate dropped for {service}",
        "description": "Cache hit rate for {service} has dropped from 95% to 45%. This is causing increased database load.",
        "category": "infrastructure",
        "subcategory": "cache",
        "severity": "medium",
        "priority": "p3",
        "tags": ["cache", "redis", "performance"],
    },
    {
        "title": "Unusual login activity detected for user account",
        "description": "Multiple failed login attempts detected from IP 185.234.xx.xx followed by successful login. Possible compromised account.",
        "category": "security",
        "subcategory": "access",
        "severity": "high",
        "priority": "p2",
        "tags": ["security", "login", "suspicious"],
    },
    {
        "title": "Kubernetes pod crash loop on {service}",
        "description": "Pod {service}-7d4f5c6b8-xyz is in CrashLoopBackOff state. Container restarted 15 times in the last hour.",
        "category": "infrastructure",
        "subcategory": "kubernetes",
        "severity": "high",
        "priority": "p2",
        "tags": ["kubernetes", "pod", "crash"],
    },
    {
        "title": "Message queue backlog growing on {server}",
        "description": "RabbitMQ queue backlog has grown to 50,000 messages. Consumer lag is increasing. May impact order processing.",
        "category": "infrastructure",
        "subcategory": "messaging",
        "severity": "medium",
        "priority": "p3",
        "tags": ["queue", "rabbitmq", "backlog"],
    },
]

# Alert templates
ALERT_TEMPLATES = [
    {
        "title": "High CPU Usage Alert",
        "message": "CPU usage exceeded threshold on {host}",
        "source": "prometheus",
        "severity": "critical",
        "metric_name": "node_cpu_usage_percent",
    },
    {
        "title": "Memory Usage Warning",
        "message": "Memory usage at {value}% on {host}",
        "source": "datadog",
        "severity": "warning",
        "metric_name": "system.mem.used_percent",
    },
    {
        "title": "Disk Space Critical",
        "message": "Disk space usage exceeded 90% on {host}",
        "source": "prometheus",
        "severity": "critical",
        "metric_name": "node_disk_usage_percent",
    },
    {
        "title": "Service Health Check Failed",
        "message": "Health check failed for {service}",
        "source": "newrelic",
        "severity": "critical",
        "metric_name": "service.health.status",
    },
    {
        "title": "High Error Rate",
        "message": "Error rate exceeded 5% for {service}",
        "source": "datadog",
        "severity": "warning",
        "metric_name": "service.error_rate",
    },
    {
        "title": "Response Time Degradation",
        "message": "P99 latency exceeded 2s for {service}",
        "source": "newrelic",
        "severity": "warning",
        "metric_name": "service.latency.p99",
    },
    {
        "title": "Database Connection Pool Exhausted",
        "message": "No available connections in pool for {service}",
        "source": "prometheus",
        "severity": "critical",
        "metric_name": "db.pool.available",
    },
    {
        "title": "SSL Certificate Expiring Soon",
        "message": "SSL certificate for {service} expires in 7 days",
        "source": "prometheus",
        "severity": "warning",
        "metric_name": "ssl.cert.days_remaining",
    },
]

# Playbook templates
PLAYBOOK_TEMPLATES = [
    {
        "name": "Restart Service",
        "description": "Safely restart a service with health checks and rollback capability",
        "trigger_conditions": {"alert_type": "health_check_failed"},
        "steps": [
            {"type": "notification", "name": "Notify team", "config": {"channel": "slack", "message": "Starting service restart"}},
            {"type": "script", "name": "Pre-restart checks", "config": {"command": "systemctl status {service}"}},
            {"type": "approval", "name": "Approval required", "config": {"roles": ["admin", "operator"]}},
            {"type": "script", "name": "Restart service", "config": {"command": "systemctl restart {service}"}},
            {"type": "wait", "name": "Wait for startup", "config": {"duration_seconds": 30}},
            {"type": "script", "name": "Verify health", "config": {"command": "curl -f http://localhost:8080/health"}},
            {"type": "notification", "name": "Complete", "config": {"channel": "slack", "message": "Service restart completed"}},
        ],
        "requires_approval": True,
        "tags": ["restart", "service", "recovery"],
    },
    {
        "name": "Clear Disk Space",
        "description": "Automated cleanup of log files and temporary data to free disk space",
        "trigger_conditions": {"metric": "disk_usage", "threshold": 90},
        "steps": [
            {"type": "script", "name": "Check disk usage", "config": {"command": "df -h"}},
            {"type": "script", "name": "Rotate logs", "config": {"command": "logrotate -f /etc/logrotate.conf"}},
            {"type": "script", "name": "Clear temp files", "config": {"command": "find /tmp -type f -mtime +7 -delete"}},
            {"type": "script", "name": "Clear old containers", "config": {"command": "docker system prune -f"}},
            {"type": "script", "name": "Verify cleanup", "config": {"command": "df -h"}},
        ],
        "requires_approval": False,
        "tags": ["disk", "cleanup", "maintenance"],
    },
    {
        "name": "Scale Application Horizontally",
        "description": "Increase the number of application instances to handle increased load",
        "trigger_conditions": {"metric": "cpu_usage", "threshold": 80},
        "steps": [
            {"type": "script", "name": "Check current replicas", "config": {"command": "kubectl get deployment {service} -o jsonpath='{.spec.replicas}'"}},
            {"type": "approval", "name": "Scale approval", "config": {"roles": ["admin"]}},
            {"type": "script", "name": "Scale up", "config": {"command": "kubectl scale deployment {service} --replicas={replicas}"}},
            {"type": "wait", "name": "Wait for pods", "config": {"duration_seconds": 60}},
            {"type": "script", "name": "Verify scale", "config": {"command": "kubectl get pods -l app={service}"}},
        ],
        "requires_approval": True,
        "tags": ["scaling", "kubernetes", "performance"],
    },
    {
        "name": "Database Failover",
        "description": "Promote replica to primary in case of database primary failure",
        "trigger_conditions": {"alert_type": "database_primary_down"},
        "steps": [
            {"type": "notification", "name": "Alert team", "config": {"channel": "pagerduty", "message": "Database failover initiated"}},
            {"type": "script", "name": "Check replica status", "config": {"command": "pg_isready -h replica-host"}},
            {"type": "approval", "name": "Failover approval", "config": {"roles": ["admin"]}},
            {"type": "script", "name": "Promote replica", "config": {"command": "pg_ctl promote -D /var/lib/postgresql/data"}},
            {"type": "script", "name": "Update DNS", "config": {"command": "update-dns.sh db-primary replica-host"}},
            {"type": "script", "name": "Verify connections", "config": {"command": "psql -c 'SELECT 1'"}},
        ],
        "requires_approval": True,
        "tags": ["database", "failover", "disaster-recovery"],
    },
    {
        "name": "SSL Certificate Renewal",
        "description": "Automated SSL certificate renewal using Let's Encrypt",
        "trigger_conditions": {"metric": "ssl_days_remaining", "threshold": 14},
        "steps": [
            {"type": "script", "name": "Check certificate", "config": {"command": "certbot certificates"}},
            {"type": "script", "name": "Renew certificate", "config": {"command": "certbot renew --nginx"}},
            {"type": "script", "name": "Reload nginx", "config": {"command": "systemctl reload nginx"}},
            {"type": "script", "name": "Verify renewal", "config": {"command": "openssl s_client -connect {domain}:443 -servername {domain} < /dev/null 2>/dev/null | openssl x509 -noout -dates"}},
        ],
        "requires_approval": False,
        "tags": ["ssl", "certificate", "security"],
    },
    {
        "name": "Cache Flush and Warmup",
        "description": "Clear Redis cache and pre-populate with frequently accessed data",
        "trigger_conditions": {"alert_type": "cache_hit_rate_low"},
        "steps": [
            {"type": "notification", "name": "Notify team", "config": {"channel": "slack", "message": "Cache flush starting"}},
            {"type": "script", "name": "Check cache stats", "config": {"command": "redis-cli info stats"}},
            {"type": "script", "name": "Flush cache", "config": {"command": "redis-cli FLUSHDB"}},
            {"type": "script", "name": "Warmup cache", "config": {"command": "python cache_warmup.py"}},
            {"type": "script", "name": "Verify hit rate", "config": {"command": "redis-cli info stats | grep hit"}},
        ],
        "requires_approval": False,
        "tags": ["cache", "redis", "performance"],
    },
    {
        "name": "Rollback Deployment",
        "description": "Rollback to previous deployment version if issues detected",
        "trigger_conditions": {"alert_type": "high_error_rate"},
        "steps": [
            {"type": "notification", "name": "Alert team", "config": {"channel": "slack", "message": "Rollback initiated due to high error rate"}},
            {"type": "script", "name": "Get rollback revision", "config": {"command": "kubectl rollout history deployment/{service}"}},
            {"type": "approval", "name": "Rollback approval", "config": {"roles": ["admin", "operator"]}},
            {"type": "script", "name": "Execute rollback", "config": {"command": "kubectl rollout undo deployment/{service}"}},
            {"type": "wait", "name": "Wait for rollout", "config": {"duration_seconds": 120}},
            {"type": "script", "name": "Verify rollback", "config": {"command": "kubectl rollout status deployment/{service}"}},
            {"type": "notification", "name": "Complete", "config": {"channel": "slack", "message": "Rollback completed successfully"}},
        ],
        "requires_approval": True,
        "tags": ["deployment", "rollback", "recovery"],
    },
    {
        "name": "Network Diagnostics",
        "description": "Run comprehensive network diagnostics to identify connectivity issues",
        "trigger_conditions": {"alert_type": "network_timeout"},
        "steps": [
            {"type": "script", "name": "DNS lookup", "config": {"command": "dig {domain}"}},
            {"type": "script", "name": "Traceroute", "config": {"command": "traceroute {host}"}},
            {"type": "script", "name": "Port connectivity", "config": {"command": "nc -zv {host} {port}"}},
            {"type": "script", "name": "Check firewall", "config": {"command": "iptables -L -n"}},
            {"type": "script", "name": "Check routes", "config": {"command": "ip route show"}},
        ],
        "requires_approval": False,
        "tags": ["network", "diagnostics", "troubleshooting"],
    },
]

# Comment templates for realistic discussions
COMMENT_TEMPLATES = [
    "I'm investigating this issue now. Initial analysis shows {finding}.",
    "Checked the logs on {server}. Found error: {error}. Working on a fix.",
    "This appears to be related to the deployment we did yesterday. Rolling back to verify.",
    "Escalating to the database team as this seems to be a connection pooling issue.",
    "Applied temporary fix by restarting the service. Monitoring for recurrence.",
    "Root cause identified: {cause}. Preparing permanent fix.",
    "Customer impact assessment: Approximately {num} users affected during the outage window.",
    "Post-mortem scheduled for tomorrow. Adding action items to prevent recurrence.",
    "Confirmed resolution. All metrics have returned to normal levels.",
    "Adding monitoring alert to catch this earlier next time.",
]

# Audit action types
AUDIT_ACTIONS = [
    ("create", "incident", "Created new incident"),
    ("update", "incident", "Updated incident status"),
    ("assign", "incident", "Assigned incident to team"),
    ("create", "alert", "Alert received from monitoring"),
    ("acknowledge", "alert", "Acknowledged alert"),
    ("resolve", "alert", "Resolved alert"),
    ("login", "user", "User logged in"),
    ("logout", "user", "User logged out"),
    ("create", "playbook", "Created new playbook"),
    ("execute", "playbook", "Executed playbook"),
    ("update", "team", "Updated team configuration"),
    ("create", "user", "Created new user"),
    ("update", "user", "Updated user profile"),
    ("update", "settings", "Updated organization settings"),
]


async def create_database_engine():
    """Create async database engine."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    return engine


async def seed_organization(session: AsyncSession) -> Organization:
    """Create demo organization."""
    org = Organization(
        id=uuid.uuid4(),
        name=ORGANIZATION_NAME,
        slug=ORGANIZATION_SLUG,
        description="Demo organization for showcasing AI-Ops Platform capabilities",
        subscription_tier="enterprise",
        is_active=True,
        settings={
            "timezone": "America/New_York",
            "date_format": "YYYY-MM-DD",
            "time_format": "HH:mm:ss",
            "incident_auto_acknowledge_minutes": 30,
            "alert_retention_days": 90,
            "enable_ai_features": True,
            "enable_auto_remediation": True,
            "notification_preferences": {
                "email": True,
                "slack": True,
                "webhook": True,
            },
        },
        features={
            "ai_classification": True,
            "ai_suggestions": True,
            "ai_correlation": True,
            "playbook_automation": True,
            "custom_dashboards": True,
            "advanced_analytics": True,
            "sso_enabled": True,
            "api_access": True,
        },
    )
    session.add(org)
    await session.flush()
    print(f"Created organization: {org.name}")
    return org


async def seed_users(session: AsyncSession, org_id: uuid.UUID) -> Dict[str, User]:
    """Create demo users with different roles."""
    users_data = [
        {
            "email": "super.admin@demo.com",
            "first_name": "Sarah",
            "last_name": "Mitchell",
            "role": UserRole.SUPER_ADMIN.value,
            "job_title": "Platform Administrator",
            "phone": "+1-555-0101",
        },
        {
            "email": "admin@demo.com",
            "first_name": "Michael",
            "last_name": "Chen",
            "role": UserRole.ADMIN.value,
            "job_title": "IT Operations Manager",
            "phone": "+1-555-0102",
        },
        {
            "email": "operator@demo.com",
            "first_name": "Emily",
            "last_name": "Rodriguez",
            "role": UserRole.OPERATOR.value,
            "job_title": "Senior SRE",
            "phone": "+1-555-0103",
        },
        {
            "email": "operator2@demo.com",
            "first_name": "James",
            "last_name": "Wilson",
            "role": UserRole.OPERATOR.value,
            "job_title": "DevOps Engineer",
            "phone": "+1-555-0104",
        },
        {
            "email": "viewer@demo.com",
            "first_name": "Amanda",
            "last_name": "Thompson",
            "role": UserRole.VIEWER.value,
            "job_title": "Support Analyst",
            "phone": "+1-555-0105",
        },
        {
            "email": "viewer2@demo.com",
            "first_name": "David",
            "last_name": "Kim",
            "role": UserRole.VIEWER.value,
            "job_title": "Technical Writer",
            "phone": "+1-555-0106",
        },
    ]

    password_hash = get_password_hash(DEMO_PASSWORD)
    users = {}

    for user_data in users_data:
        user = User(
            id=uuid.uuid4(),
            organization_id=org_id,
            email=user_data["email"],
            password_hash=password_hash,
            first_name=user_data["first_name"],
            last_name=user_data["last_name"],
            role=user_data["role"],
            job_title=user_data["job_title"],
            phone=user_data["phone"],
            is_active=True,
            is_verified=True,
            last_login=datetime.now(timezone.utc) - timedelta(hours=random.randint(1, 48)),
            preferences={
                "theme": random.choice(["light", "dark"]),
                "language": "en",
                "timezone": "America/New_York",
                "notifications": {
                    "email_incidents": True,
                    "email_alerts": user_data["role"] in ["super_admin", "admin", "operator"],
                    "browser_notifications": True,
                },
            },
        )
        session.add(user)
        users[user_data["role"]] = user
        users[user_data["email"]] = user

    await session.flush()
    print(f"Created {len(users_data)} users")
    return users


async def seed_teams(session: AsyncSession, org_id: uuid.UUID, users: Dict[str, User]) -> Dict[str, Team]:
    """Create demo teams."""
    teams_data = [
        {
            "name": "Infrastructure Team",
            "description": "Manages cloud infrastructure, servers, and networking",
            "team_type": "infrastructure",
        },
        {
            "name": "Application Support",
            "description": "Handles application-level incidents and deployments",
            "team_type": "devops",
        },
        {
            "name": "Security Operations",
            "description": "Security monitoring, incident response, and compliance",
            "team_type": "security",
        },
        {
            "name": "Database Administration",
            "description": "Database management, optimization, and disaster recovery",
            "team_type": "operations",
        },
    ]

    teams = {}
    for team_data in teams_data:
        team = Team(
            id=uuid.uuid4(),
            organization_id=org_id,
            name=team_data["name"],
            description=team_data["description"],
            team_type=team_data["team_type"],
            is_active=True,
            settings={
                "escalation_timeout_minutes": 30,
                "on_call_rotation": True,
            },
        )
        session.add(team)
        teams[team_data["name"]] = team

    await session.flush()
    print(f"Created {len(teams_data)} teams")
    return teams


async def seed_team_members(session: AsyncSession, teams: Dict[str, Team], users: Dict[str, User]) -> None:
    """Assign users to teams."""
    # Get specific users
    admin = users.get("admin@demo.com")
    operator = users.get("operator@demo.com")
    operator2 = users.get("operator2@demo.com")
    viewer = users.get("viewer@demo.com")
    viewer2 = users.get("viewer2@demo.com")

    memberships = [
        # Infrastructure Team
        (teams["Infrastructure Team"], admin, "lead", True),
        (teams["Infrastructure Team"], operator, "member", False),
        (teams["Infrastructure Team"], viewer, "member", False),

        # Application Support
        (teams["Application Support"], operator, "lead", True),
        (teams["Application Support"], operator2, "member", True),
        (teams["Application Support"], viewer2, "member", False),

        # Security Operations
        (teams["Security Operations"], admin, "lead", False),
        (teams["Security Operations"], operator2, "member", True),

        # Database Administration
        (teams["Database Administration"], operator, "lead", False),
        (teams["Database Administration"], operator2, "member", True),
    ]

    for team, user, role, is_on_call in memberships:
        member = TeamMember(
            id=uuid.uuid4(),
            team_id=team.id,
            user_id=user.id,
            role=role,
            is_on_call=is_on_call,
            notifications_enabled=True,
        )
        session.add(member)

    await session.flush()
    print(f"Created {len(memberships)} team memberships")


async def seed_incidents(
    session: AsyncSession,
    org_id: uuid.UUID,
    users: Dict[str, User],
    teams: Dict[str, Team]
) -> List[Incident]:
    """Create demo incidents spanning 30 days."""
    incidents = []
    now = datetime.now(timezone.utc)

    # Status distribution for realism
    status_weights = {
        "closed": 0.35,
        "resolved": 0.25,
        "in_progress": 0.20,
        "acknowledged": 0.10,
        "open": 0.10,
    }

    team_list = list(teams.values())
    operator_users = [users.get("operator@demo.com"), users.get("operator2@demo.com")]
    all_users = [users.get("admin@demo.com")] + operator_users

    for i in range(30):
        template = random.choice(INCIDENT_TEMPLATES)
        server = random.choice(SERVERS)
        service = random.choice(SERVICES)

        # Determine status with weighted probability
        rand = random.random()
        cumulative = 0
        status = "open"
        for s, weight in status_weights.items():
            cumulative += weight
            if rand <= cumulative:
                status = s
                break

        # Calculate timestamps based on status
        days_ago = random.randint(0, 30)
        created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))

        acknowledged_at = None
        resolved_at = None
        closed_at = None

        if status in ["acknowledged", "in_progress", "resolved", "closed"]:
            acknowledged_at = created_at + timedelta(minutes=random.randint(5, 60))

        if status in ["resolved", "closed"]:
            resolved_at = created_at + timedelta(hours=random.randint(1, 24))

        if status == "closed":
            closed_at = resolved_at + timedelta(hours=random.randint(1, 48))

        # Generate realistic AI classification
        ai_classification = {
            "category": template["category"],
            "subcategory": template["subcategory"],
            "confidence": round(random.uniform(0.85, 0.98), 2),
            "model": "mock-classifier-v1",
            "features": {
                "title_keywords": template["tags"][:2],
                "severity_indicator": template["severity"],
                "service_detected": service,
            },
        }

        incident = Incident(
            id=uuid.uuid4(),
            organization_id=org_id,
            incident_number=f"INC-{2024000 + i}",
            title=template["title"].format(server=server, service=service, date=(now + timedelta(days=7)).strftime("%Y-%m-%d")),
            description=template["description"].format(server=server, service=service, date=(now + timedelta(days=7)).strftime("%Y-%m-%d")),
            status=status,
            priority=template["priority"],
            severity=template["severity"],
            impact=random.choice(["high", "medium", "low"]),
            urgency=random.choice(["high", "medium", "low"]),
            category=template["category"],
            subcategory=template["subcategory"],
            assigned_team_id=random.choice(team_list).id,
            assigned_user_id=random.choice(operator_users).id if status != "open" else None,
            reported_by_id=random.choice(all_users).id,
            affected_services=[service, random.choice(SERVICES)] if random.random() > 0.5 else [service],
            business_impact_score=Decimal(str(round(random.uniform(1.0, 10.0), 2))),
            ai_classification=ai_classification,
            ai_suggested_resolution=f"1. Check {service} logs for errors\n2. Verify {server} resource utilization\n3. Restart service if necessary\n4. Monitor for 15 minutes",
            ai_confidence_score=Decimal(str(round(random.uniform(0.80, 0.95), 2))),
            root_cause="Configuration issue in load balancer settings" if status == "closed" else None,
            resolution_notes=f"Resolved by restarting {service} and adjusting resource limits" if status in ["resolved", "closed"] else None,
            acknowledged_at=acknowledged_at,
            resolved_at=resolved_at,
            closed_at=closed_at,
            tags=template["tags"],
            created_at=created_at,
        )
        session.add(incident)
        incidents.append(incident)

    await session.flush()
    print(f"Created {len(incidents)} incidents")
    return incidents


async def seed_incident_comments(session: AsyncSession, incidents: List[Incident], users: Dict[str, User]) -> None:
    """Create comments on incidents."""
    operator_users = [users.get("operator@demo.com"), users.get("operator2@demo.com"), users.get("admin@demo.com")]

    findings = ["high memory usage", "connection timeout errors", "permission denied errors", "resource exhaustion"]
    errors = ["OutOfMemoryError", "ConnectionTimeoutException", "PermissionDenied", "ResourceExhausted"]
    causes = ["memory leak in recent deployment", "misconfigured connection pool", "expired credentials", "insufficient resources"]

    comment_count = 0
    for incident in incidents:
        # Add 1-4 comments per incident
        num_comments = random.randint(1, 4)
        for j in range(num_comments):
            template = random.choice(COMMENT_TEMPLATES)
            content = template.format(
                finding=random.choice(findings),
                server=random.choice(SERVERS),
                error=random.choice(errors),
                cause=random.choice(causes),
                num=random.randint(50, 500),
            )

            comment_time = incident.created_at + timedelta(minutes=random.randint(5, 60) * (j + 1))

            comment = IncidentComment(
                id=uuid.uuid4(),
                incident_id=incident.id,
                user_id=random.choice(operator_users).id,
                content=content,
                is_internal=random.random() > 0.8,
                is_ai_generated=random.random() > 0.9,
                attachments=[],
                created_at=comment_time,
            )
            session.add(comment)
            comment_count += 1

    await session.flush()
    print(f"Created {comment_count} incident comments")


async def seed_incident_timeline(session: AsyncSession, incidents: List[Incident], users: Dict[str, User]) -> None:
    """Create timeline events for incidents."""
    event_count = 0

    for incident in incidents:
        # Created event
        timeline = IncidentTimeline(
            id=uuid.uuid4(),
            incident_id=incident.id,
            user_id=incident.reported_by_id,
            event_type="created",
            description="Incident created",
            is_automated=False,
            created_at=incident.created_at,
        )
        session.add(timeline)
        event_count += 1

        # AI classification event
        timeline = IncidentTimeline(
            id=uuid.uuid4(),
            incident_id=incident.id,
            user_id=None,
            event_type="ai_classified",
            description=f"AI classified as {incident.category}/{incident.subcategory}",
            is_automated=True,
            created_at=incident.created_at + timedelta(seconds=30),
        )
        session.add(timeline)
        event_count += 1

        if incident.acknowledged_at:
            timeline = IncidentTimeline(
                id=uuid.uuid4(),
                incident_id=incident.id,
                user_id=incident.assigned_user_id,
                event_type="acknowledged",
                description="Incident acknowledged",
                changes={"status": {"old": "open", "new": "acknowledged"}},
                is_automated=False,
                created_at=incident.acknowledged_at,
            )
            session.add(timeline)
            event_count += 1

        if incident.resolved_at:
            timeline = IncidentTimeline(
                id=uuid.uuid4(),
                incident_id=incident.id,
                user_id=incident.assigned_user_id,
                event_type="resolved",
                description="Incident resolved",
                changes={"status": {"old": "in_progress", "new": "resolved"}},
                is_automated=False,
                created_at=incident.resolved_at,
            )
            session.add(timeline)
            event_count += 1

    await session.flush()
    print(f"Created {event_count} timeline events")


async def seed_alerts(session: AsyncSession, org_id: uuid.UUID, incidents: List[Incident]) -> List[Alert]:
    """Create demo alerts."""
    alerts = []
    now = datetime.now(timezone.utc)

    status_distribution = ["firing"] * 20 + ["acknowledged"] * 15 + ["resolved"] * 60 + ["suppressed"] * 5

    for i in range(60):
        template = random.choice(ALERT_TEMPLATES)
        host = random.choice(SERVERS)
        service = random.choice(SERVICES)

        days_ago = random.randint(0, 30)
        created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))

        status = random.choice(status_distribution)

        metric_value = Decimal(str(round(random.uniform(75.0, 99.9), 2)))
        threshold_value = Decimal(str(round(random.uniform(70.0, 90.0), 2)))

        # Link some alerts to incidents
        incident_id = None
        if random.random() > 0.6 and incidents:
            incident_id = random.choice(incidents).id

        alert = Alert(
            id=uuid.uuid4(),
            organization_id=org_id,
            alert_id_external=f"ALT-{random.randint(100000, 999999)}",
            source=template["source"],
            source_type="metric",
            title=template["title"],
            message=template["message"].format(host=host, service=service, value=metric_value),
            severity=template["severity"],
            status=status,
            host=host,
            service=service,
            metric_name=template["metric_name"],
            metric_value=metric_value,
            threshold_value=threshold_value,
            tags={
                "environment": random.choice(["production", "staging"]),
                "region": random.choice(["us-east-1", "us-west-2", "eu-west-1"]),
                "team": random.choice(["infrastructure", "application", "security"]),
            },
            incident_id=incident_id,
            is_suppressed=status == "suppressed",
            suppression_reason="Maintenance window" if status == "suppressed" else None,
            ai_correlation_score=Decimal(str(round(random.uniform(0.5, 0.95), 2))) if incident_id else None,
            acknowledged_at=created_at + timedelta(minutes=random.randint(1, 30)) if status in ["acknowledged", "resolved"] else None,
            resolved_at=created_at + timedelta(hours=random.randint(1, 8)) if status == "resolved" else None,
            fingerprint=f"{host}:{service}:{template['metric_name']}",
            occurrence_count=random.randint(1, 10),
            first_occurrence_at=created_at - timedelta(hours=random.randint(0, 2)),
            last_occurrence_at=created_at,
            created_at=created_at,
        )
        session.add(alert)
        alerts.append(alert)

    await session.flush()
    print(f"Created {len(alerts)} alerts")
    return alerts


async def seed_alert_correlations(session: AsyncSession, alerts: List[Alert]) -> None:
    """Create alert correlation groups."""
    # Group alerts by service for correlation
    service_alerts = {}
    for alert in alerts:
        if alert.service not in service_alerts:
            service_alerts[alert.service] = []
        service_alerts[alert.service].append(alert)

    correlation_count = 0
    for service, service_alert_list in service_alerts.items():
        if len(service_alert_list) < 2:
            continue

        # Create a correlation group for related alerts
        group_id = uuid.uuid4()
        for i, alert in enumerate(service_alert_list[:5]):  # Max 5 alerts per group
            # Link each alert to the next one in the group
            if i < len(service_alert_list[:5]) - 1:
                related_alert = service_alert_list[i + 1]
            else:
                # Last alert links back to first
                related_alert = service_alert_list[0]
            
            correlation = AlertCorrelation(
                id=uuid.uuid4(),
                organization_id=alert.organization_id,
                correlation_group_id=group_id,
                alert_id=alert.id,
                related_alert_id=related_alert.id,
                correlation_type=random.choice(["temporal", "topological", "causal"]),
                confidence_score=Decimal(str(round(random.uniform(0.7, 0.95), 2))),
                correlation_reason=f"Alerts share same service: {service}",
                is_root_cause=i == 0,  # First alert is root cause
            )
            session.add(correlation)
            correlation_count += 1

    await session.flush()
    print(f"Created {correlation_count} alert correlations")


async def seed_alert_sources(session: AsyncSession, org_id: uuid.UUID) -> None:
    """Create alert source configurations."""
    sources = [
        {
            "name": "Prometheus Production",
            "source_type": "prometheus",
            "config": {"url": "http://prometheus.internal:9090", "scrape_interval": 15},
        },
        {
            "name": "Datadog Integration",
            "source_type": "datadog",
            "config": {"api_host": "https://api.datadoghq.com"},
        },
        {
            "name": "New Relic APM",
            "source_type": "newrelic",
            "config": {"account_id": "12345", "region": "US"},
        },
        {
            "name": "Custom Webhook",
            "source_type": "webhook",
            "config": {"endpoint": "/api/v1/webhooks/alerts"},
        },
    ]

    for source_data in sources:
        source = AlertSource(
            id=uuid.uuid4(),
            organization_id=org_id,
            name=source_data["name"],
            source_type=source_data["source_type"],
            config=source_data["config"],
            is_active=True,
            last_received_at=datetime.now(timezone.utc) - timedelta(minutes=random.randint(1, 60)),
            total_alerts_received=random.randint(100, 5000),
        )
        session.add(source)

    await session.flush()
    print(f"Created {len(sources)} alert sources")


async def seed_playbooks(session: AsyncSession, org_id: uuid.UUID, users: Dict[str, User]) -> List[Playbook]:
    """Create demo playbooks."""
    playbooks = []
    admin_user = users.get("admin@demo.com")

    for template in PLAYBOOK_TEMPLATES:
        playbook = Playbook(
            id=uuid.uuid4(),
            organization_id=org_id,
            name=template["name"],
            description=template["description"],
            trigger_conditions=template["trigger_conditions"],
            steps=template["steps"],
            requires_approval=template["requires_approval"],
            approval_roles=["admin", "operator"] if template["requires_approval"] else [],
            is_active=True,
            execution_count=random.randint(5, 50),
            success_count=random.randint(4, 45),
            failure_count=random.randint(0, 5),
            avg_execution_time_seconds=random.randint(30, 300),
            created_by_id=admin_user.id,
            tags=template["tags"],
        )
        session.add(playbook)
        playbooks.append(playbook)

    await session.flush()
    print(f"Created {len(playbooks)} playbooks")
    return playbooks


async def seed_playbook_executions(
    session: AsyncSession,
    org_id: uuid.UUID,
    playbooks: List[Playbook],
    incidents: List[Incident],
    users: Dict[str, User]
) -> None:
    """Create playbook execution history."""
    execution_count = 0
    now = datetime.now(timezone.utc)
    operator_users = [users.get("operator@demo.com"), users.get("operator2@demo.com")]
    admin_user = users.get("admin@demo.com")

    for playbook in playbooks:
        # Create 2-5 executions per playbook
        for _ in range(random.randint(2, 5)):
            days_ago = random.randint(0, 30)
            started_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            status = random.choice(["completed"] * 8 + ["failed"] * 2)
            duration = random.randint(30, 300)
            completed_at = started_at + timedelta(seconds=duration) if status in ["completed", "failed"] else None

            # Generate execution log
            execution_log = []
            for i, step in enumerate(playbook.steps):
                step_status = "completed" if status == "completed" or i < len(playbook.steps) - 1 else "failed"
                execution_log.append({
                    "step": i,
                    "name": step.get("name", f"Step {i+1}"),
                    "status": step_status,
                    "output": "Success" if step_status == "completed" else "Command timed out",
                    "duration_ms": random.randint(100, 5000),
                })

            execution = PlaybookExecution(
                id=uuid.uuid4(),
                playbook_id=playbook.id,
                organization_id=org_id,
                incident_id=random.choice(incidents).id if random.random() > 0.3 else None,
                status=status,
                triggered_by=random.choice(["manual", "auto"]),
                triggered_by_user_id=random.choice(operator_users).id,
                approval_required=playbook.requires_approval,
                approved_by_id=admin_user.id if playbook.requires_approval else None,
                approved_at=started_at - timedelta(minutes=5) if playbook.requires_approval else None,
                execution_log=execution_log,
                result={"success": status == "completed", "steps_executed": len(execution_log)},
                current_step=len(playbook.steps) if status == "completed" else len(playbook.steps) - 1,
                started_at=started_at,
                completed_at=completed_at,
                error_message="Step timeout" if status == "failed" else None,
                created_at=started_at - timedelta(minutes=10),
            )
            session.add(execution)
            execution_count += 1

    await session.flush()
    print(f"Created {execution_count} playbook executions")


async def seed_notifications(session: AsyncSession, org_id: uuid.UUID, users: Dict[str, User]) -> None:
    """Create notifications for users."""
    notification_templates = [
        ("New critical incident assigned", NotificationType.INCIDENT.value, NotificationPriority.HIGH.value),
        ("Alert acknowledged", NotificationType.ALERT.value, NotificationPriority.MEDIUM.value),
        ("Playbook execution completed", NotificationType.SUCCESS.value, NotificationPriority.LOW.value),
        ("Your password will expire in 7 days", NotificationType.WARNING.value, NotificationPriority.MEDIUM.value),
        ("New team member added", NotificationType.INFO.value, NotificationPriority.LOW.value),
        ("Security alert: Unusual login detected", NotificationType.WARNING.value, NotificationPriority.HIGH.value),
        ("Monthly report available", NotificationType.INFO.value, NotificationPriority.LOW.value),
        ("SLA breach warning", NotificationType.WARNING.value, NotificationPriority.URGENT.value),
    ]

    notification_count = 0
    now = datetime.now(timezone.utc)

    for user in users.values():
        if not isinstance(user, User):
            continue

        # Create 3-8 notifications per user
        for _ in range(random.randint(3, 8)):
            title, ntype, priority = random.choice(notification_templates)
            days_ago = random.randint(0, 14)
            created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23))

            is_read = random.random() > 0.4

            notification = Notification(
                id=uuid.uuid4(),
                organization_id=org_id,
                user_id=user.id,
                title=title,
                message=f"Details about: {title}. Please review and take necessary action.",
                type=ntype,
                priority=priority,
                is_read=is_read,
                read_at=created_at + timedelta(hours=random.randint(1, 4)) if is_read else None,
                action_url="/incidents" if "incident" in title.lower() else "/dashboard",
                action_label="View Details",
                created_at=created_at,
            )
            session.add(notification)
            notification_count += 1

    await session.flush()
    print(f"Created {notification_count} notifications")


async def seed_audit_logs(session: AsyncSession, org_id: uuid.UUID, users: Dict[str, User]) -> None:
    """Create audit log entries."""
    audit_count = 0
    now = datetime.now(timezone.utc)
    user_list = [u for u in users.values() if isinstance(u, User)]

    ip_addresses = ["192.168.1.100", "192.168.1.101", "10.0.0.50", "172.16.0.25"]
    user_agents = [
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Chrome/120.0.0.0",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Firefox/121.0",
        "Mozilla/5.0 (X11; Linux x86_64) Chrome/120.0.0.0",
    ]

    for i in range(120):
        action, resource_type, description = random.choice(AUDIT_ACTIONS)
        days_ago = random.randint(0, 30)
        created_at = now - timedelta(days=days_ago, hours=random.randint(0, 23), minutes=random.randint(0, 59))

        user = random.choice(user_list)

        audit = AuditLog(
            id=uuid.uuid4(),
            organization_id=org_id,
            user_id=user.id,
            action=action,
            resource_type=resource_type,
            resource_id=str(uuid.uuid4()),
            resource_name=f"{resource_type.title()} #{random.randint(1000, 9999)}",
            description=description,
            changes={"status": {"old": "active", "new": "updated"}} if action == "update" else None,
            ip_address=random.choice(ip_addresses),
            user_agent=random.choice(user_agents),
            request_id=str(uuid.uuid4()),
            status="success",
            created_at=created_at,
        )
        session.add(audit)
        audit_count += 1

    await session.flush()
    print(f"Created {audit_count} audit log entries")


async def clear_existing_data(session: AsyncSession) -> None:
    """Clear existing demo data if present."""
    # Check if demo org exists
    result = await session.execute(
        text("SELECT id FROM organizations WHERE slug = :slug"),
        {"slug": ORGANIZATION_SLUG}
    )
    row = result.fetchone()

    if row:
        org_id = row[0]
        print(f"Found existing demo organization, clearing data...")

        # Delete in order to respect foreign keys
        await session.execute(text("DELETE FROM audit_logs WHERE organization_id = :org_id"), {"org_id": org_id})
        await session.execute(text("DELETE FROM notifications WHERE organization_id = :org_id"), {"org_id": org_id})
        await session.execute(text("DELETE FROM playbook_executions WHERE organization_id = :org_id"), {"org_id": org_id})
        await session.execute(text("DELETE FROM playbooks WHERE organization_id = :org_id"), {"org_id": org_id})
        await session.execute(text("DELETE FROM alert_correlations WHERE alert_id IN (SELECT id FROM alerts WHERE organization_id = :org_id)"), {"org_id": org_id})
        await session.execute(text("DELETE FROM alert_sources WHERE organization_id = :org_id"), {"org_id": org_id})
        await session.execute(text("DELETE FROM alerts WHERE organization_id = :org_id"), {"org_id": org_id})
        await session.execute(text("DELETE FROM incident_timeline WHERE incident_id IN (SELECT id FROM incidents WHERE organization_id = :org_id)"), {"org_id": org_id})
        await session.execute(text("DELETE FROM incident_comments WHERE incident_id IN (SELECT id FROM incidents WHERE organization_id = :org_id)"), {"org_id": org_id})
        await session.execute(text("DELETE FROM incidents WHERE organization_id = :org_id"), {"org_id": org_id})
        await session.execute(text("DELETE FROM team_members WHERE team_id IN (SELECT id FROM teams WHERE organization_id = :org_id)"), {"org_id": org_id})
        await session.execute(text("DELETE FROM teams WHERE organization_id = :org_id"), {"org_id": org_id})
        await session.execute(text("DELETE FROM users WHERE organization_id = :org_id"), {"org_id": org_id})
        await session.execute(text("DELETE FROM organizations WHERE id = :org_id"), {"org_id": org_id})

        await session.commit()
        print("Existing demo data cleared")


async def main():
    """Main function to seed all demo data."""
    print("=" * 60)
    print("AI-Ops Platform - Demo Data Seeder")
    print("=" * 60)

    # Create engine and session
    engine = await create_database_engine()

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_session() as session:
        try:
            # Clear existing demo data
            await clear_existing_data(session)

            # Seed all data
            print("\nSeeding demo data...")
            print("-" * 40)

            # 1. Organization
            org = await seed_organization(session)

            # 2. Users
            users = await seed_users(session, org.id)

            # 3. Teams
            teams = await seed_teams(session, org.id, users)

            # 4. Team Members
            await seed_team_members(session, teams, users)

            # 5. Incidents
            incidents = await seed_incidents(session, org.id, users, teams)

            # 6. Incident Comments
            await seed_incident_comments(session, incidents, users)

            # 7. Incident Timeline
            await seed_incident_timeline(session, incidents, users)

            # 8. Alerts
            alerts = await seed_alerts(session, org.id, incidents)

            # 9. Alert Correlations
            await seed_alert_correlations(session, alerts)

            # 10. Alert Sources
            await seed_alert_sources(session, org.id)

            # 11. Playbooks
            playbooks = await seed_playbooks(session, org.id, users)

            # 12. Playbook Executions
            await seed_playbook_executions(session, org.id, playbooks, incidents, users)

            # 13. Notifications
            await seed_notifications(session, org.id, users)

            # 14. Audit Logs
            await seed_audit_logs(session, org.id, users)

            # Commit all changes
            await session.commit()

            print("\n" + "=" * 60)
            print("Demo data seeding completed successfully!")
            print("=" * 60)
            print("\nDemo User Accounts:")
            print("-" * 40)
            print(f"{'Email':<30} {'Role':<15} Password")
            print("-" * 40)
            print(f"{'super.admin@demo.com':<30} {'Super Admin':<15} {DEMO_PASSWORD}")
            print(f"{'admin@demo.com':<30} {'Admin':<15} {DEMO_PASSWORD}")
            print(f"{'operator@demo.com':<30} {'Operator':<15} {DEMO_PASSWORD}")
            print(f"{'operator2@demo.com':<30} {'Operator':<15} {DEMO_PASSWORD}")
            print(f"{'viewer@demo.com':<30} {'Viewer':<15} {DEMO_PASSWORD}")
            print(f"{'viewer2@demo.com':<30} {'Viewer':<15} {DEMO_PASSWORD}")
            print("=" * 60)

        except Exception as e:
            await session.rollback()
            print(f"\nError seeding data: {e}")
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
