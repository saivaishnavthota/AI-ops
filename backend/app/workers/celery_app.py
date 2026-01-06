"""
Celery application configuration for background task processing.
"""

from celery import Celery
from celery.schedules import crontab

from app.config.settings import settings

# Create Celery app
celery_app = Celery(
    "aiops_worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,

    # Task execution settings
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=300,  # 5 minutes
    task_soft_time_limit=240,  # 4 minutes

    # Worker settings
    worker_prefetch_multiplier=1,
    worker_concurrency=4,

    # Result settings
    result_expires=3600,  # 1 hour

    # Task routing
    task_routes={
        "app.workers.tasks.alerts.*": {"queue": "alerts"},
        "app.workers.tasks.incidents.*": {"queue": "incidents"},
        "app.workers.tasks.notifications.*": {"queue": "notifications"},
        "app.workers.tasks.reports.*": {"queue": "reports"},
    },

    # Beat schedule for periodic tasks
    beat_schedule={
        # Check for stale incidents every 5 minutes
        "check-stale-incidents": {
            "task": "app.workers.tasks.incidents.check_stale_incidents",
            "schedule": crontab(minute="*/5"),
        },
        # Generate daily summary reports at 6 AM UTC
        "generate-daily-report": {
            "task": "app.workers.tasks.reports.generate_daily_summary",
            "schedule": crontab(hour=6, minute=0),
        },
        # Cleanup old resolved alerts weekly
        "cleanup-old-alerts": {
            "task": "app.workers.tasks.alerts.cleanup_old_alerts",
            "schedule": crontab(day_of_week=0, hour=2, minute=0),
        },
        # Health check every minute
        "worker-health-check": {
            "task": "app.workers.tasks.health.check_worker_health",
            "schedule": crontab(minute="*"),
        },
    },
)

# Auto-discover tasks from the tasks module
celery_app.autodiscover_tasks(["app.workers.tasks"])
