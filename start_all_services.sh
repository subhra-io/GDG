#!/bin/bash

# Start all PolicySentinel services

echo "🚀 Starting PolicySentinel Services..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Start databases
echo "📦 Starting databases (PostgreSQL, MongoDB, Redis)..."
docker-compose up -d

# Wait for databases to be ready
echo "⏳ Waiting for databases to be ready..."
sleep 5

# Start FastAPI backend
echo "🔧 Starting FastAPI backend..."
source venv/bin/activate 2>/dev/null || true
python src/main.py &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start Celery worker
echo "👷 Starting Celery worker..."
celery -A src.workers.celery_app worker --loglevel=info --concurrency=2 &
WORKER_PID=$!
echo "Worker PID: $WORKER_PID"

# Start Celery beat
echo "⏰ Starting Celery beat scheduler..."
celery -A src.workers.celery_app beat --loglevel=info &
BEAT_PID=$!
echo "Beat PID: $BEAT_PID"

# Start frontend (optional)
if [ -d "frontend" ]; then
    echo "🎨 Starting Next.js frontend..."
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    echo "Frontend PID: $FRONTEND_PID"
fi

echo ""
echo "✅ All services started!"
echo ""
echo "📊 Service URLs:"
echo "  - Backend API: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo "  - Frontend: http://localhost:3000"
echo ""
echo "🔍 Monitoring:"
echo "  - Health: http://localhost:8000/health"
echo "  - Monitoring Status: http://localhost:8000/api/v1/monitoring/status"
echo ""
echo "⚠️  Press Ctrl+C to stop all services"
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping all services...'; kill $BACKEND_PID $WORKER_PID $BEAT_PID $FRONTEND_PID 2>/dev/null; docker-compose down; echo '✅ All services stopped'; exit 0" INT

# Keep script running
wait
