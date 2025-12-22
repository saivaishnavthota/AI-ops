"""
Incident-related background tasks with AI integration.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from uuid import UUID

from app.workers.celery_app import celery_app
from app.config.database import AsyncSessionLocal
from app.ml.service import AIService

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async code in Celery tasks."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery_app.task(name="app.workers.tasks.incidents.check_stale_incidents")
def check_stale_incidents() -> dict:
    """
    Check for incidents that haven't been updated and need attention.
    """
    logger.info("Checking for stale incidents")

    try:
        thresholds = {
            "p1": timedelta(minutes=15),
            "p2": timedelta(hours=1),
            "p3": timedelta(hours=4),
            "p4": timedelta(hours=24),
        }

        async def _check_stale():
            from sqlalchemy import select, and_
            from app.models.incident import Incident

            stale_count = 0
            escalated_count = 0

            async with AsyncSessionLocal() as db:
                now = datetime.utcnow()

                for priority, threshold in thresholds.items():
                    cutoff = now - threshold
                    result = await db.execute(
                        select(Incident)
                        .where(
                            and_(
                                Incident.status.in_(["open", "acknowledged", "in_progress"]),
                                Incident.priority == priority,
                                Incident.updated_at < cutoff,
                            )
                        )
                    )
                    stale_incidents = result.scalars().all()
                    stale_count += len(stale_incidents)

                    # Mark as needing escalation (could trigger notifications)
                    for incident in stale_incidents:
                        if not incident.extra_data:
                            incident.extra_data = {}
                        incident.extra_data["stale_check"] = now.isoformat()
                        escalated_count += 1

                await db.commit()

            return stale_count, escalated_count

        stale_count, escalated_count = run_async(_check_stale())

        logger.info(
            f"Stale incident check completed: {stale_count} stale, "
            f"{escalated_count} escalated"
        )

        return {
            "status": "success",
            "stale": stale_count,
            "escalated": escalated_count,
        }

    except Exception as e:
        logger.error(f"Stale incident check failed: {e}")
        raise


@celery_app.task(name="app.workers.tasks.incidents.auto_classify")
def auto_classify_incident(incident_id: str) -> dict:
    """
    Use AI to automatically classify an incident.
    """
    logger.info(f"Auto-classifying incident {incident_id}")

    try:
        async def _classify():
            async with AsyncSessionLocal() as db:
                async with AIService(db) as ai:
                    result = await ai.classify_incident(
                        incident_id=UUID(incident_id),
                        update_incident=True,
                    )
                    return result

        result = run_async(_classify())

        logger.info(
            f"Auto-classification completed for {incident_id}: "
            f"{result['classification']['category']} "
            f"(confidence: {result['classification']['confidence']:.2f})"
        )

        return {
            "status": "success",
            "incident_id": incident_id,
            "classification": result["classification"],
        }

    except Exception as e:
        logger.error(f"Auto-classification failed for {incident_id}: {e}")
        raise


@celery_app.task(name="app.workers.tasks.incidents.suggest_resolution")
def suggest_resolution(incident_id: str) -> dict:
    """
    Use AI to suggest resolution steps for an incident.
    """
    logger.info(f"Generating resolution suggestions for incident {incident_id}")

    try:
        async def _suggest():
            async with AsyncSessionLocal() as db:
                async with AIService(db) as ai:
                    result = await ai.suggest_resolution(
                        incident_id=UUID(incident_id),
                        update_incident=True,
                    )
                    return result

        result = run_async(_suggest())

        logger.info(
            f"Resolution suggestions generated for {incident_id}: "
            f"{len(result['suggestion']['steps'])} steps "
            f"(confidence: {result['suggestion']['confidence']:.2f})"
        )

        return {
            "status": "success",
            "incident_id": incident_id,
            "suggestion": result["suggestion"],
            "suggestion_text": result["suggestion_text"],
        }

    except Exception as e:
        logger.error(f"Resolution suggestion failed for {incident_id}: {e}")
        raise


@celery_app.task(name="app.workers.tasks.incidents.analyze_incident")
def analyze_incident(incident_id: str) -> dict:
    """
    Perform full AI analysis (classification + suggestions) on an incident.
    """
    logger.info(f"Running full AI analysis for incident {incident_id}")

    try:
        async def _analyze():
            async with AsyncSessionLocal() as db:
                async with AIService(db) as ai:
                    result = await ai.analyze_incident(
                        incident_id=UUID(incident_id),
                        update_incident=True,
                    )
                    return result

        result = run_async(_analyze())

        logger.info(f"Full AI analysis completed for {incident_id}")

        return {
            "status": "success",
            "incident_id": incident_id,
            "classification": result["classification"],
            "suggestion": result["suggestion"],
        }

    except Exception as e:
        logger.error(f"Full AI analysis failed for {incident_id}: {e}")
        raise


@celery_app.task(name="app.workers.tasks.incidents.execute_playbook")
def execute_playbook(incident_id: str, playbook_id: str) -> dict:
    """
    Execute an automation playbook for an incident.
    """
    logger.info(f"Executing playbook {playbook_id} for incident {incident_id}")

    try:
        async def _execute():
            from sqlalchemy import select
            from app.models.playbook import Playbook, PlaybookExecution, PlaybookStatus
            from app.models.incident import IncidentTimeline

            async with AsyncSessionLocal() as db:
                # Fetch playbook
                result = await db.execute(
                    select(Playbook).where(Playbook.id == UUID(playbook_id))
                )
                playbook = result.scalar_one_or_none()

                if not playbook:
                    raise ValueError(f"Playbook {playbook_id} not found")

                # Create execution record
                execution = PlaybookExecution(
                    playbook_id=playbook.id,
                    organization_id=playbook.organization_id,
                    incident_id=UUID(incident_id),
                    status=PlaybookStatus.RUNNING.value,
                    triggered_by="auto",
                    started_at=datetime.utcnow(),
                    execution_log=[],
                )
                db.add(execution)
                await db.flush()

                steps_executed = 0
                steps_failed = 0

                # Execute each step
                for i, step in enumerate(playbook.steps or []):
                    step_log = {
                        "step": i,
                        "name": step.get("name", f"Step {i+1}"),
                        "type": step.get("type", "unknown"),
                        "started_at": datetime.utcnow().isoformat(),
                    }

                    try:
                        # Placeholder for actual step execution
                        # In production, this would execute scripts, send notifications, etc.
                        step_log["status"] = "completed"
                        step_log["duration_ms"] = 100
                        steps_executed += 1
                    except Exception as step_error:
                        step_log["status"] = "failed"
                        step_log["error"] = str(step_error)
                        steps_failed += 1

                    execution.execution_log.append(step_log)
                    execution.current_step = i + 1

                # Update execution status
                execution.status = (
                    PlaybookStatus.COMPLETED.value
                    if steps_failed == 0
                    else PlaybookStatus.FAILED.value
                )
                execution.completed_at = datetime.utcnow()

                # Update playbook statistics
                playbook.execution_count += 1
                if steps_failed == 0:
                    playbook.success_count += 1
                else:
                    playbook.failure_count += 1

                # Add timeline event
                timeline = IncidentTimeline(
                    incident_id=UUID(incident_id),
                    event_type="playbook_executed",
                    description=f"Playbook '{playbook.name}' executed",
                    is_automated=True,
                    changes={
                        "playbook_id": playbook_id,
                        "execution_id": str(execution.id),
                        "status": execution.status,
                    },
                )
                db.add(timeline)

                await db.commit()

                return steps_executed, steps_failed, str(execution.id)

        steps_executed, steps_failed, execution_id = run_async(_execute())

        logger.info(
            f"Playbook execution completed: {steps_executed} succeeded, {steps_failed} failed"
        )

        return {
            "status": "success" if steps_failed == 0 else "partial",
            "incident_id": incident_id,
            "playbook_id": playbook_id,
            "execution_id": execution_id,
            "steps_executed": steps_executed,
            "steps_failed": steps_failed,
        }

    except Exception as e:
        logger.error(f"Playbook execution failed: {e}")
        raise


@celery_app.task(name="app.workers.tasks.incidents.calculate_metrics")
def calculate_incident_metrics(organization_id: str) -> dict:
    """
    Calculate incident metrics for an organization.
    """
    logger.info(f"Calculating metrics for organization {organization_id}")

    try:
        async def _calculate():
            from sqlalchemy import select, func, and_
            from app.models.incident import Incident

            async with AsyncSessionLocal() as db:
                org_id = UUID(organization_id)
                now = datetime.utcnow()
                today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
                week_ago = now - timedelta(days=7)

                # Get resolved incidents for MTTR calculation
                resolved_result = await db.execute(
                    select(Incident)
                    .where(
                        and_(
                            Incident.organization_id == org_id,
                            Incident.status.in_(["resolved", "closed"]),
                            Incident.resolved_at.isnot(None),
                            Incident.resolved_at >= week_ago,
                        )
                    )
                )
                resolved_incidents = resolved_result.scalars().all()

                # Calculate MTTR (Mean Time to Resolve)
                if resolved_incidents:
                    resolution_times = [
                        (i.resolved_at - i.created_at).total_seconds() / 3600
                        for i in resolved_incidents
                        if i.resolved_at and i.created_at
                    ]
                    mttr = sum(resolution_times) / len(resolution_times) if resolution_times else 0
                else:
                    mttr = 0

                # Calculate MTTA (Mean Time to Acknowledge)
                acknowledged_result = await db.execute(
                    select(Incident)
                    .where(
                        and_(
                            Incident.organization_id == org_id,
                            Incident.acknowledged_at.isnot(None),
                            Incident.acknowledged_at >= week_ago,
                        )
                    )
                )
                acknowledged_incidents = acknowledged_result.scalars().all()

                if acknowledged_incidents:
                    ack_times = [
                        (i.acknowledged_at - i.created_at).total_seconds() / 60
                        for i in acknowledged_incidents
                        if i.acknowledged_at and i.created_at
                    ]
                    mtta = sum(ack_times) / len(ack_times) if ack_times else 0
                else:
                    mtta = 0

                # Count incidents today
                today_count_result = await db.execute(
                    select(func.count(Incident.id))
                    .where(
                        and_(
                            Incident.organization_id == org_id,
                            Incident.created_at >= today_start,
                        )
                    )
                )
                incidents_today = today_count_result.scalar() or 0

                # Calculate resolution rate (last 7 days)
                total_result = await db.execute(
                    select(func.count(Incident.id))
                    .where(
                        and_(
                            Incident.organization_id == org_id,
                            Incident.created_at >= week_ago,
                        )
                    )
                )
                total_count = total_result.scalar() or 0

                resolution_rate = (
                    len(resolved_incidents) / total_count if total_count > 0 else 0
                )

                return {
                    "mttr_hours": round(mttr, 2),
                    "mtta_minutes": round(mtta, 2),
                    "incidents_today": incidents_today,
                    "resolution_rate": round(resolution_rate, 2),
                    "resolved_last_7_days": len(resolved_incidents),
                    "total_last_7_days": total_count,
                }

        metrics = run_async(_calculate())

        logger.info(f"Metrics calculated for {organization_id}: {metrics}")

        return {
            "status": "success",
            "organization_id": organization_id,
            "metrics": metrics,
        }

    except Exception as e:
        logger.error(f"Metrics calculation failed: {e}")
        raise
