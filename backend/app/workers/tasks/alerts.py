"""
Alert-related background tasks.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from app.workers.celery_app import celery_app
from app.config.database import AsyncSessionLocal

logger = logging.getLogger(__name__)


def run_async(coro):
    """Helper to run async code in Celery tasks."""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()





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
