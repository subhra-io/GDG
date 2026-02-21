"""Celery application configuration."""

from celery import Celery
from celery.schedules import crontab
from src.config.settings import settings

# Create Celery app
celery_app = Celery(
    "policysentinel",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["src.workers.tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

# Periodic tasks schedule
celery_app.conf.beat_schedule = {
    "continuous-monitoring": {
        "task": "src.workers.tasks.continuous_monitoring_task",
        "schedule": 300.0,  # Every 5 minutes
    },
    "cleanup-old-jobs": {
        "task": "src.workers.tasks.cleanup_old_jobs_task",
        "schedule": crontab(hour=2, minute=0),  # Daily at 2 AM
    },
}
