# How to Check for Violations - Complete Guide

## 🎯 Quick Answer

There are **3 ways** to check for violations:

1. **Frontend UI** (Easiest - Click button)
2. **API Call** (For testing)
3. **Pre-loaded Demo Data** (Instant results)

---

## Method 1: Frontend UI (Recommended for Demo)

### Step-by-Step:

```bash
# 1. Make sure everything is running
# Backend
uvicorn src.main:app --reload

# Frontend (new terminal)
cd frontend && npm run dev
```

### In Browser:

1. **Go to Dashboard**: http://localhost:3000
2. **Click "Scan for Violations"** button (if available)
   
   OR

3. **Go to Violations page**: http://localhost:3000/violations
4. **Click "Scan Now"** button

### What Happens:
- System checks all records against all active rules
- Creates violations when rules are broken
- Generates AI justifications and remediation steps
- Shows results in violations table

---

## Method 2: API Call (For Testing)

### Trigger Violation Scan:

```bash
# Scan for violations
curl -X POST http://localhost:8000/api/v1/violations/scan

# Response:
{
  "status": "success",
  "message": "Scan completed successfully",
  "rules_scanned": 4,
  "records_scanned": 20,
  "violations_detected": 5
}
```

### View Violations:

```bash
# Get all violations
curl http://localhost:8000/api/v1/violations

# Filter by severity
curl "http://localhost:8000/api/v1/violations?severity=critical"

# Filter by status
curl "http://localhost:8000/api/v1/violations?status=pending_review"

# Get specific violation
curl http://localhost:8000/api/v1/violations/{violation_id}

# Get statistics
curl http://localhost:8000/api/v1/violations/stats/summary
```

---

## Method 3: Pre-loaded Demo Data (Fastest)

### Use Test Scenarios:

```bash
# This creates 13 violations instantly (no scanning needed)
python scripts/create_test_scenarios.py

# What it creates:
# - 5 AML violations (large transactions, rapid transfers)
# - 4 GDPR violations (data retention, consent issues)
# - 3 SOX violations (unauthorized changes, missing approvals)
```

### Then view in frontend:
```
http://localhost:3000/violations
```

---

## 🔍 How Violation Detection Works

### The Process:

```
1. Load Active Rules
   ↓
2. Load Company Records (transactions)
   ↓
3. For each record:
   ↓
4. Check against each rule
   ↓
5. If rule is violated:
   ↓
6. Generate AI justification (why it's a violation)
   ↓
7. Generate AI remediation steps (how to fix)
   ↓
8. Save violation to database
```

### Example Rule:

```json
{
  "description": "Transactions exceeding $10,000 require approval",
  "validation_logic": {
    "condition": {
      "field": "amount",
      "operator": "greater_than",
      "value": 10000
    }
  },
  "severity": "high"
}
```

### Example Record:

```json
{
  "transaction_id": "TXN000123",
  "amount": 15000,
  "transaction_type": "TRANSFER",
  "from_account": "ACC001",
  "to_account": "ACC002"
}
```

### Result:

```
✅ VIOLATION DETECTED!

Rule: Transactions exceeding $10,000 require approval
Record: TXN000123 ($15,000)
Severity: HIGH

AI Justification:
"This transaction of $15,000 exceeds the $10,000 threshold 
requiring managerial approval. No approval record was found 
in the system, violating AML policy section 2.1."

AI Remediation:
1. [CRITICAL] Obtain retroactive approval from authorized manager
2. [HIGH] Document approval in compliance system
3. [MEDIUM] Review similar transactions in past 30 days
4. [LOW] Update transaction processing workflow
```

---

## 🎬 Demo Flow (Recommended)

### Option A: Live Scan (If MongoDB working)

```bash
# 1. Upload policy
# (via frontend UI)

# 2. Extract rules
# (click "Extract Rules" button)

# 3. Load sample data
python scripts/create_test_scenarios.py

# 4. Scan for violations
# (click "Scan Now" button in UI)

# 5. View results
# (violations appear in table)
```

### Option B: Pre-loaded Demo (Safer)

```bash
# 1. Load everything at once
python scripts/setup_demo.py

# This creates:
# - Sample policies
# - Extracted rules
# - Sample transactions
# - Detected violations

# 2. Just show the results
# Open http://localhost:3000/violations
```

---

## 🧪 Testing Violation Detection

### Test 1: Check if rules exist

```bash
curl http://localhost:8000/api/v1/policies

# Should show policies with rules
```

### Test 2: Check if records exist

```bash
curl http://localhost:8000/api/v1/data/records

# Should show transaction records
```

### Test 3: Trigger scan

```bash
curl -X POST http://localhost:8000/api/v1/violations/scan

# Should return:
# - rules_scanned: > 0
# - records_scanned: > 0
# - violations_detected: > 0
```

### Test 4: View violations

```bash
curl http://localhost:8000/api/v1/violations

# Should return array of violations
```

---

## 🚨 Troubleshooting

### "No active rules to scan"

**Problem**: No rules in database

**Solution**:
```bash
# Option 1: Upload policy and extract rules
# (via frontend)

# Option 2: Use setup script
python scripts/setup_demo.py
```

### "No records to scan"

**Problem**: No transaction records in database

**Solution**:
```bash
# Create test scenarios
python scripts/create_test_scenarios.py

# OR load IBM dataset
python scripts/load_ibm_dataset.py --path data/HI-Small_Trans.csv
```

### "Violations detected: 0"

**Problem**: Records don't violate any rules

**Solution**:
```bash
# Use test scenarios (guaranteed violations)
python scripts/create_test_scenarios.py

# This creates records specifically designed to violate rules
```

### "Internal Server Error"

**Problem**: Database connection issue

**Solution**:
```bash
# Check health
curl http://localhost:8000/health

# Should show:
# - postgres: healthy
# - mongodb: healthy (or can work without it)
# - redis: healthy
```

---

## 📊 What Gets Checked

### Supported Rule Types:

1. **Amount Thresholds**
   - `amount > 10000` → High-value transaction
   - `amount < 100` → Suspicious small amount

2. **Transaction Patterns**
   - Multiple transactions in short time
   - Rapid transfers between accounts
   - Structuring (amounts just below threshold)

3. **Data Compliance**
   - Data retention periods
   - Missing consent records
   - Incomplete audit trails

4. **Access Control**
   - Unauthorized changes
   - Missing approvals
   - Segregation of duties violations

### Supported Operators:

- `greater_than` - Numeric comparison
- `less_than` - Numeric comparison
- `equals` - Exact match
- `not_equals` - Not equal
- `contains` - String contains
- `not_contains` - String doesn't contain
- `regex_match` - Pattern matching
- `is_null` - Field is missing
- `is_not_null` - Field exists

---

## 🎯 For Your Demo

### Recommended Approach:

**Before Demo:**
```bash
# Run this once
python scripts/create_test_scenarios.py
```

**During Demo:**

1. **Show Dashboard** - "Here's our compliance status"
2. **Go to Violations** - "We detected 13 violations"
3. **Click one violation** - "Here's the AI analysis"
4. **Show justification** - "Why it's a violation"
5. **Show remediation** - "How to fix it"

**Key Message:**
"PolicySentinel automatically monitors all transactions, 
detects violations, and provides AI-powered guidance 
for remediation."

---

## 💡 Pro Tips

1. **Use test scenarios** - Guaranteed violations for demo
2. **Pre-load data** - Don't scan live during demo (risky)
3. **Show one violation in detail** - That's where AI shines
4. **Focus on remediation steps** - That's the wow factor
5. **Keep it simple** - Don't explain the detection algorithm

---

## 📝 Quick Commands Cheat Sheet

```bash
# Create demo data with violations
python scripts/create_test_scenarios.py

# Scan for violations (API)
curl -X POST http://localhost:8000/api/v1/violations/scan

# View violations (API)
curl http://localhost:8000/api/v1/violations

# View in browser
http://localhost:3000/violations

# Check system health
curl http://localhost:8000/health
```

---

## ✅ Success Checklist

Before demo, verify:

- [ ] Backend running (port 8000)
- [ ] Frontend running (port 3000)
- [ ] PostgreSQL healthy
- [ ] Test scenarios loaded
- [ ] Violations visible in UI
- [ ] Can click violation and see details
- [ ] AI justification shows
- [ ] AI remediation shows

**If all checked → You're ready to demo! 🚀**
