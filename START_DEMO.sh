#!/bin/bash

echo "🚀 Starting PolicySentinel Demo..."
echo ""

# Activate virtual environment
source venv/bin/activate

# Start backend in background
echo "📡 Starting backend on port 8000..."
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 5

# Start frontend in background
echo "🎨 Starting frontend on port 3003..."
cd frontend
npm run dev -- -p 3003 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Services started!"
echo ""
echo "📊 Backend:  http://localhost:8000"
echo "🌐 Frontend: http://localhost:3003"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "💡 Demo data already loaded:"
echo "   - 3 compliance rules"
echo "   - 5 violations with risk scores"
echo "   - 36 company records"
echo ""
echo "🎯 Key Features to Show:"
echo "   1. Risk Scoring - Color-coded badges in violation table"
echo "   2. Reasoning Traces - Click any violation to see AI explanation"
echo "   3. Multi-LLM Support - Check /api/v1/llm/metrics"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for user interrupt
trap "echo ''; echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait
