#!/bin/bash

# Start Celery Beat scheduler for PolicySentinel

echo "⏰ Starting Celery Beat Scheduler..."

celery -A src.workers.celery_app beat \
    --loglevel=info \
    --scheduler=celery.beat:PersistentScheduler

