"""
Background tasks for ticket management.
"""

from datetime import datetime, timezone, timedelta
from typing import List
import logging

from celery import Celery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from ..config.settings import settings
from ..models.ticket import Ticket
from ..models.incident import Incident

logger = logging.getLogger(__name__)

# Create async engine for background tasks
engine = create_async_engine(settings.DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def migrate_old_resolved_tickets():
    """
    Migrate resolved tickets older than 1 day to incidents.
    This should be run as a daily background task.
    """
    
    async with AsyncSessionLocal() as db:
        try:
            # Find resolved tickets older than 1 day
            one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)
            
            result = await db.execute(
                select(Ticket).where(
                    Ticket.status == "resolved",
                    Ticket.resolved_at <= one_day_ago
                )
            )
            old_tickets = result.scalars().all()
            
            migrated_count = 0
            
            for ticket in old_tickets:
                try:
                    # Create incident from ticket
                    incident = Incident(
                        organization_id=ticket.organization_id,
                        incident_number=f"INC-{datetime.now().strftime('%Y%m%d')}-{ticket.id.hex[:8]}",
                        title=ticket.subject,
                        description=ticket.description,
                        status="closed",  # Since ticket was resolved
                        priority=ticket.priority,
                        severity="medium",  # Default severity
                        impact="medium",   # Default impact
                        urgency="medium",  # Default urgency
                        category=ticket.category,
                        subcategory="service_desk",
                        assigned_team_id=None,
                        assignee_id=ticket.assignee_id,
                        assignee_name=ticket.assignee_name,
                        created_at=ticket.created_at,
                        acknowledged_at=ticket.created_at,
                        resolved_at=ticket.resolved_at,
                        closed_at=ticket.resolved_at,
                        source="service_desk_ticket",
                        source_id=str(ticket.id),
                        comments=ticket.comments or [],
                        tags=["migrated_from_ticket"],
                        metadata={
                            "original_ticket_id": str(ticket.id),
                            "migration_date": datetime.now(timezone.utc).isoformat(),
                            "requester_name": ticket.requester_name
                        }
                    )
                    
                    db.add(incident)
                    
                    # Delete the original ticket
                    await db.delete(ticket)
                    
                    migrated_count += 1
                    
                except Exception as e:
                    logger.error(f"Failed to migrate ticket {ticket.id}: {e}")
                    continue
            
            await db.commit()
            
            logger.info(f"Successfully migrated {migrated_count} resolved tickets to incidents")
            return migrated_count
            
        except Exception as e:
            logger.error(f"Error in ticket migration: {e}")
            await db.rollback()
            raise


# Celery task wrapper (if Celery is available)
try:
    from ..worker import celery_app
    
    @celery_app.task(name="migrate_old_resolved_tickets")
    def migrate_old_resolved_tickets_task():
        """Celery task wrapper for ticket migration."""
        import asyncio
        return asyncio.run(migrate_old_resolved_tickets())
        
except ImportError:
    logger.warning("Celery not available, ticket migration will need to be run manually")


# Manual execution function
async def run_ticket_migration():
    """Run ticket migration manually."""
    try:
        count = await migrate_old_resolved_tickets()
        print(f"✓ Migrated {count} tickets to incidents")
        return count
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        raise
    finally:
        await engine.dispose()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_ticket_migration())