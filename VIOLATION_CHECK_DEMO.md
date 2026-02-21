# ✅ How to Check Violations - SIMPLE VERSION

## 🎯 3 Simple Ways

### Method 1: Frontend (Easiest)
```
1. Open: http://localhost:3000/violations
2. Click: "Scan for Violations" button
3. See: Violations appear in table
```

### Method 2: API (For Testing)
```bash
# Trigger scan
curl -X POST http://localhost:8000/api/v1/violations/scan

# View results
curl http://localhost:8000/api/v1/violations
```

### Method 3: Pre-loaded (Fastest)
```bash
# Creates 13 violations instantly
python scripts/create_test_scenarios.py

# Then view at: http://localhost:3000/violations
```

---

## 🚀 Current Status

**Your System Right Now:**
- ✅ Backend: Running
- ✅ Frontend: Running  
- ✅ Records: 20 transactions loaded
- ❌ Rules: 0 active rules
- ❌ Violations: 0 (because no rules)

**To Get Violations:**

You need **rules** first! Here's how:

---

## 🔧 Quick Fix: Load Demo Data

Run this ONE command:

```bash
python scripts/create_test_scenarios.py
```

**This creates:**
- ✅ 3 sample policies (AML, GDPR, SOX)
- ✅ 10 compliance rules
- ✅ 13 violation records
- ✅ AI justifications
- ✅ AI remediation steps

**Then check:**
```
http://localhost:3000/violations
```

You'll see 13 violations ready to demo! 🎉

---

## 🎬 For Your Demo

### Before Demo (Run Once):
```bash
python scripts/create_test_scenarios.py
```

### During Demo:

**1. Dashboard (30 sec)**
- Show: "13 violations detected"
- Show: Risk score

**2. Violations Page (30 sec)**
- Show: Table with 13 violations
- Point out: Different severities (Critical, High, Medium)

**3. Click One Violation (60 sec)** ⭐ **MONEY SHOT**
- Show: Which rule was violated
- Show: Actual transaction data
- Show: **AI Justification** (why it's bad)
- Show: **AI Remediation** (how to fix)

**4. Close (10 sec)**
"From policy to action in seconds."

---

## 🧪 Test Right Now

```bash
# 1. Check current violations
curl http://localhost:8000/api/v1/violations

# Should return: [] (empty - no violations yet)

# 2. Load demo data
python scripts/create_test_scenarios.py

# 3. Check again
curl http://localhost:8000/api/v1/violations

# Should return: Array with 13 violations!
```

---

## ❓ Why No Violations?

**Violations = Records that break Rules**

Right now:
- ✅ You have 20 records (transactions)
- ❌ You have 0 rules (nothing to check against)
- = 0 violations

**After running test scenarios:**
- ✅ You have 20 records
- ✅ You have 10 rules
- ✅ 13 records break rules
- = 13 violations! 🎉

---

## 🎯 Bottom Line

**Run this now:**
```bash
python scripts/create_test_scenarios.py
```

**Then open:**
```
http://localhost:3000/violations
```

**You'll see violations ready to demo!** ✅
