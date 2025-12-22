"""
Alert-related background tasks with AI integration.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
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


@celery_app.task(name="app.workers.tasks.alerts.correlate_alerts")
def correlate_alerts(organization_id: str, time_window_minutes: int = 30) -> dict:
    """
    Use AI to correlate related alerts to reduce noise.
    """
    logger.info(f"Starting AI alert correlation for org {organization_id}")

    try:
        async def _correlate():
            async with AsyncSessionLocal() as db:
                async with AIService(db) as ai:
                    result = await ai.correlate_alerts(
                        organization_id=UUID(organization_id),
                        time_window_minutes=time_window_minutes,
                    )
                    return result

        result = run_async(_correlate())

        correlation = result["correlation"]
        groups_count = len(correlation.get("groups", []))
        uncorrelated_count = len(correlation.get("uncorrelated_ids", []))

        logger.info(
            f"Alert correlation completed: {groups_count} groups found, "
            f"{uncorrelated_count} uncorrelated alerts"
        )

        return {
            "status": "success",
            "organization_id": organization_id,
            "groups": groups_count,
            "uncorrelated": uncorrelated_count,
            "analysis_summary": correlation.get("analysis_summary", ""),
            "correlation_details": correlation,
        }

    except Exception as e:
        logger.error(f"Alert correlation failed: {e}")
        raise


@celery_app.task(name="app.workers.tasks.alerts.create_incidents_from_correlations")
def create_incidents_from_correlations(organization_id: str, correlation_data: dict) -> dict:
    """
    Create incidents from correlated alert groups.
    """
    logger.info(f"Creating incidents from correlations for org {organization_id}")

    try:
        async def _create_incidents():
            from sqlalchemy import select
            from app.models.incident import Incident
            from app.models.alert import Alert
            from app.services.incident_service import IncidentService

            created_incidents = []

            async with AsyncSessionLocal() as db:
                incident_service = IncidentService(db)

                for group in correlation_data.get("groups", []):
                    # Skip low confidence correlations
                    if group.get("confidence", 0) < 0.6:
                        continue

                    alert_ids = group.get("alert_ids", [])
                    if not alert_ids:
                        continue

                    # Fetch alerts in this group
                    result = await db.execute(
                        select(Alert).where(
                            Alert.id.in_([UUID(aid) for aid in alert_ids])
                        )
                    )
                    alerts = result.scalars().all()

                    if not alerts:
                        continue

                    # Create incident from correlation
                    first_alert = alerts[0]
                    incident = await incident_service.create(
                        organization_id=UUID(organization_id),
                        data={
                            "title": group.get("suggested_incident_title", f"Correlated alerts: {first_alert.title}"),
                            "description": f"Auto-created from {len(alerts)} correlated alerts.\n\n{group.get('reasoning', '')}",
                            "priority": group.get("suggested_incident_priority", "p3"),
                            "severity": first_alert.severity or "medium",
                            "category": first_alert.source_type or "monitoring",
                            "affected_services": list(set(a.service for a in alerts if a.service)),
                        },
                    )

                    # Link alerts to incident
                    for alert in alerts:
                        alert.incident_id = incident.id
                        alert.status = "acknowledged"

                    # Store correlation metadata
                    if not incident.extra_data:
                        incident.extra_data = {}
                    incident.extra_data["correlation"] = {
                        "type": group.get("correlation_type"),
                        "confidence": group.get("confidence"),
                        "root_cause_alert_id": group.get("root_cause_id"),
                        "alert_count": len(alerts),
                    }

                    await db.commit()
                    created_incidents.append({
                        "incident_id": str(incident.id),
                        "alert_count": len(alerts),
                        "title": incident.title,
                    })

            return created_incidents

        created = run_async(_create_incidents())

        logger.info(f"Created {len(created)} incidents from correlations")

        return {
            "status": "success",
            "organization_id": organization_id,
            "incidents_created": len(created),
            "incidents": created,
        }

    except Exception as e:
        logger.error(f"Incident creation from correlations failed: {e}")
        raise


@celery_app.task(name="app.workers.tasks.alerts.cleanup_old_alerts")
def cleanup_old_alerts(days: int = 30) -> dict:
    """
    Clean up old resolved alerts to manage database size.
    """
    logger.info(f"Starting cleanup of alerts older than {days} days")

    try:
        async def _cleanup():
            from sqlalchemy import delete, and_
            from app.models.alert import Alert

            cutoff_date = datetime.utcnow() - timedelta(days=days)

            async with AsyncSessionLocal() as db:
                # Delete old resolved/suppressed alerts
                result = await db.execute(
                    delete(Alert)
                    .where(
                        and_(
                            Alert.status.in_(["resolved", "suppressed"]),
                            Alert.updated_at < cutoff_date,
                        )
                    )
                )
                deleted_count = result.rowcount
                await db.commit()

            return deleted_count, cutoff_date

        deleted_count, cutoff_date = run_async(_cleanup())

        logger.info(f"Cleanup completed: {deleted_count} alerts deleted")

        return {
            "status": "success",
            "deleted": deleted_count,
            "cutoff_date": cutoff_date.isoformat(),
        }

    except Exception as e:
        logger.error(f"Alert cleanup failed: {e}")
        raise


@celery_app.task(name="app.workers.tasks.alerts.process_alert_webhook")
def process_alert_webhook(payload: dict, source: str, organization_id: str) -> dict:
    """
    Process an incoming alert webhook asynchronously.
    """
    logger.info(f"Processing alert webhook from {source}")

    try:
        async def _process():
            from app.services.alert_service import AlertService

            async with AsyncSessionLocal() as db:
                alert_service = AlertService(db)

                # Normalize payload based on source
                normalized = normalize_webhook_payload(payload, source)

                # Create or update alert
                alert = await alert_service.ingest_alert(
                    organization_id=UUID(organization_id),
                    data=normalized,
                )

                return str(alert.id), alert.status

        alert_id, status = run_async(_process())

        logger.info(f"Webhook processed: alert {alert_id} ({status})")

        return {
            "status": "success",
            "source": source,
            "alert_id": alert_id,
            "alert_status": status,
        }

    except Exception as e:
        logger.error(f"Alert webhook processing failed: {e}")
        raise


@celery_app.task(name="app.workers.tasks.alerts.auto_resolve_stale")
def auto_resolve_stale_alerts(hours: int = 24) -> dict:
    """
    Auto-resolve alerts that haven't been updated in the specified time.
    """
    logger.info(f"Auto-resolving alerts stale for {hours} hours")

    try:
        async def _auto_resolve():
            from sqlalchemy import select, and_
            from app.models.alert import Alert

            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            resolved_count = 0

            async with AsyncSessionLocal() as db:
                result = await db.execute(
                    select(Alert)
                    .where(
                        and_(
                            Alert.status.in_(["open", "acknowledged"]),
                            Alert.updated_at < cutoff_time,
                        )
                    )
                )
                stale_alerts = result.scalars().all()

                for alert in stale_alerts:
                    alert.status = "resolved"
                    alert.resolved_at = datetime.utcnow()
                    if not alert.extra_data:
                        alert.extra_data = {}
                    alert.extra_data["auto_resolved"] = True
                    alert.extra_data["auto_resolved_reason"] = f"Stale for {hours} hours"
                    resolved_count += 1

                await db.commit()

            return resolved_count

        resolved_count = run_async(_auto_resolve())

        logger.info(f"Auto-resolved {resolved_count} stale alerts")

        return {
            "status": "success",
            "resolved": resolved_count,
        }

    except Exception as e:
        logger.error(f"Auto-resolve failed: {e}")
        raise


@celery_app.task(name="app.workers.tasks.alerts.run_correlation_cycle")
def run_correlation_cycle() -> dict:
    """
    Run correlation for all organizations with recent alerts.
    """
    logger.info("Starting correlation cycle for all organizations")

    try:
        async def _run_cycle():
            from sqlalchemy import select, func
            from app.models.alert import Alert
            from app.models.organization import Organization

            async with AsyncSessionLocal() as db:
                # Find organizations with recent open alerts
                cutoff = datetime.utcnow() - timedelta(hours=1)
                result = await db.execute(
                    select(Alert.organization_id)
                    .where(
                        Alert.status.in_(["open", "acknowledged"]),
                        Alert.created_at >= cutoff,
                    )
                    .group_by(Alert.organization_id)
                )
                org_ids = [str(row[0]) for row in result.fetchall()]

            return org_ids

        org_ids = run_async(_run_cycle())

        # Queue correlation tasks for each organization
        results = []
        for org_id in org_ids:
            correlate_alerts.delay(org_id)
            results.append(org_id)

        logger.info(f"Queued correlation for {len(results)} organizations")

        return {
            "status": "success",
            "organizations_queued": len(results),
            "organization_ids": results,
        }

    except Exception as e:
        logger.error(f"Correlation cycle failed: {e}")
        raise


def normalize_webhook_payload(payload: dict, source: str) -> dict:
    """
    Normalize webhook payloads from different alert sources.
    """
    # Default normalized structure
    normalized = {
        "title": "",
        "message": "",
        "severity": "medium",
        "source": source,
        "source_type": "webhook",
        "host": None,
        "service": None,
        "tags": [],
        "extra_data": payload,
    }

    if source == "prometheus":
        # Prometheus AlertManager format
        alerts = payload.get("alerts", [payload])
        if alerts:
            alert = alerts[0]
            labels = alert.get("labels", {})
            annotations = alert.get("annotations", {})
            normalized["title"] = labels.get("alertname", "Prometheus Alert")
            normalized["message"] = annotations.get("description", annotations.get("summary", ""))
            normalized["severity"] = labels.get("severity", "medium")
            normalized["host"] = labels.get("instance", labels.get("host"))
            normalized["service"] = labels.get("job", labels.get("service"))
            normalized["tags"] = list(labels.keys())

    elif source == "grafana":
        # Grafana alert format
        normalized["title"] = payload.get("title", payload.get("ruleName", "Grafana Alert"))
        normalized["message"] = payload.get("message", "")
        normalized["severity"] = payload.get("state", "medium").lower()
        if normalized["severity"] == "alerting":
            normalized["severity"] = "high"
        tags = payload.get("tags", {})
        normalized["tags"] = list(tags.keys()) if isinstance(tags, dict) else tags

    elif source == "datadog":
        # Datadog webhook format
        normalized["title"] = payload.get("title", "Datadog Alert")
        normalized["message"] = payload.get("body", "")
        priority = payload.get("priority", "normal")
        normalized["severity"] = {"low": "low", "normal": "medium", "high": "high"}.get(priority, "medium")
        normalized["host"] = payload.get("host")
        normalized["service"] = payload.get("service")
        normalized["tags"] = payload.get("tags", [])

    elif source == "pagerduty":
        # PagerDuty webhook format
        messages = payload.get("messages", [payload])
        if messages:
            msg = messages[0]
            incident = msg.get("incident", {})
            normalized["title"] = incident.get("title", "PagerDuty Alert")
            normalized["message"] = incident.get("description", "")
            urgency = incident.get("urgency", "low")
            normalized["severity"] = {"high": "high", "low": "medium"}.get(urgency, "medium")
            normalized["service"] = incident.get("service", {}).get("name")

    else:
        # Generic format - try common fields
        normalized["title"] = (
            payload.get("title") or
            payload.get("name") or
            payload.get("alert_name") or
            payload.get("summary") or
            "Alert"
        )
        normalized["message"] = (
            payload.get("message") or
            payload.get("description") or
            payload.get("body") or
            payload.get("text") or
            ""
        )
        normalized["severity"] = (
            payload.get("severity") or
            payload.get("priority") or
            payload.get("level") or
            "medium"
        ).lower()
        normalized["host"] = payload.get("host") or payload.get("hostname")
        normalized["service"] = payload.get("service") or payload.get("application")

    return normalized
