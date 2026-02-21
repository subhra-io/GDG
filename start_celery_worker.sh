#!/bin/bash

# Start Celery worker for PolicySentinel

echo "🚀 Starting Celery Worker..."

celery -A src.workers.celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --max-tasks-per-child=100 \
    --time-limit=1800 \
    --soft-time-limit=1500

