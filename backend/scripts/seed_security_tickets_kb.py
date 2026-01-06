#!/usr/bin/env python3
"""
Seed script for security events, tickets, and knowledge base articles.
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config.database import AsyncSessionLocal
from app.models import Organization, User, SecurityEvent, Ticket, KnowledgeBaseArticle


async def seed_security_events(db: AsyncSession, org_id: str):
    """Seed security events."""
    print("Seeding security events...")
    
    events_data = [
        {
            "type": "Failed Login Attempt",
            "severity": "medium",
            "source": "Auth Service",
            "description": "Multiple failed login attempts detected from IP 192.168.1.100",
            "status": "investigating",
            "affected_asset": "auth.example.com",
            "details": "15 failed login attempts in the last 5 minutes. All attempts used the same username but different passwords.",
            "ip_address": "192.168.1.100",
            "user": "admin@example.com",
        },
        {
            "type": "Suspicious API Activity",
            "severity": "high",
            "source": "API Gateway",
            "description": "Unusual rate of API calls from user account detected",
            "status": "open",
            "affected_asset": "api.example.com",
            "details": "User made 10,000 API calls in 1 hour, which is 50x the normal rate.",
            "ip_address": "203.45.67.89",
            "user": "service-account-1",
        },
        {
            "type": "SSL Certificate Expiring",
            "severity": "medium",
            "source": "Certificate Monitor",
            "description": "SSL certificate for app.example.com expires in 14 days",
            "status": "open",
            "affected_asset": "app.example.com",
            "details": "Certificate issued by Let's Encrypt, expires on 2025-01-19.",
        },
        {
            "type": "Vulnerability Detected",
            "severity": "critical",
            "source": "Security Scanner",
            "description": "Critical CVE-2025-1234 detected in production container images",
            "status": "investigating",
            "affected_asset": "prod-api:latest",
            "details": "CVE-2025-1234 affects the base image. CVSS score: 9.8. Remote code execution vulnerability.",
        },
        {
            "type": "Firewall Rule Change",
            "severity": "info",
            "source": "AWS CloudTrail",
            "description": "Security group sg-12345 modified by admin user",
            "status": "resolved",
            "affected_asset": "sg-12345",
            "details": "Port 22 was opened to 10.0.0.0/8 CIDR range by user admin@example.com.",
            "user": "admin@example.com",
            "resolved_at": datetime.utcnow() - timedelta(hours=2),
        },
        {
            "type": "Port Scan Detected",
            "severity": "low",
            "source": "IDS",
            "description": "Port scan activity detected from external IP",
            "status": "false_positive",
            "affected_asset": "edge-firewall",
            "ip_address": "8.8.8.8",
            "details": "Detected as Google's DNS server performing legitimate health checks.",
        },
    ]
    
    for event_data in events_data:
        event = SecurityEvent(
            organization_id=org_id,
            **event_data
        )
        db.add(event)
    
    await db.commit()
    print(f"✓ Created {len(events_data)} security events")


async def seed_tickets(db: AsyncSession, org_id: str, user_id: str):
    """Seed support tickets."""
    print("Seeding tickets...")
    
    tickets_data = [
        {
            "subject": "Cannot access production dashboard",
            "description": "Getting 403 error when trying to access the main dashboard. This started happening after the recent deployment.",
            "status": "open",
            "priority": "high",
            "requester_name": "John Smith",
            "assignee_name": "Support Team",
            "category": "Access Issue",
            "comments": [
                {"user": "John Smith", "text": "This is blocking my work", "time": (datetime.utcnow() - timedelta(minutes=5)).isoformat()},
            ],
        },
        {
            "subject": "Request for new API key",
            "description": "Need a new API key for the reporting integration. The old one expired.",
            "status": "in_progress",
            "priority": "normal",
            "requester_name": "Sarah Johnson",
            "assignee_name": "Mike Wilson",
            "category": "Service Request",
            "comments": [
                {"user": "Mike Wilson", "text": "Generating new API key now", "time": (datetime.utcnow() - timedelta(minutes=15)).isoformat()},
            ],
        },
        {
            "subject": "Slow response times on API",
            "description": "API response times have increased significantly since yesterday. P95 latency is now over 2 seconds.",
            "status": "in_progress",
            "priority": "urgent",
            "requester_name": "Alex Chen",
            "assignee_name": "Emily Davis",
            "category": "Performance",
            "comments": [
                {"user": "Emily Davis", "text": "Investigating database connection pool", "time": (datetime.utcnow() - timedelta(hours=1)).isoformat()},
                {"user": "Emily Davis", "text": "Found the issue - scaling up the database", "time": (datetime.utcnow() - timedelta(minutes=30)).isoformat()},
            ],
        },
        {
            "subject": "Update user permissions",
            "description": "Please add admin access for the new team member Tom Anderson.",
            "status": "pending",
            "priority": "low",
            "requester_name": "Lisa Brown",
            "assignee_name": None,
            "category": "Access Issue",
            "comments": [],
        },
        {
            "subject": "Monthly report generation failed",
            "description": "The scheduled monthly report did not generate this morning. Error: Timeout exceeded.",
            "status": "resolved",
            "priority": "normal",
            "requester_name": "Tom Anderson",
            "assignee_name": "Support Team",
            "category": "Bug Report",
            "comments": [
                {"user": "Support Team", "text": "Increased timeout and reran the report successfully", "time": (datetime.utcnow() - timedelta(days=1)).isoformat()},
            ],
            "resolved_at": datetime.utcnow() - timedelta(days=1),
        },
    ]
    
    for ticket_data in tickets_data:
        ticket = Ticket(
            organization_id=org_id,
            requester_id=user_id,
            **ticket_data
        )
        db.add(ticket)
    
    await db.commit()
    print(f"✓ Created {len(tickets_data)} tickets")


async def seed_kb_articles(db: AsyncSession, org_id: str, user_id: str):
    """Seed knowledge base articles."""
    print("Seeding knowledge base articles...")
    
    articles_data = [
        {
            "title": "How to set up monitoring alerts",
            "excerpt": "Learn how to configure alerts for your infrastructure and applications...",
            "content": """# How to Set Up Monitoring Alerts

This guide will walk you through the process of setting up monitoring alerts for your infrastructure.

## Prerequisites
- Access to the AI-Ops dashboard
- Admin or Operator role

## Steps

### 1. Navigate to Alert Settings
Go to Settings > Alerts in the main navigation.

### 2. Create a New Alert Rule
Click "Create Alert Rule" and configure:
- **Name**: Give your alert a descriptive name
- **Condition**: Set the metric and threshold
- **Severity**: Choose from Critical, High, Medium, Low
- **Notification**: Select notification channels

### 3. Configure Notification Channels
Set up where alerts should be sent:
- Email notifications
- Slack integration
- PagerDuty escalation

### 4. Test Your Alert
Use the "Test" button to verify your alert configuration works correctly.

## Best Practices
- Start with higher thresholds and tune down
- Use different severities appropriately
- Set up escalation policies for critical alerts""",
            "category": "Getting Started",
            "tags": ["alerts", "monitoring", "setup"],
            "views": 1250,
            "helpful_count": 89,
        },
        {
            "title": "Troubleshooting API connection issues",
            "excerpt": "Common causes and solutions for API connectivity problems...",
            "content": """# Troubleshooting API Connection Issues

This article covers common API connectivity problems and their solutions.

## Common Issues

### 1. Authentication Errors (401)
**Cause**: Invalid or expired API key
**Solution**:
- Verify your API key is correct
- Check if the key has expired
- Regenerate the key if needed

### 2. Forbidden Errors (403)
**Cause**: Insufficient permissions
**Solution**:
- Check your user role permissions
- Verify IP whitelist settings
- Contact admin for access

### 3. Timeout Errors
**Cause**: Network issues or overloaded servers
**Solution**:
- Check your network connection
- Increase timeout settings
- Verify server status

## Debugging Steps
1. Check the API status page
2. Verify network connectivity
3. Review request headers
4. Check rate limits""",
            "category": "Troubleshooting",
            "tags": ["api", "troubleshooting", "errors"],
            "views": 980,
            "helpful_count": 76,
        },
        {
            "title": "Integrating with Slack for notifications",
            "excerpt": "Step-by-step guide to connect your workspace with Slack...",
            "content": """# Integrating with Slack for Notifications

Connect AI-Ops with Slack to receive real-time notifications.

## Setup Process

### 1. Create a Slack App
1. Go to api.slack.com/apps
2. Click "Create New App"
3. Choose "From scratch"
4. Name it "AI-Ops Notifications"

### 2. Configure Permissions
Add these OAuth scopes:
- chat:write
- channels:read

### 3. Install to Workspace
Click "Install to Workspace" and authorize.

### 4. Copy the Webhook URL
Navigate to Incoming Webhooks and copy the URL.

### 5. Add to AI-Ops
Go to Integrations > Slack and paste the webhook URL.

## Customizing Notifications
You can customize which alerts go to which channels.""",
            "category": "Integrations",
            "tags": ["slack", "integration", "notifications"],
            "views": 856,
            "helpful_count": 92,
        },
        {
            "title": "Understanding incident priority levels",
            "excerpt": "Learn about P1-P5 priority classifications and response times...",
            "content": """# Understanding Incident Priority Levels

## Priority Classifications

### P1 - Critical
- Complete service outage
- Response time: 15 minutes
- All hands on deck

### P2 - High
- Major functionality impaired
- Response time: 1 hour
- On-call team response

### P3 - Medium
- Partial impact
- Response time: 4 hours
- Normal business hours

### P4 - Low
- Minor issue
- Response time: 24 hours

### P5 - Planning
- Enhancement request
- Response time: As scheduled""",
            "category": "Best Practices",
            "tags": ["incidents", "priority", "sla"],
            "views": 720,
            "helpful_count": 85,
        },
        {
            "title": "Setting up SSO authentication",
            "excerpt": "Configure single sign-on with your identity provider...",
            "content": """# Setting up SSO Authentication

Enable Single Sign-On for your organization.

## Supported Providers
- Okta
- Azure AD
- Google Workspace
- OneLogin

## Configuration Steps
1. Go to Settings > Security > SSO
2. Select your identity provider
3. Enter your SSO metadata
4. Configure attribute mapping
5. Test the connection""",
            "category": "Security",
            "tags": ["sso", "authentication", "security"],
            "views": 650,
            "helpful_count": 78,
        },
    ]
    
    for article_data in articles_data:
        article = KnowledgeBaseArticle(
            organization_id=org_id,
            author_id=user_id,
            is_published=True,
            **article_data
        )
        db.add(article)
    
    await db.commit()
    print(f"✓ Created {len(articles_data)} knowledge base articles")


async def main():
    """Main seeding function."""
    async with AsyncSessionLocal() as db:
        try:
            # Get the first organization and admin user
            result = await db.execute(select(Organization))
            org = result.scalars().first()
            
            if not org:
                print("❌ No organization found. Please run the main seed script first.")
                return
            
            result = await db.execute(
                select(User).filter(
                    User.organization_id == org.id,
                    User.role == "admin"
                )
            )
            admin_user = result.scalars().first()
            
            if not admin_user:
                print("❌ No admin user found. Please run the main seed script first.")
                return
            
            print(f"Seeding data for organization: {org.name}")
            
            # Seed security events
            await seed_security_events(db, str(org.id))
            
            # Seed tickets
            await seed_tickets(db, str(org.id), str(admin_user.id))
            
            # Seed knowledge base articles
            await seed_kb_articles(db, str(org.id), str(admin_user.id))
            
            print("\n✅ Security, tickets, and KB seeding completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
