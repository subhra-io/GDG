# 🚀 PolicySentinel Quick Start

Get PolicySentinel running in 5 minutes!

## Prerequisites Check

```bash
# Check Python version (need 3.11+)
python3 --version

# Check if databases are installed
psql --version
mongod --version
redis-server --version
```

## Step 1: Install Dependencies (2 minutes)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

## Step 2: Configure Environment (1 minute)

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your OpenAI API key
# OPENAI_API_KEY=sk-your-key-here
```

**Get OpenAI API Key**: https://platform.openai.com/api-keys

## Step 3: Start Databases (1 minute)

```bash
# PostgreSQL
createdb policysentinel

# MongoDB (should auto-start)
# If not: brew services start mongodb-community  # macOS
#         sudo systemctl start mongod             # Linux

# Redis (should auto-start)
# If not: brew services start redis              # macOS
#         sudo systemctl start redis              # Linux
```

## Step 4: Initialize System (30 seconds)

```bash
# Setup database and load sample data
python scripts/setup_demo.py

# Create sample policy PDF
pip install reportlab
python scripts/create_sample_policy.py
```

## Step 5: Start Server (30 seconds)

```bash
# Start the API server
python src/main.py
```

Server running at: http://localhost:8000
API Docs: http://localhost:8000/docs

## Step 6: Test It! (1 minute)

Open a new terminal and run:

```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Upload policy
curl -X POST "http://localhost:8000/api/v1/policies/upload" \
  -F "file=@sample_aml_policy.pdf"

# Save the policy_id from the response, then:

# 3. Extract rules with AI
curl -X POST "http://localhost:8000/api/v1/policies/{policy_id}/extract-rules"

# 4. Scan for violations
curl -X POST "http://localhost:8000/api/v1/violations/scan"

# 5. View dashboard
curl "http://localhost:8000/api/v1/dashboard/metrics"
```

## 🎉 Success!

You should see:
- ✅ 4 rules extracted from the policy
- ✅ 5-8 violations detected in sample data
- ✅ Compliance score around 70-80
- ✅ AI-generated justifications and remediation steps

## What Just Happened?

1. **Uploaded** a PDF policy document
2. **Extracted** 4 compliance rules using GPT-4
3. **Scanned** 20 sample transactions
4. **Detected** violations automatically
5. **Generated** AI explanations for each violation

## Next Steps

### View in Browser

Open http://localhost:8000/docs for interactive API documentation

### Explore the API

```bash
# List all violations
curl "http://localhost:8000/api/v1/violations"

# Get violation details
curl "http://localhost:8000/api/v1/violations/{violation_id}"

# View risk score
curl "http://localhost:8000/api/v1/dashboard/risk-score"
```

### Try Your Own Policy

1. Create a PDF with compliance rules
2. Upload it via the API
3. Extract rules
4. Scan your data

### Build the Frontend

```bash
# In a new directory
npx create-next-app@latest policy-sentinel-ui
cd policy-sentinel-ui
npm install axios recharts
```

## Troubleshooting

### "Database connection failed"
```bash
# Check if PostgreSQL is running
psql -U postgres -c "SELECT 1"

# If not, start it:
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

### "OpenAI API key not configured"
```bash
# Add your key to .env
echo "OPENAI_API_KEY=sk-your-key-here" >> .env
```

### "No module named 'src'"
```bash
# Make sure you're in the project root directory
pwd  # Should show .../policysentinel

# And virtual environment is activated
which python  # Should show .../venv/bin/python
```

### "Port 8000 already in use"
```bash
# Change port in .env
echo "API_PORT=8001" >> .env
```

## Demo Script for Presentation

```bash
# Terminal 1: Start server
python src/main.py

# Terminal 2: Run demo
# 1. Show health
curl http://localhost:8000/health | jq

# 2. Upload policy
curl -X POST "http://localhost:8000/api/v1/policies/upload" \
  -F "file=@sample_aml_policy.pdf" | jq

# 3. Extract rules (use policy_id from above)
curl -X POST "http://localhost:8000/api/v1/policies/{policy_id}/extract-rules" | jq

# 4. Show extracted rules
curl "http://localhost:8000/api/v1/policies/{policy_id}/rules" | jq

# 5. Scan for violations
curl -X POST "http://localhost:8000/api/v1/violations/scan" | jq

# 6. Show dashboard
curl "http://localhost:8000/api/v1/dashboard/metrics" | jq

# 7. Show violations
curl "http://localhost:8000/api/v1/violations" | jq

# 8. Show violation detail
curl "http://localhost:8000/api/v1/violations/{violation_id}" | jq
```

## Architecture Overview

```
PDF Policy → AI Extraction → Rules → Scan Records → Detect Violations → Dashboard
     ↓            ↓            ↓          ↓              ↓                ↓
  pdfplumber   GPT-4      PostgreSQL  Validation    AI Justification   FastAPI
                                       Engine
```

## Key Features Demonstrated

✅ **AI Rule Extraction** - GPT-4 extracts structured rules from unstructured text
✅ **Automated Scanning** - Checks all records against all rules
✅ **Explainable AI** - Natural language justifications for violations
✅ **Risk Scoring** - Calculates compliance score based on violations
✅ **Remediation** - AI-generated steps to fix violations

## Resources

- Full API Documentation: http://localhost:8000/docs
- Detailed Testing Guide: See `API_TESTING_GUIDE.md`
- Complete README: See `README.md`

## Support

Having issues? Check:
1. All databases are running
2. Virtual environment is activated
3. OpenAI API key is set
4. You're in the project root directory

---

**Ready for Round 3! 🚀**
