#!/usr/bin/env python3
"""
Seed script for playbooks and predictions data.
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import AsyncSessionLocal
from app.models import Organization, User, Playbook, Prediction


async def seed_playbooks(db: AsyncSession, org_id: str, admin_user_id: str):
    """Seed playbook data."""
    print("Seeding playbooks...")
    
    playbooks_data = [
        {
            "name": "Auto-Restart Failed Services",
            "description": "Automatically restart services when they fail health checks",
            "trigger_conditions": {"trigger": "Alert: Service Down"},
            "steps": [
                {"type": "script", "name": "Check service status", "config": {"command": "systemctl status nginx"}},
                {"type": "notification", "name": "Notify team", "config": {"channel": "slack", "message": "Investigating service failure"}},
                {"type": "script", "name": "Restart service", "config": {"command": "systemctl restart nginx"}},
                {"type": "notification", "name": "Confirm restart", "config": {"channel": "slack", "message": "Service restarted successfully"}},
            ],
            "requires_approval": False,
            "approval_roles": [],
            "is_active": True,
            "execution_count": 156,
            "success_count": 147,
            "failure_count": 9,
            "avg_execution_time_seconds": 12,
            "tags": ["automation", "service-recovery"],
        },
        {
            "name": "Database Failover",
            "description": "Initiate database failover when primary becomes unavailable",
            "trigger_conditions": {"trigger": "Alert: DB Connection Timeout"},
            "steps": [
                {"type": "script", "name": "Check DB health", "config": {"command": "pg_isready"}},
                {"type": "approval", "name": "Approve failover", "config": {"roles": ["admin"]}},
                {"type": "script", "name": "Promote replica", "config": {"command": "pg_ctl promote"}},
                {"type": "notification", "name": "Alert team", "config": {"channel": "pagerduty", "message": "Database failover completed"}},
            ],
            "requires_approval": True,
            "approval_roles": ["admin"],
            "is_active": True,
            "execution_count": 12,
            "success_count": 12,
            "failure_count": 0,
            "avg_execution_time_seconds": 45,
            "tags": ["database", "failover", "critical"],
        },
        {
            "name": "Scale Up on High Load",
            "description": "Auto-scale application instances when CPU exceeds 80%",
            "trigger_conditions": {"trigger": "Metric: CPU > 80%"},
            "steps": [
                {"type": "script", "name": "Check current capacity", "config": {"command": "kubectl get pods"}},
                {"type": "script", "name": "Scale deployment", "config": {"command": "kubectl scale deployment app --replicas=5"}},
                {"type": "notification", "name": "Notify ops", "config": {"channel": "slack", "message": "Auto-scaled application"}},
            ],
            "requires_approval": False,
            "approval_roles": [],
            "is_active": True,
            "execution_count": 89,
            "success_count": 88,
            "failure_count": 1,
            "avg_execution_time_seconds": 30,
            "tags": ["scaling", "performance"],
        },
        {
            "name": "Security Incident Response",
            "description": "Isolate affected systems and notify security team",
            "trigger_conditions": {"trigger": "Alert: Security Breach"},
            "steps": [
                {"type": "script", "name": "Isolate system", "config": {"command": "iptables -A INPUT -j DROP"}},
                {"type": "notification", "name": "Alert security", "config": {"channel": "pagerduty", "message": "Security incident detected"}},
                {"type": "approval", "name": "Approve remediation", "config": {"roles": ["security_admin"]}},
                {"type": "script", "name": "Run security scan", "config": {"command": "trivy scan"}},
            ],
            "requires_approval": True,
            "approval_roles": ["security_admin"],
            "is_active": False,
            "execution_count": 3,
            "success_count": 3,
            "failure_count": 0,
            "avg_execution_time_seconds": 120,
            "tags": ["security", "incident-response"],
        },
        {
            "name": "Disk Cleanup Automation",
            "description": "Clean up old logs and temp files when disk usage exceeds 90%",
            "trigger_conditions": {"trigger": "Metric: Disk > 90%"},
            "steps": [
                {"type": "script", "name": "Check disk usage", "config": {"command": "df -h"}},
                {"type": "script", "name": "Clean old logs", "config": {"command": "find /var/log -mtime +30 -delete"}},
                {"type": "script", "name": "Clean temp files", "config": {"command": "rm -rf /tmp/*"}},
                {"type": "notification", "name": "Report cleanup", "config": {"channel": "slack", "message": "Disk cleanup completed"}},
            ],
            "requires_approval": False,
            "approval_roles": [],
            "is_active": True,
            "execution_count": 0,
            "success_count": 0,
            "failure_count": 0,
            "avg_execution_time_seconds": None,
            "tags": ["maintenance", "disk-management"],
        },
    ]
    
    for playbook_data in playbooks_data:
        playbook = Playbook(
            organization_id=org_id,
            created_by_id=admin_user_id,
            **playbook_data
        )
        db.add(playbook)
    
    await db.commit()
    print(f"✓ Created {len(playbooks_data)} playbooks")


async def seed_predictions(db: AsyncSession, org_id: str):
    """Seed prediction data."""
    print("Seeding predictions...")
    
    predictions_data = [
        {
            "type": "capacity",
            "resource": "prod-db-primary",
            "prediction": "Database storage will reach 90% capacity",
            "likelihood": Decimal("0.87"),
            "impact": "high",
            "timeframe": "3-5 days",
            "predicted_date": datetime.utcnow() + timedelta(days=4),
            "status": "active",
            "recommended_action": "Increase storage allocation or archive old data",
            "details": "Based on current growth rate of 2.5GB/day, the database will reach 90% capacity within 3-5 days. Current usage is at 78%.",
            "prevention_steps": [
                "Archive data older than 90 days to cold storage",
                "Increase RDS storage from 500GB to 750GB",
                "Review and optimize large tables",
                "Set up storage usage alerts at 80% and 85%",
            ],
            "model_version": "v1.2.0",
            "confidence_factors": {"historical_accuracy": 0.92, "data_quality": 0.95},
        },
        {
            "type": "performance",
            "resource": "api-gateway",
            "prediction": "API latency will exceed SLA threshold during peak hours",
            "likelihood": Decimal("0.72"),
            "impact": "medium",
            "timeframe": "1-2 days",
            "predicted_date": datetime.utcnow() + timedelta(days=1),
            "status": "active",
            "recommended_action": "Scale up API instances before peak period",
            "details": "Historical traffic patterns show a 40% increase in requests during the upcoming promotion. Current capacity may not handle the load.",
            "prevention_steps": [
                "Pre-scale API instances from 3 to 5",
                "Enable auto-scaling with aggressive thresholds",
                "Warm up the cache before peak period",
                "Set up latency alerts at 500ms P95",
            ],
            "model_version": "v1.2.0",
            "confidence_factors": {"historical_accuracy": 0.85, "data_quality": 0.88},
        },
        {
            "type": "failure",
            "resource": "cache-cluster-node-3",
            "prediction": "Memory exhaustion risk based on current growth pattern",
            "likelihood": Decimal("0.65"),
            "impact": "high",
            "timeframe": "7-10 days",
            "predicted_date": datetime.utcnow() + timedelta(days=8),
            "status": "active",
            "recommended_action": "Review cache eviction policy and memory allocation",
            "details": "Node memory usage has been growing at 1% per day. At current rate, it will reach critical levels in 7-10 days.",
            "prevention_steps": [
                "Review cache TTL settings",
                "Implement LRU eviction policy",
                "Add another cache node to distribute load",
                "Monitor memory usage trends",
            ],
            "model_version": "v1.2.0",
            "confidence_factors": {"historical_accuracy": 0.78, "data_quality": 0.82},
        },
        {
            "type": "security",
            "resource": "SSL Certificate",
            "prediction": "Certificate for app.example.com will expire",
            "likelihood": Decimal("1.00"),
            "impact": "critical",
            "timeframe": "14 days",
            "predicted_date": datetime.utcnow() + timedelta(days=14),
            "status": "active",
            "recommended_action": "Renew SSL certificate before expiration",
            "details": "The SSL certificate for app.example.com expires on January 19, 2026. Certificate must be renewed and deployed before this date.",
            "prevention_steps": [
                "Request new certificate from Let's Encrypt",
                "Deploy new certificate to load balancer",
                "Verify certificate chain is complete",
                "Set up automated certificate renewal",
            ],
            "model_version": "v1.2.0",
            "confidence_factors": {"historical_accuracy": 1.0, "data_quality": 1.0},
        },
        {
            "type": "capacity",
            "resource": "prod-logs-bucket",
            "prediction": "Log storage exceeded threshold",
            "likelihood": Decimal("0.95"),
            "impact": "medium",
            "timeframe": "Occurred",
            "predicted_date": datetime.utcnow() - timedelta(days=5),
            "status": "prevented",
            "recommended_action": "Implemented log rotation policy",
            "details": "AI predicted storage issue 5 days ago. Log rotation was implemented, preventing the issue.",
            "prevention_steps": [],
            "action_taken": "Implemented log rotation policy",
            "action_taken_at": datetime.utcnow() - timedelta(days=4),
            "model_version": "v1.2.0",
            "confidence_factors": {"historical_accuracy": 0.93, "data_quality": 0.91},
        },
        {
            "type": "performance",
            "resource": "worker-queue",
            "prediction": "Queue backlog predicted to cause delays",
            "likelihood": Decimal("0.78"),
            "impact": "medium",
            "timeframe": "Expired",
            "predicted_date": datetime.utcnow() - timedelta(days=3),
            "status": "expired",
            "recommended_action": "Prediction window passed without occurrence",
            "details": "The predicted backlog did not occur. Queue processing remained within normal parameters.",
            "prevention_steps": [],
            "model_version": "v1.2.0",
            "confidence_factors": {"historical_accuracy": 0.75, "data_quality": 0.80},
        },
    ]
    
    for prediction_data in predictions_data:
        prediction = Prediction(
            organization_id=org_id,
            **prediction_data
        )
        db.add(prediction)
    
    await db.commit()
    print(f"✓ Created {len(predictions_data)} predictions")


async def main():
    """Main seeding function."""
    async with AsyncSessionLocal() as db:
        try:
            # Get the first organization and admin user
            from sqlalchemy import select
            
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
            
            # Seed playbooks
            await seed_playbooks(db, str(org.id), str(admin_user.id))
            
            # Seed predictions
            await seed_predictions(db, str(org.id))
            
            print("\n✅ Playbooks and predictions seeding completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
