#!/usr/bin/env python3
"""
Seed script for notifications data.
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy.ext.asyncio import AsyncSession
from app.config.database import AsyncSessionLocal
from app.models import Organization, User, Notification
from app.models.notification import NotificationType, NotificationPriority


async def seed_notifications(db: AsyncSession, org_id: str, user_id: str):
    """Seed notification data."""
    print("Seeding notifications...")
    
    notifications_data = [
        {
            "title": "New Ticket Assigned",
            "message": "Ticket #TKT-001: Email server down has been assigned to you by Admin User",
            "type": NotificationType.INFO.value,
            "priority": NotificationPriority.MEDIUM.value,
            "action_url": "/tickets/1",
            "action_label": "View Ticket",
            "related_entity_type": "ticket",
            "related_entity_id": "1",
            "is_read": False,
        },
        {
            "title": "High Priority Incident",
            "message": "Incident #INC-042: Database connection timeout requires immediate attention",
            "type": NotificationType.ALERT.value,
            "priority": NotificationPriority.HIGH.value,
            "action_url": "/incidents/42",
            "action_label": "View Incident",
            "related_entity_type": "incident",
            "related_entity_id": "42",
            "is_read": False,
        },
        {
            "title": "System Maintenance Scheduled",
            "message": "Scheduled maintenance window: January 15, 2026 02:00-04:00 UTC. Services may be temporarily unavailable.",
            "type": NotificationType.SYSTEM.value,
            "priority": NotificationPriority.MEDIUM.value,
            "is_read": True,
            "read_at": datetime.utcnow() - timedelta(hours=2),
        },
        {
            "title": "Alert Escalated",
            "message": "Alert: CPU usage > 90% on prod-server-01 has been escalated due to no response",
            "type": NotificationType.WARNING.value,
            "priority": NotificationPriority.HIGH.value,
            "action_url": "/alerts/123",
            "action_label": "View Alert",
            "related_entity_type": "alert",
            "related_entity_id": "123",
            "is_read": False,
        },
        {
            "title": "Playbook Execution Completed",
            "message": "Auto-restart playbook for nginx service completed successfully",
            "type": NotificationType.SUCCESS.value,
            "priority": NotificationPriority.LOW.value,
            "action_url": "/playbooks/executions/456",
            "action_label": "View Execution",
            "related_entity_type": "playbook_execution",
            "related_entity_id": "456",
            "is_read": False,
        },
        {
            "title": "Security Investigation Created",
            "message": "New security investigation: Suspicious login attempts from unknown IP addresses",
            "type": NotificationType.WARNING.value,
            "priority": NotificationPriority.HIGH.value,
            "action_url": "/security/investigations/789",
            "action_label": "View Investigation",
            "related_entity_type": "investigation",
            "related_entity_id": "789",
            "is_read": False,
        },
        {
            "title": "Team Assignment Updated",
            "message": "You have been added to the Database Team with operator permissions",
            "type": NotificationType.INFO.value,
            "priority": NotificationPriority.MEDIUM.value,
            "action_url": "/teams",
            "action_label": "View Teams",
            "is_read": True,
            "read_at": datetime.utcnow() - timedelta(days=1),
        },
        {
            "title": "Prediction Alert",
            "message": "AI predicts database storage will reach 90% capacity in 3-5 days",
            "type": NotificationType.WARNING.value,
            "priority": NotificationPriority.MEDIUM.value,
            "action_url": "/predictions",
            "action_label": "View Predictions",
            "related_entity_type": "prediction",
            "related_entity_id": "pred-001",
            "is_read": False,
        },
    ]
    
    for notification_data in notifications_data:
        notification = Notification(
            organization_id=org_id,
            user_id=user_id,
            **notification_data
        )
        db.add(notification)
    
    await db.commit()
    print(f"✓ Created {len(notifications_data)} notifications")


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
            
            print(f"Seeding notifications for user: {admin_user.email}")
            
            # Seed notifications
            await seed_notifications(db, str(org.id), str(admin_user.id))
            
            print("\n✅ Notifications seeding completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())