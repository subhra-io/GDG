# Production Features: Prompts & Dataset Integration

This document describes the production-ready OpenAI prompt templates and sample dataset integration features added to PolicySentinel.

## Option B: Production OpenAI Prompt Templates

### Overview

We've implemented production-quality prompt templates with examples, validation, and best practices for three key AI operations:

1. **Rule Extraction** - Extract compliance rules from PDF policy documents
2. **Violation Justification** - Generate clear explanations for detected violations
3. **Remediation Suggestions** - Provide actionable steps to resolve violations

### Implementation

#### 1. Rule Extraction Prompt (`src/prompts/rule_extraction.py`)

**Features:**
- Structured JSON output with comprehensive rule metadata
- Support for multiple rule categories (transaction_limit, pattern_detection, required_field, time_constraint)
- Confidence scoring for extracted rules
- Validation query generation for each rule
- Built-in validation to ensure extracted rules meet quality standards

**Example Output:**
```json
{
  "rule_id": "R001",
  "description": "Single transactions exceeding $10,000 must be flagged for review",
  "category": "transaction_limit",
  "condition": {
    "field": "amount",
    "operator": "greater_than",
    "value": 10000
  },
  "severity": "high",
  "confidence_score": 0.98,
  "validation_query": "SELECT * FROM transactions WHERE amount > 10000"
}
```

**Validation:**
- Checks for required fields (rule_id, description, category, condition, severity)
- Validates severity levels (critical, high, medium, low)
- Validates operators (greater_than, less_than, equals, contains, regex_match, etc.)
- Ensures confidence scores are between 0 and 1
- Validates condition structure

#### 2. Justification Prompt (`src/prompts/justification.py`)

**Features:**
- Business-friendly language (non-technical)
- Concise explanations (2-3 sentences)
- Clear identification of rule requirement vs actual record data
- Quality validation to ensure explanations meet standards

**Example Output:**
```
This transaction violates the high-value transaction policy, which requires flagging 
any single transaction exceeding $10,000. The transaction amount of $15,750 exceeds 
this threshold by $5,750, triggering a mandatory review requirement.
```

**Validation:**
- Checks length (10-150 words)
- Flags technical jargon (SQL, database, API, JSON)
- Ensures explicit mention of "violate" or "violation"
- Verifies inclusion of specific numeric values

#### 3. Remediation Prompt (`src/prompts/remediation.py`)

**Features:**
- Specific, actionable steps (not vague advice)
- Priority levels (immediate, high, medium, low)
- Responsible party identification
- Time estimates for each step
- Prevention focus (at least one step should prevent recurrence)

**Example Output:**
```json
{
  "steps": [
    {
      "step_number": 1,
      "action": "Immediately flag transaction TXN123456 for compliance review",
      "responsible_party": "Compliance Team",
      "priority": "immediate",
      "estimated_time": "1 hour",
      "prevents_recurrence": false
    },
    {
      "step_number": 2,
      "action": "Review and update the automated flagging system to ensure all transactions above $10,000 are automatically flagged",
      "responsible_party": "System Admin",
      "priority": "high",
      "estimated_time": "1 week",
      "prevents_recurrence": true
    }
  ]
}
```

**Validation:**
- Ensures 2-6 steps provided
- Checks for required fields (action, responsible_party, priority, estimated_time)
- Validates priority levels
- Ensures actions are specific (minimum 5 words)
- Flags vague language (review, consider, maybe, possibly)
- Requires at least one prevention-focused step

### Usage

The prompts are automatically used by the `RuleExtractor` service:

```python
from src.services.rule_extractor import RuleExtractor

extractor = RuleExtractor()

# Extract rules from policy text
rules = extractor.extract_rules(policy_text, policy_id)

# Generate justification for violation
justification = extractor.generate_justification(
    rule_description="Transactions over $10,000 must be flagged",
    record_data={"amount": 15750, "transaction_id": "TXN123"},
    violation_details={"condition": {"field": "amount", "operator": "greater_than", "value": 10000}}
)

# Generate remediation steps
steps = extractor.generate_remediation_steps(
    rule_description="Transactions over $10,000 must be flagged",
    violation_justification=justification,
    record_data={"amount": 15750, "transaction_id": "TXN123"},
    severity="high"
)
```

## Option C: Sample Dataset Integration

### Overview

We've integrated support for the IBM AML dataset and created comprehensive test scenario generators for realistic compliance testing.

### 1. IBM AML Dataset Loader (`src/datasets/ibm_aml_loader.py`)

**Dataset Information:**
- **Name:** IBM Transactions for Anti-Money Laundering (AML)
- **Source:** https://www.kaggle.com/datasets/ealtman2019/ibm-transactions-for-anti-money-laundering-aml
- **License:** CDLA-Sharing-1.0 (permissive, allows sharing and use)
- **Type:** Synthetic financial transaction data with explicit laundering tags

**Features:**
- Automatic dataset discovery in common locations
- Field mapping from IBM schema to PolicySentinel schema
- Batch loading with progress tracking
- Filtering by laundering status (normal vs laundering transactions)
- Statistics generation (counts, amounts, transaction types)
- Transaction type mapping (Cheque→PAYMENT, ACH→TRANSFER, Cash→CASH_OUT, etc.)

**Usage:**

```bash
# Download dataset from Kaggle first, then:

# Load all records
python scripts/load_ibm_dataset.py --path data/HI-Small_Trans.csv

# Load first 1000 records
python scripts/load_ibm_dataset.py --max-records 1000

# Load only laundering transactions
python scripts/load_ibm_dataset.py --laundering-only

# Show statistics
python scripts/load_ibm_dataset.py --stats
```

**Example Statistics Output:**
```
=== IBM AML Dataset Statistics ===
Total Records: 5000
Laundering Transactions: 250 (5.0%)
Normal Transactions: 4750

Amount Statistics:
  Min: $100.00
  Max: $500,000.00
  Avg: $12,450.50

Transaction Types:
  TRANSFER: 2500
  PAYMENT: 1500
  CASH_OUT: 800
  DEBIT: 200
```

### 2. Enhanced Sample Policy Generator (`scripts/create_sample_policy.py`)

**Features:**
- Multiple policy types: AML, GDPR, SOX
- Realistic compliance rules with specific thresholds
- Professional PDF formatting
- Clear severity levels and page references

**Usage:**

```bash
# Generate AML policy (default)
python scripts/create_sample_policy.py

# Generate GDPR policy
python scripts/create_sample_policy.py --type gdpr

# Generate SOX policy
python scripts/create_sample_policy.py --type sox

# Generate all policies
python scripts/create_sample_policy.py --type all
```

**Generated Policies:**

1. **AML Policy** (`sample_aml_policy.pdf`)
   - Rule 1: Transactions > $10,000 (High severity)
   - Rule 2: Multiple transactions > $50,000 in 24h (Critical severity)
   - Rule 3: Cash withdrawals > $5,000 (Medium severity)
   - Rule 4: Rapid fund movement > $20,000 (High severity)

2. **GDPR Policy** (`sample_gdpr_policy.pdf`)
   - Rule 1: Data retention > 90 days (High severity)
   - Rule 2: Missing or withdrawn consent (Critical severity)
   - Rule 3: Excessive data collection > 10 fields (Medium severity)

3. **SOX Policy** (`sample_sox_policy.pdf`)
   - Rule 1: Dual authorization for transactions > $25,000 (Critical severity)
   - Rule 2: Segregation of duties violation (High severity)
   - Rule 3: Incomplete audit trail (High severity)

### 3. Test Scenario Generator (`scripts/create_test_scenarios.py`)

**Features:**
- Pre-configured test data designed to trigger specific violations
- Scenarios for AML, GDPR, and SOX compliance
- Both violating and compliant examples
- Realistic transaction patterns

**Usage:**

```bash
python scripts/create_test_scenarios.py
```

**Generated Scenarios:**

**AML Scenarios:**
- High-value transaction ($15,750 - violates $10k threshold)
- Pattern violation (4 transactions totaling $67k in 16 hours)
- Large cash withdrawal ($7,200 - violates $5k limit)
- Rapid fund movement ($25k in and out within 30 minutes)
- Compliant transaction ($4,500 - below all thresholds)

**GDPR Scenarios:**
- Data retention violation (120 days old, exceeds 90-day limit)
- Missing consent documentation
- Withdrawn consent (should be deleted)
- Excessive data collection (15 fields, exceeds 10-field limit)

**SOX Scenarios:**
- Missing dual authorization ($35k payment with only one approver)
- Segregation of duties violation (same person created and approved)
- Incomplete audit trail (missing modified_at and modified_by fields)

## Complete Demo Workflow

### Step 1: Set Up Database

```bash
# Start PostgreSQL and MongoDB
docker-compose up -d

# Run database migrations
alembic upgrade head
```

### Step 2: Load Sample Data

```bash
# Option A: Load IBM AML dataset (realistic data)
python scripts/load_ibm_dataset.py --path data/HI-Small_Trans.csv --max-records 1000

# Option B: Load test scenarios (pre-configured violations)
python scripts/create_test_scenarios.py

# Option C: Both
python scripts/load_ibm_dataset.py --max-records 500
python scripts/create_test_scenarios.py
```

### Step 3: Generate Policy Documents

```bash
# Generate all policy types
python scripts/create_sample_policy.py --type all
```

This creates:
- `sample_aml_policy.pdf`
- `sample_gdpr_policy.pdf`
- `sample_sox_policy.pdf`

### Step 4: Start Backend

```bash
uvicorn src.main:app --reload
```

### Step 5: Upload Policies and Run Scans

```bash
# Upload AML policy
curl -X POST "http://localhost:8000/api/v1/policies/upload" \
  -F "file=@sample_aml_policy.pdf"

# The system will automatically:
# 1. Extract text from PDF
# 2. Use production prompts to extract rules
# 3. Validate extracted rules
# 4. Store rules in database

# Run compliance scan
curl -X POST "http://localhost:8000/api/v1/violations/scan"

# The system will:
# 1. Evaluate all records against extracted rules
# 2. Detect violations
# 3. Generate justifications using production prompts
# 4. Generate remediation steps using production prompts
# 5. Store violations with full context

# View violations
curl "http://localhost:8000/api/v1/violations"
```

### Step 6: Review Results

Access the dashboard at `http://localhost:3000` to see:
- Total violations by severity
- Violation trends over time
- Detailed violation information with justifications
- Remediation suggestions for each violation
- Compliance score and metrics

## Benefits

### Production Prompts

1. **Consistency:** Standardized prompts ensure consistent output quality
2. **Validation:** Built-in validation catches issues early
3. **Examples:** Comprehensive examples guide the LLM to better outputs
4. **Maintainability:** Centralized prompts are easy to update and improve
5. **Transparency:** Clear documentation of what we ask the LLM to do

### Dataset Integration

1. **Realistic Testing:** IBM AML dataset provides real-world transaction patterns
2. **Ground Truth:** Pre-labeled laundering transactions enable accuracy validation
3. **Scale:** Thousands of transactions for performance testing
4. **Variety:** Multiple transaction types and patterns
5. **Demo-Ready:** Test scenarios guarantee violations for demonstrations

## Next Steps

1. **Fine-tune Prompts:** Adjust prompts based on actual usage and feedback
2. **Add More Datasets:** Integrate additional compliance datasets (GDPR violations, SOX examples)
3. **Expand Scenarios:** Create more complex multi-rule violation scenarios
4. **Performance Testing:** Use IBM dataset to test system performance at scale
5. **Accuracy Metrics:** Compare detected violations against ground truth labels

## Files Created

### Prompt Templates
- `src/prompts/__init__.py` - Module exports
- `src/prompts/rule_extraction.py` - Rule extraction prompt and validation
- `src/prompts/justification.py` - Justification prompt and validation
- `src/prompts/remediation.py` - Remediation prompt and validation

### Dataset Integration
- `src/datasets/__init__.py` - Module exports
- `src/datasets/ibm_aml_loader.py` - IBM AML dataset loader
- `scripts/load_ibm_dataset.py` - CLI tool for loading IBM dataset

### Sample Data
- `scripts/create_sample_policy.py` - Enhanced with multiple policy types
- `scripts/create_test_scenarios.py` - Pre-configured test scenarios

### Documentation
- `PRODUCTION_FEATURES.md` - This file

## Testing

All prompt templates include validation functions that can be tested:

```python
from src.prompts import RuleExtractionPrompt, JustificationPrompt, RemediationPrompt

# Test rule extraction validation
rules = [{"rule_id": "R001", "description": "Test", ...}]
is_valid, errors = RuleExtractionPrompt.validate_extracted_rules(rules)

# Test justification validation
justification = "This transaction violates..."
is_valid, warnings = JustificationPrompt.validate_justification(justification)

# Test remediation validation
steps = [{"step_number": 1, "action": "Do something", ...}]
is_valid, errors = RemediationPrompt.validate_remediation_steps(steps)
```

## License Notes

- **IBM AML Dataset:** CDLA-Sharing-1.0 (permissive, allows sharing and use)
- **PolicySentinel Code:** Your project license
- **OpenAI API:** Requires valid API key and follows OpenAI's usage policies
