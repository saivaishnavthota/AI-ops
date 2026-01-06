#!/usr/bin/env python3
"""
Seed script for security investigations.
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
from app.models import Organization, User, Investigation


async def seed_investigations(db: AsyncSession, org_id: str, user_id: str):
    """Seed security investigations."""
    print("Seeding investigations...")
    
    investigations_data = [
        {
            "title": "Suspicious API Access Pattern Investigation",
            "description": "Investigating unusual API call patterns from multiple user accounts",
            "status": "active",
            "priority": "high",
            "assignee_name": "Alex Chen",
            "progress": 65,
            "events_linked": 15,
            "findings": [
                "Identified 3 user accounts with unusual activity",
                "API calls originating from unexpected geographic locations",
                "Pattern suggests automated script usage",
            ],
            "timeline": [
                {
                    "date": (datetime.utcnow() - timedelta(hours=4)).isoformat(),
                    "action": "Investigation created",
                    "user": "System",
                },
                {
                    "date": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                    "action": "Assigned to Alex Chen",
                    "user": "Admin",
                },
                {
                    "date": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                    "action": "Initial analysis completed",
                    "user": "Alex Chen",
                },
            ],
        },
        {
            "title": "Container Image Vulnerability Assessment",
            "description": "Analysis of critical CVE detected in production images",
            "status": "active",
            "priority": "critical",
            "assignee_name": "Sarah Johnson",
            "progress": 30,
            "events_linked": 8,
            "findings": [
                "CVE-2025-1234 confirmed in base image",
                "Affects 5 production containers",
            ],
            "timeline": [
                {
                    "date": (datetime.utcnow() - timedelta(hours=3)).isoformat(),
                    "action": "Investigation created",
                    "user": "Security Scanner",
                },
                {
                    "date": (datetime.utcnow() - timedelta(hours=2, minutes=30)).isoformat(),
                    "action": "Assigned to Sarah Johnson",
                    "user": "Admin",
                },
            ],
        },
        {
            "title": "Failed Login Attempts Analysis",
            "description": "Reviewing pattern of failed authentication attempts",
            "status": "pending",
            "priority": "medium",
            "assignee_name": "Mike Wilson",
            "progress": 10,
            "events_linked": 23,
            "findings": [],
            "timeline": [
                {
                    "date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    "action": "Investigation created",
                    "user": "System",
                },
            ],
        },
        {
            "title": "Firewall Rule Change Audit",
            "description": "Audit of recent security group modifications",
            "status": "closed",
            "priority": "low",
            "assignee_name": "Emily Davis",
            "progress": 100,
            "events_linked": 5,
            "findings": [
                "All changes were authorized",
                "Documentation verified",
                "No security concerns identified",
            ],
            "timeline": [
                {
                    "date": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                    "action": "Investigation created",
                    "user": "System",
                },
                {
                    "date": (datetime.utcnow() - timedelta(days=2, hours=2)).isoformat(),
                    "action": "Assigned to Emily Davis",
                    "user": "Admin",
                },
                {
                    "date": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                    "action": "Investigation closed",
                    "user": "Emily Davis",
                },
            ],
        },
    ]
    
    for investigation_data in investigations_data:
        investigation = Investigation(
            organization_id=org_id,
            created_by_id=user_id,
            **investigation_data
        )
        db.add(investigation)
    
    await db.commit()
    print(f"✓ Created {len(investigations_data)} investigations")


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
            
            # Seed investigations
            await seed_investigations(db, str(org.id), str(admin_user.id))
            
            print("\n✅ Investigations seeding completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during seeding: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
