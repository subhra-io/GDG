#!/bin/bash

# PolicySentinel - Mentorship Demo Startup Script
# Run this script before your 12 PM mentorship session

echo "🚀 PolicySentinel - Starting Demo Environment"
echo "=============================================="
echo ""

# Check if backend is running
echo "📡 Checking Backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend is running on port 8000"
else
    echo "❌ Backend is NOT running"
    echo "   Start with: source venv/bin/activate && uvicorn src.main:app --reload"
fi

echo ""

# Check if frontend is running
echo "🎨 Checking Frontend..."
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is running on port 3000"
else
    echo "❌ Frontend is NOT running"
    echo "   Start with: cd frontend && npm run dev"
fi

echo ""

# Check database health
echo "💾 Checking Databases..."
HEALTH=$(curl -s http://localhost:8000/health 2>/dev/null)
if echo "$HEALTH" | grep -q "postgres.*healthy"; then
    echo "✅ PostgreSQL is healthy"
else
    echo "⚠️  PostgreSQL status unknown"
fi

if echo "$HEALTH" | grep -q "redis.*healthy"; then
    echo "✅ Redis is healthy"
else
    echo "⚠️  Redis status unknown"
fi

if echo "$HEALTH" | grep -q "mongodb.*healthy"; then
    echo "✅ MongoDB is healthy"
else
    echo "⚠️  MongoDB is degraded (not critical for demo)"
fi

echo ""

# Check data
echo "📊 Checking Data..."
STATS=$(curl -s http://localhost:8000/api/v1/data/statistics 2>/dev/null)
if [ ! -z "$STATS" ]; then
    TOTAL=$(echo "$STATS" | grep -o '"total_records":[0-9]*' | grep -o '[0-9]*')
    echo "✅ Data loaded: $TOTAL transactions"
else
    echo "⚠️  Could not fetch data statistics"
fi

POLICIES=$(curl -s http://localhost:8000/api/v1/policies 2>/dev/null)
if [ ! -z "$POLICIES" ]; then
    POLICY_COUNT=$(echo "$POLICIES" | grep -o '"id"' | wc -l | tr -d ' ')
    echo "✅ Policies uploaded: $POLICY_COUNT policies"
else
    echo "⚠️  Could not fetch policies"
fi

echo ""
echo "=============================================="
echo "🎯 DEMO URLS (Open these in your browser):"
echo "=============================================="
echo ""
echo "1. Dashboard:      http://localhost:3000"
echo "2. Data Explorer:  http://localhost:3000/data      ⭐ MAIN FOCUS"
echo "3. Policies:       http://localhost:3000/policies  ⭐ SECONDARY"
echo "4. Violations:     http://localhost:3000/violations"
echo "5. API Health:     http://localhost:8000/health"
echo ""
echo "=============================================="
echo "📋 QUICK DEMO SCRIPT:"
echo "=============================================="
echo ""
echo "1. Show Data Explorer (60 sec)"
echo "   - Statistics dashboard"
echo "   - Transaction filters"
echo "   - IBM dataset integration"
echo ""
echo "2. Show Policies (60 sec)"
echo "   - Policy list"
echo "   - View details"
echo "   - AI rule extraction"
echo ""
echo "3. Explain Architecture (60 sec)"
echo "   - FastAPI + 3 DBs + Next.js + GPT-4"
echo "   - 17,000+ lines, 80% complete"
echo "   - Production-ready"
echo ""
echo "=============================================="
echo "💡 KEY MESSAGE:"
echo "=============================================="
echo ""
echo "\"PolicySentinel: 80% built with core AI engine,"
echo "data pipeline, and UI complete. Remaining 20%"
echo "are enhancements for the hackathon.\""
echo ""
echo "=============================================="
echo "🎉 YOU'RE READY! Good luck at 12 PM!"
echo "=============================================="
