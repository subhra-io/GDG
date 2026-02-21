# 🤖 PolicySentinel - AI Prompts Summary

## Overview

Your system uses **4 main prompts** for different AI tasks. All prompts are production-ready with validation and quality checks.

---

## 1️⃣ Rule Extraction Prompt

**File**: `src/prompts/rule_extraction.py`

**Purpose**: Convert policy PDF text into structured, actionable compliance rules

**System Prompt**:
```
You are an expert compliance analyst specializing in extracting 
actionable rules from policy documents.

Focus on:
- Quantitative thresholds (amounts, counts, percentages)
- Time-based constraints (within X hours/days)
- Pattern requirements (frequency, sequences)
- Required field validations
- Conditional logic (if-then rules)
```

**Input**: Policy document text (from PDF)

**Output**: JSON with structured rules
```json
{
  "rules": [
    {
      "rule_id": "R001",
      "description": "Transactions exceeding $10,000 must be flagged",
      "category": "transaction_limit",
      "condition": {
        "field": "amount",
        "operator": "greater_than",
        "value": 10000
      },
      "severity": "high",
      "confidence_score": 0.98
    }
  ]
}
```

**Key Features**:
- Extracts quantitative thresholds
- Identifies operators (greater_than, less_than, equals, etc.)
- Assigns severity based on language (must = high, should = medium)
- Provides confidence scores
- Includes validation query suggestions

---

## 2️⃣ Justification Prompt

**File**: `src/prompts/justification.py`

**Purpose**: Explain WHY a violation occurred in business-friendly language

**System Prompt**:
```
You are a compliance officer explaining violations to business 
stakeholders.

Your explanations should be:
- Clear and concise (2-3 sentences maximum)
- Non-technical and business-friendly
- Specific about what was violated and why
- Factual without speculation
```

**Input**: 
- Rule description
- Rule condition
- Record data
- Violation details

**Output**: Business-friendly explanation (2-3 sentences)

**Example Output**:
```
"This transaction violates the high-value transaction policy, 
which requires flagging any single transaction exceeding $10,000. 
The transaction amount of $15,750 exceeds this threshold by $5,750, 
triggering a mandatory review requirement."
```

**Key Features**:
- Non-technical language
- Specific values mentioned
- Clear gap identification
- Concise (under 150 words)
- Quality validation checks

---

## 3️⃣ Remediation Prompt

**File**: `src/prompts/remediation.py`

**Purpose**: Generate actionable steps to fix violations and prevent recurrence

**System Prompt**:
```
You are a compliance consultant providing actionable remediation 
guidance.

Your recommendations should be:
- Specific and actionable (not vague advice)
- Prioritized by urgency and impact
- Practical and implementable
- Focused on preventing recurrence
```

**Input**:
- Rule description
- Violation justification
- Record data
- Severity level

**Output**: JSON with 2-4 actionable steps
```json
{
  "steps": [
    {
      "step_number": 1,
      "action": "Immediately flag transaction for review",
      "responsible_party": "Compliance Team",
      "priority": "immediate",
      "estimated_time": "1 hour",
      "prevents_recurrence": false
    },
    {
      "step_number": 2,
      "action": "Update automated flagging system",
      "responsible_party": "System Admin",
      "priority": "high",
      "estimated_time": "1 week",
      "prevents_recurrence": true
    }
  ],
  "additional_notes": "Priority on fixing root cause"
}
```

**Key Features**:
- Specific, actionable steps
- Assigns responsibility
- Prioritizes by urgency
- Estimates time required
- Identifies prevention steps
- Severity-aware recommendations

---

## 4️⃣ Reasoning Trace Prompt

**File**: `src/prompts/reasoning_trace.py`

**Purpose**: Generate transparent, step-by-step AI reasoning for audit compliance

**System Prompt**:
```
You are an AI compliance auditor explaining your decision-making 
process.

Generate a step-by-step reasoning trace that shows how you reached 
the conclusion that this is a violation.
```

**Input**:
- Rule description
- Severity
- Record data
- Violation details

**Output**: JSON array of reasoning steps (3-5 steps)
```json
[
  {
    "step_number": 1,
    "description": "Evaluated transaction amount against threshold",
    "rules_evaluated": ["Transaction Limit Rule R001"],
    "policy_references": [
      {
        "clause": "Section 2.1: High-value transactions",
        "page": 3,
        "document_name": "AML Policy"
      }
    ],
    "confidence_score": 95,
    "outcome": "fail"
  },
  {
    "step_number": 2,
    "description": "Checked for approval documentation",
    "rules_evaluated": ["Approval Requirement R002"],
    "confidence_score": 90,
    "outcome": "fail"
  }
]
```

**Key Features**:
- Multi-step reasoning chain
- Confidence scores per step
- Policy clause references
- Clear outcomes (pass/fail/inconclusive)
- Audit-ready transparency

---

## 🎯 Prompt Design Principles

All prompts follow these principles:

### 1. Clear Role Definition
Each prompt starts with a clear role:
- "You are an expert compliance analyst..."
- "You are a compliance officer..."
- "You are a compliance consultant..."

### 2. Structured Output
All prompts request JSON output with specific schemas for:
- Consistency
- Easy parsing
- Validation
- Database storage

### 3. Examples Included
Each prompt includes 2-3 concrete examples showing:
- Input format
- Expected output
- Quality standards

### 4. Quality Validation
Each prompt has validation functions:
- `validate_extracted_rules()` - Checks rule structure
- `validate_justification()` - Checks explanation quality
- `validate_remediation_steps()` - Checks actionability
- Reasoning traces have built-in confidence scores

### 5. Business-Friendly Language
Prompts emphasize:
- Non-technical explanations
- Specific, actionable guidance
- Clear, concise communication
- Stakeholder-appropriate tone

---

## 📊 Prompt Usage Flow

```
1. POLICY UPLOAD
   ↓
   Rule Extraction Prompt
   ↓
   Structured Rules → Database

2. VIOLATION DETECTION
   ↓
   Justification Prompt
   ↓
   Business-friendly explanation
   ↓
   Remediation Prompt
   ↓
   Actionable steps
   ↓
   Reasoning Trace Prompt (optional)
   ↓
   Transparent AI reasoning

3. DASHBOARD DISPLAY
   ↓
   Show all generated content
```

---

## 🔧 How to Customize Prompts

### Modify System Prompts
Edit the `SYSTEM_PROMPT` in each file:
```python
SYSTEM_PROMPT = """Your custom instructions here..."""
```

### Adjust Output Format
Modify the JSON schema in the prompt:
```python
RETURN FORMAT (JSON):
{
  "your_custom_field": "value"
}
```

### Add Examples
Add more examples to guide the LLM:
```python
Example 4 - Your Custom Case:
{
  "field": "value"
}
```

### Change Validation Rules
Update validation functions:
```python
def validate_extracted_rules(rules):
    # Your custom validation logic
    pass
```

---

## 💡 Prompt Engineering Tips

### 1. Be Specific
❌ "Extract rules from this document"
✅ "Extract actionable compliance rules with quantitative thresholds"

### 2. Provide Structure
❌ "Return the rules"
✅ "Return JSON with rule_id, description, condition, severity"

### 3. Include Examples
❌ Just instructions
✅ Instructions + 2-3 concrete examples

### 4. Set Constraints
❌ "Explain the violation"
✅ "Explain in 2-3 sentences using business-friendly language"

### 5. Request Confidence
❌ Just the answer
✅ Answer + confidence score (0-100)

---

## 🎯 For Your Demo

**Talking Points**:

1. **"Production-ready prompts"**
   - Not just basic prompts
   - Structured output with validation
   - Quality checks built-in

2. **"Business-friendly AI"**
   - Justifications in plain language
   - Actionable remediation steps
   - No technical jargon

3. **"Transparent reasoning"**
   - Step-by-step AI decision-making
   - Confidence scores
   - Policy references
   - Audit-ready

4. **"Validated output"**
   - Every prompt has validation
   - Ensures quality and consistency
   - Catches errors early

---

## 📚 Files to Show in Demo

1. **Rule Extraction**: `src/prompts/rule_extraction.py`
   - Show the structured JSON output
   - Highlight validation logic

2. **Justification**: `src/prompts/justification.py`
   - Show business-friendly examples
   - Emphasize clarity

3. **Reasoning Trace**: `src/prompts/reasoning_trace.py`
   - Show multi-step reasoning
   - Highlight transparency

---

**These prompts are the secret sauce that makes your AI compliance engine work!** 🚀
