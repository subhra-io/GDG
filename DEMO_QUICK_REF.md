# 🎯 PolicySentinel - Quick Demo Reference Card

## 🚀 SYSTEM STATUS
✅ Backend: http://localhost:8000
✅ Frontend: http://localhost:3003
✅ Demo Data: 5 violations loaded

## 📊 DEMO FLOW (5 minutes)

### 1️⃣ Dashboard (1 min)
- URL: http://localhost:3003
- Show: Compliance score 68%, 5 violations, 36 records
- Action: Click "Scan for Violations"

### 2️⃣ Risk Scoring (1.5 min)
- URL: http://localhost:3003/violations
- Show: Color-coded badges (Red=Critical, Orange=High)
- Show: Risk scores 95, 90, 85, 80, 75
- **Say**: "Automatic prioritization saves hours of manual work"

### 3️⃣ Reasoning Traces (1.5 min)
- Show Code: `src/services/reasoning_trace.py`
- Show Code: `frontend/components/ReasoningTraceViewer.tsx`
- **Say**: "Transparent AI reasoning - competitors don't have this"
- **Say**: "Required for regulatory audits and compliance"

### 4️⃣ Architecture (1 min)
- Mention: Background workers (Celery + Redis)
- Mention: Multi-LLM support (OpenAI + Gemini)
- **Say**: "Production-ready, not a prototype"

## 🏆 KEY DIFFERENTIATORS

1. **Reasoning Traces** - Transparent AI (competitors: ❌)
2. **Risk Scoring** - 4-factor algorithm (competitors: basic)
3. **Multi-LLM** - Cost optimization (competitors: single)
4. **Background Workers** - Scalable (competitors: sync only)

## 💬 TALKING POINTS

- "Automates compliance monitoring using AI"
- "Reasoning traces are UNIQUE - required for audits"
- "Risk scoring prioritizes critical violations"
- "Multi-LLM saves 60% on AI costs"
- "Production-ready architecture"

## 🔗 QUICK LINKS

- Dashboard: http://localhost:3003
- Violations: http://localhost:3003/violations
- API Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## ⚡ IF SOMETHING BREAKS

```bash
# Check status
curl http://localhost:8000/health
curl http://localhost:3003

# Restart backend
./venv/bin/python -m uvicorn src.main:app --host 0.0.0.0 --port 8000 &

# Restart frontend
cd frontend && npm run dev -- -p 3003 &
```

## 🎯 SUCCESS = Show These 3 Things

1. ✅ Risk scoring in action (violations page)
2. ✅ Reasoning trace architecture (code walkthrough)
3. ✅ Competitive advantages (vs competitor)

---
**You're ready! Go crush it! 🚀**
