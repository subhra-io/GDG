# PolicySentinel API Testing Guide

Complete guide for testing the PolicySentinel API endpoints.

## Setup

1. Make sure the server is running:
```bash
python src/main.py
```

2. Server should be available at: `http://localhost:8000`

## Test Flow

### 1. Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "postgres": "healthy",
  "mongodb": "healthy",
  "redis": "healthy"
}
```

### 2. Upload Policy Document

First, create a sample policy:
```bash
python scripts/create_sample_policy.py
```

Then upload it:
```bash
curl -X POST "http://localhost:8000/api/v1/policies/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_aml_policy.pdf"
```

Expected response:
```json
{
  "policy_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "sample_aml_policy.pdf",
  "status": "processed",
  "message": "Policy uploaded and processed successfully"
}
```

Save the `policy_id` for next steps.

### 3. List Policies

```bash
curl http://localhost:8000/api/v1/policies
```

### 4. Get Policy Details

```bash
curl http://localhost:8000/api/v1/policies/{policy_id}
```

### 5. Extract Rules Using AI

**Important**: Make sure you have set `OPENAI_API_KEY` in your `.env` file!

```bash
curl -X POST "http://localhost:8000/api/v1/policies/{policy_id}/extract-rules"
```

Expected response:
```json
{
  "policy_id": "550e8400-e29b-41d4-a716-446655440000",
  "rules_extracted": 4,
  "rules": [
    {
      "id": "...",
      "description": "Any single transaction exceeding $10,000 must be flagged",
      "severity": "high",
      "validation_logic": {
        "field": "amount",
        "operator": "greater_than",
        "value": "10000"
      },
      ...
    }
  ],
  "status": "success",
  "message": "Extracted 4 rules successfully"
}
```

### 6. View Extracted Rules

```bash
curl http://localhost:8000/api/v1/policies/{policy_id}/rules
```

### 7. Scan for Violations

This will check all company records against the extracted rules:

```bash
curl -X POST "http://localhost:8000/api/v1/violations/scan"
```

Expected response:
```json
{
  "status": "success",
  "message": "Scan completed successfully",
  "rules_scanned": 4,
  "records_scanned": 20,
  "violations_detected": 5
}
```

### 8. List Violations

```bash
curl "http://localhost:8000/api/v1/violations"
```

With filters:
```bash
# Filter by severity
curl "http://localhost:8000/api/v1/violations?severity=high"

# Filter by status
curl "http://localhost:8000/api/v1/violations?status=pending_review"

# Limit results
curl "http://localhost:8000/api/v1/violations?limit=10"
```

### 9. Get Violation Details

```bash
curl "http://localhost:8000/api/v1/violations/{violation_id}"
```

Expected response:
```json
{
  "id": "...",
  "rule_id": "...",
  "record_identifier": "...",
  "table_name": "company_records",
  "detected_at": "2026-02-21T10:30:00",
  "status": "pending_review",
  "severity": "high",
  "justification": "This transaction violates the high-value transaction monitoring rule. The transaction amount of $45,000 exceeds the $10,000 threshold requiring additional review and documentation.",
  "record_snapshot": {
    "transaction_id": "TXN000005",
    "amount": 45000,
    "transaction_type": "TRANSFER",
    ...
  },
  "remediation_steps": [
    {
      "step": "Verify the source of funds for this transaction",
      "priority": "high"
    },
    {
      "step": "Obtain additional documentation from the customer",
      "priority": "high"
    }
  ]
}
```

### 10. Get Violation Statistics

```bash
curl "http://localhost:8000/api/v1/violations/stats/summary"
```

Expected response:
```json
{
  "total_violations": 5,
  "by_severity": {
    "critical": 1,
    "high": 3,
    "medium": 1,
    "low": 0
  },
  "by_status": {
    "pending_review": 5,
    "confirmed": 0,
    "dismissed": 0,
    "resolved": 0
  }
}
```

### 11. Dashboard Metrics

```bash
curl "http://localhost:8000/api/v1/dashboard/metrics"
```

Expected response:
```json
{
  "total_violations": 5,
  "active_violations": 5,
  "total_rules": 4,
  "total_records": 20,
  "compliance_score": 75,
  "violations_by_severity": {
    "critical": 1,
    "high": 3,
    "medium": 1,
    "low": 0
  }
}
```

### 12. Risk Score

```bash
curl "http://localhost:8000/api/v1/dashboard/risk-score"
```

Expected response:
```json
{
  "score": 75,
  "total_violations": 5,
  "severity_breakdown": {
    "critical": 1,
    "high": 3,
    "medium": 1,
    "low": 0
  },
  "status": "at_risk"
}
```

### 13. Trends

```bash
curl "http://localhost:8000/api/v1/dashboard/trends"
```

## Using Postman

Import this collection to test all endpoints:

1. Create a new collection in Postman
2. Add environment variable: `base_url = http://localhost:8000`
3. Add environment variable: `policy_id` (after upload)
4. Add environment variable: `violation_id` (after scan)

### Collection Structure

```
PolicySentinel API
├── Health Check (GET {{base_url}}/health)
├── Policies
│   ├── Upload Policy (POST {{base_url}}/api/v1/policies/upload)
│   ├── List Policies (GET {{base_url}}/api/v1/policies)
│   ├── Get Policy (GET {{base_url}}/api/v1/policies/{{policy_id}})
│   ├── Extract Rules (POST {{base_url}}/api/v1/policies/{{policy_id}}/extract-rules)
│   └── Get Rules (GET {{base_url}}/api/v1/policies/{{policy_id}}/rules)
├── Violations
│   ├── Scan (POST {{base_url}}/api/v1/violations/scan)
│   ├── List Violations (GET {{base_url}}/api/v1/violations)
│   ├── Get Violation (GET {{base_url}}/api/v1/violations/{{violation_id}})
│   └── Statistics (GET {{base_url}}/api/v1/violations/stats/summary)
└── Dashboard
    ├── Metrics (GET {{base_url}}/api/v1/dashboard/metrics)
    ├── Risk Score (GET {{base_url}}/api/v1/dashboard/risk-score)
    └── Trends (GET {{base_url}}/api/v1/dashboard/trends)
```

## Testing Tips

1. **Always check health first** - Ensure all services are running
2. **Upload policy before extracting rules** - Rules need a policy document
3. **Extract rules before scanning** - Scanning needs active rules
4. **Use the sample data** - Run `python scripts/setup_demo.py` to load test data
5. **Check logs** - The application logs all operations for debugging

## Common Issues

### Issue: "OpenAI API key not configured"
**Solution**: Add your OpenAI API key to `.env`:
```
OPENAI_API_KEY=sk-your-key-here
```

### Issue: "No records to scan"
**Solution**: Load sample data:
```bash
python scripts/setup_demo.py
```

### Issue: "Database connection failed"
**Solution**: Ensure PostgreSQL, MongoDB, and Redis are running:
```bash
# Check PostgreSQL
psql -U postgres -c "SELECT 1"

# Check MongoDB
mongosh --eval "db.runCommand({ ping: 1 })"

# Check Redis
redis-cli ping
```

### Issue: "No active rules to scan"
**Solution**: Upload a policy and extract rules first:
```bash
# 1. Create sample policy
python scripts/create_sample_policy.py

# 2. Upload it
curl -X POST "http://localhost:8000/api/v1/policies/upload" \
  -F "file=@sample_aml_policy.pdf"

# 3. Extract rules (save policy_id from step 2)
curl -X POST "http://localhost:8000/api/v1/policies/{policy_id}/extract-rules"
```

## Demo Script

For a complete demo, run these commands in order:

```bash
# 1. Setup
python scripts/setup_demo.py
python scripts/create_sample_policy.py

# 2. Start server (in another terminal)
python src/main.py

# 3. Test flow
curl http://localhost:8000/health

# Upload policy
curl -X POST "http://localhost:8000/api/v1/policies/upload" \
  -F "file=@sample_aml_policy.pdf" | jq

# Extract rules (replace {policy_id})
curl -X POST "http://localhost:8000/api/v1/policies/{policy_id}/extract-rules" | jq

# Scan for violations
curl -X POST "http://localhost:8000/api/v1/violations/scan" | jq

# View results
curl "http://localhost:8000/api/v1/dashboard/metrics" | jq
curl "http://localhost:8000/api/v1/violations" | jq
```

## Next Steps

- Build the Next.js frontend
- Add Celery background workers
- Implement real-time monitoring
- Add more sophisticated rule types
- Integrate with real AML datasets

---

**Happy Testing! 🚀**
