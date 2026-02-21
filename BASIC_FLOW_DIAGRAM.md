# 🔄 PolicySentinel - Basic Flow (Current Implementation)

## ✅ Your Current Flow - Exactly Right!

```
┌─────────────────────────────────────────────────────────────────┐
│                    POLICYSENTINEL FLOW                          │
└─────────────────────────────────────────────────────────────────┘

1️⃣ POLICY UPLOAD
   ┌──────────────┐
   │ User uploads │
   │  Policy PDF  │
   └──────┬───────┘
          │
          ▼
   ┌──────────────────┐
   │ PDF Extractor    │  ← PyPDF2
   │ Extract text     │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ GPT-4 / Gemini   │  ← LLM Router
   │ Convert to       │
   │ Structured Rules │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ PostgreSQL       │
   │ Store Rules      │
   └──────────────────┘


2️⃣ VIOLATION SCANNING
   ┌──────────────────┐
   │ Trigger Scan     │  ← Manual or Scheduled (Celery)
   │ (Manual/Auto)    │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Load Rules       │  ← From PostgreSQL
   │ from Database    │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Load Company     │  ← From PostgreSQL
   │ Records          │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Validation       │  ← ViolationDetector
   │ Engine           │     Compare records vs rules
   │ Compare & Check  │
   └──────┬───────────┘
          │
          ├─── No Violation → Continue
          │
          └─── Violation Found ▼
               ┌──────────────────┐
               │ GPT-4 / Gemini   │  ← Generate Justification
               │ Generate         │
               │ Justification    │
               └──────┬───────────┘
                      │
                      ▼
               ┌──────────────────┐
               │ GPT-4 / Gemini   │  ← Generate Remediation
               │ Generate         │
               │ Remediation      │
               └──────┬───────────┘
                      │
                      ▼
               ┌──────────────────┐
               │ Risk Scoring     │  ← Calculate Risk (0-100)
               │ Engine           │     4 factors
               └──────┬───────────┘
                      │
                      ▼
               ┌──────────────────┐
               │ PostgreSQL       │
               │ Store Violation  │
               └──────────────────┘


3️⃣ DASHBOARD DISPLAY
   ┌──────────────────┐
   │ Load Violations  │  ← From PostgreSQL
   │ from Database    │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Calculate        │  ← Aggregate metrics
   │ Compliance Score │
   └──────┬───────────┘
          │
          ▼
   ┌──────────────────┐
   │ Display on       │  ← Next.js Frontend
   │ Dashboard        │
   │ • Violations     │
   │ • Severity       │
   │ • Risk Scores    │
   │ • Compliance %   │
   └──────────────────┘
```

---

## 📊 Detailed Component Breakdown

### 1️⃣ Policy Upload & Rule Extraction

**API Endpoint**: `POST /api/v1/policies/upload`

**Flow**:
```python
# 1. Upload PDF
file = request.files['file']

# 2. Extract text
pdf_extractor = PDFExtractor()
text = pdf_extractor.extract_text(file)

# 3. Send to LLM (GPT-4 or Gemini)
llm_router = LLMRouter()
rules = llm_router.extract_rules(text)

# 4. Store in PostgreSQL
for rule in rules:
    db.add(ComplianceRule(
        description=rule['description'],
        severity=rule['severity'],
        policy_id=policy.id
    ))
db.commit()
```

**Files Involved**:
- `src/routes/policy.py` - Upload endpoint
- `src/services/pdf_extractor.py` - Text extraction
- `src/services/rule_extractor.py` - LLM rule extraction
- `src/services/llm/router.py` - Multi-LLM routing
- `src/models/rule.py` - Rule database model

---

### 2️⃣ Violation Scanning & Detection

**API Endpoint**: `POST /api/v1/violations/scan`

**Flow**:
```python
# 1. Load all active rules
rules = db.query(ComplianceRule).filter(
    ComplianceRule.is_active == True
).all()

# 2. Load company records
records = db.query(CompanyRecord).all()

# 3. For each record, check against each rule
violation_detector = ViolationDetector(db)
for record in records:
    for rule in rules:
        # Validation logic
        is_violated = violation_detector.check_rule(record, rule)
        
        if is_violated:
            # 4. Generate justification (GPT-4)
            justification = llm_router.generate_justification(
                rule, record
            )
            
            # 5. Generate remediation (GPT-4)
            remediation = llm_router.generate_remediation(
                rule, record
            )
            
            # 6. Calculate risk score
            risk_engine = RiskScoringEngine()
            risk_score = risk_engine.calculate_risk(
                severity=rule.severity,
                amount=record.amount,
                frequency=record.frequency,
                history=record.history
            )
            
            # 7. Store violation
            db.add(Violation(
                rule_id=rule.id,
                record_id=record.id,
                justification=justification,
                remediation=remediation,
                risk_score=risk_score,
                severity=rule.severity
            ))
db.commit()
```

**Files Involved**:
- `src/routes/violations.py` - Scan endpoint
- `src/services/violation_detector.py` - Validation engine
- `src/services/risk_scoring.py` - Risk calculation
- `src/prompts/justification.py` - Justification prompt
- `src/prompts/remediation.py` - Remediation prompt
- `src/models/violation.py` - Violation database model

---

### 3️⃣ Dashboard Display

**API Endpoint**: `GET /api/v1/dashboard/metrics`

**Flow**:
```python
# 1. Count violations
total_violations = db.query(Violation).count()

# 2. Count by severity
violations_by_severity = {
    'critical': db.query(Violation).filter(
        Violation.severity == 'critical'
    ).count(),
    'high': db.query(Violation).filter(
        Violation.severity == 'high'
    ).count(),
    # ... etc
}

# 3. Calculate compliance score
violation_detector = ViolationDetector()
compliance_score = violation_detector.calculate_risk_score(
    violations
)

# 4. Return metrics
return {
    'total_violations': total_violations,
    'violations_by_severity': violations_by_severity,
    'compliance_score': compliance_score,
    'total_rules': total_rules,
    'total_records': total_records
}
```

**Frontend Display**:
```typescript
// Load metrics
const metrics = await getDashboardMetrics();

// Display on dashboard
<ComplianceGauge score={metrics.compliance_score} />
<MetricCard title="Total Violations" value={metrics.total_violations} />
<ViolationTable violations={violations} />
```

**Files Involved**:
- `src/routes/dashboard.py` - Metrics endpoint
- `frontend/app/page.tsx` - Dashboard page
- `frontend/components/ComplianceGauge.tsx` - Score gauge
- `frontend/components/ViolationTable.tsx` - Violations table

---

## 🔄 Background Processing (Bonus)

You also have **continuous monitoring** running in the background:

```
┌──────────────────┐
│ Celery Beat      │  ← Scheduler
│ Every 5 minutes  │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Celery Worker    │  ← Background task
│ Run Scan         │
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│ Same Scan Flow   │  ← Steps 2️⃣ above
│ as Manual Scan   │
└──────────────────┘
```

**Files Involved**:
- `src/workers/celery_app.py` - Celery configuration
- `src/workers/tasks.py` - Background tasks
- `src/routes/monitoring.py` - Monitoring endpoints

---

## 🎯 Key Components Summary

| Component | Purpose | Status |
|-----------|---------|--------|
| **PDF Extractor** | Extract text from PDF | ✅ Working |
| **Rule Extractor** | LLM converts text to rules | ✅ Working |
| **Validation Engine** | Compare records vs rules | ✅ Working |
| **Justification Generator** | Explain why violation occurred | ✅ Working |
| **Remediation Generator** | Suggest how to fix | ✅ Working |
| **Risk Scoring Engine** | Calculate risk (0-100) | ✅ Working |
| **Dashboard** | Display violations & metrics | ✅ Working |
| **Background Workers** | Continuous monitoring | ✅ Working |
| **Multi-LLM Router** | OpenAI + Gemini fallback | ✅ Working |

---

## 💡 Enhanced Features (Beyond Basic Flow)

You've also added these enhancements:

### 1. Risk Scoring (4-Factor Algorithm)
```python
risk_score = (
    severity_weight +      # 10-40 points
    amount_factor +        # 0-25 points
    frequency_factor +     # 0-20 points
    historical_factor      # 0-15 points
)
# Total: 0-100
```

### 2. Reasoning Traces (Transparent AI)
```python
# Generate step-by-step reasoning
reasoning_trace = [
    {
        "step": 1,
        "description": "Evaluated transaction amount",
        "confidence": 95
    },
    {
        "step": 2,
        "description": "Checked against threshold",
        "confidence": 90
    },
    # ... more steps
]
```

### 3. Multi-LLM Support
```python
# Automatic fallback
try:
    result = openai_client.generate(prompt)
except:
    result = gemini_client.generate(prompt)
```

---

## 🎬 Demo Flow (What to Show)

### Step 1: Upload Policy (30 seconds)
1. Navigate to Policies page
2. Upload `sample_aml_policy.pdf`
3. Click "Extract Rules"
4. Show extracted rules in table

### Step 2: Run Scan (30 seconds)
1. Navigate to Dashboard
2. Click "Scan for Violations"
3. Show scanning progress
4. Show violations detected

### Step 3: View Violations (1 minute)
1. Navigate to Violations page
2. Show risk scores (95, 90, 85, 80, 75)
3. Show color-coded badges
4. Click on a violation
5. Show justification and remediation

### Step 4: Explain Architecture (1 minute)
1. Show this flow diagram
2. Explain: "PDF → Rules → Scan → Violations → Dashboard"
3. Highlight unique features:
   - Risk scoring
   - Reasoning traces
   - Multi-LLM
   - Background workers

---

## ✅ Your Understanding is Perfect!

You've described the flow exactly right:

1. ✅ User uploads policy PDF
2. ✅ Extract text and send to GPT-4
3. ✅ Convert to structured rules
4. ✅ Store in PostgreSQL
5. ✅ Run scan comparing records vs rules
6. ✅ Generate justification and remediation
7. ✅ Display on dashboard with severity and compliance score

**Plus you've added**:
- Risk scoring (4-factor algorithm)
- Reasoning traces (transparent AI)
- Multi-LLM support (OpenAI + Gemini)
- Background workers (continuous monitoring)

---

## 🚀 For Your Demo

**Opening line**: 
"PolicySentinel automates compliance monitoring. Here's the flow: Upload a policy PDF, our AI extracts structured rules, we scan company records against those rules, and generate explainable violations with remediation guidance. The dashboard shows everything with risk scores and compliance metrics."

**Then show it working live!**

Good luck! 🎯
