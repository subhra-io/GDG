# PolicySentinel - AI-Powered Compliance Monitoring Platform

PolicySentinel is an autonomous compliance agent that transforms unstructured PDF policies into executable rule graphs and continuously enforces them across enterprise databases using AI.

## 🚀 Features

- **AI-Powered Rule Extraction**: Automatically extract compliance rules from PDF policy documents using GPT-4
- **Intelligent Violation Detection**: Scan database records against extracted rules to identify violations
- **Explainable AI**: Generate human-readable justifications and remediation steps for each violation
- **Real-time Dashboard**: Monitor compliance scores, violations, and trends
- **Multi-Database Support**: Works with PostgreSQL, MongoDB, and more
- **RESTful API**: Complete API for integration with existing systems

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL 14+
- MongoDB 6+
- Redis 7+
- OpenAI API Key (for AI features)

## 🛠️ Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd policysentinel
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your configuration:
- Database credentials
- OpenAI API key (required for AI features)
- Other settings as needed

### 5. Setup Databases

Make sure PostgreSQL, MongoDB, and Redis are running:

```bash
# PostgreSQL
createdb policysentinel

# MongoDB - should be running on default port 27017

# Redis - should be running on default port 6379
```

### 6. Initialize Demo Environment

```bash
python scripts/setup_demo.py
```

This will:
- Create database tables
- Load 20 sample financial transaction records
- Prepare the system for testing

## 🎯 Quick Start

### 1. Start the Server

```bash
python src/main.py
```

The API will be available at `http://localhost:8000`

API Documentation:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### 2. Create a Sample Policy PDF

```bash
pip install reportlab  # If not already installed
python scripts/create_sample_policy.py
```

This creates `sample_aml_policy.pdf` with 4 testable AML compliance rules.

### 3. Test the Complete Flow

#### Step 1: Upload Policy Document

```bash
curl -X POST "http://localhost:8000/api/v1/policies/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample_aml_policy.pdf"
```

Response:
```json
{
  "policy_id": "uuid-here",
  "filename": "sample_aml_policy.pdf",
  "status": "processed",
  "message": "Policy uploaded and processed successfully"
}
```

#### Step 2: Extract Rules Using AI

```bash
curl -X POST "http://localhost:8000/api/v1/policies/{policy_id}/extract-rules"
```

This uses GPT-4 to extract structured compliance rules from the policy text.

#### Step 3: Scan for Violations

```bash
curl -X POST "http://localhost:8000/api/v1/violations/scan"
```

This scans all company records against the extracted rules and creates violation records.

#### Step 4: View Dashboard Metrics

```bash
curl "http://localhost:8000/api/v1/dashboard/metrics"
```

Response:
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

#### Step 5: View Violation Details

```bash
curl "http://localhost:8000/api/v1/violations"
```

Each violation includes:
- Rule that was violated
- Record that violated it
- AI-generated justification
- Suggested remediation steps

## 📚 API Endpoints

### Policies

- `POST /api/v1/policies/upload` - Upload policy PDF
- `GET /api/v1/policies` - List all policies
- `GET /api/v1/policies/{id}` - Get policy details
- `POST /api/v1/policies/{id}/extract-rules` - Extract rules using AI
- `GET /api/v1/policies/{id}/rules` - Get rules for a policy

### Violations

- `POST /api/v1/violations/scan` - Scan for violations
- `GET /api/v1/violations` - List violations (with filters)
- `GET /api/v1/violations/{id}` - Get violation details
- `GET /api/v1/violations/stats/summary` - Get violation statistics

### Dashboard

- `GET /api/v1/dashboard/metrics` - Get key metrics
- `GET /api/v1/dashboard/risk-score` - Get compliance risk score
- `GET /api/v1/dashboard/trends` - Get violation trends

### Health

- `GET /health` - System health check
- `GET /` - API information

## 🏗️ Project Structure

```
policysentinel/
├── src/
│   ├── config/          # Configuration management
│   ├── core/            # Core infrastructure (database, logging)
│   ├── models/          # SQLAlchemy database models
│   ├── schemas/         # Pydantic API schemas
│   ├── services/        # Business logic services
│   │   ├── pdf_extractor.py      # PDF text extraction
│   │   ├── rule_extractor.py     # AI rule extraction
│   │   └── violation_detector.py # Violation detection
│   ├── routes/          # FastAPI route handlers
│   ├── utils/           # Utility functions
│   └── main.py          # Application entry point
├── scripts/             # Setup and utility scripts
├── tests/               # Test suite
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
└── README.md
```

## 🧪 Testing

Run the test suite:

```bash
pytest tests/ -v
```

Run specific tests:

```bash
pytest tests/test_config.py -v
pytest tests/test_logging.py -v
```

## 🔧 Development

### Adding New Rules

Rules are extracted automatically from policy PDFs using AI. The system supports:

- Numeric comparisons (>, <, =)
- String matching (contains, equals)
- Regex patterns
- Null checks
- Complex AND/OR logic

### Adding New Data Sources

To monitor different types of records:

1. Create a new model in `src/models/`
2. Add validation logic in `src/services/violation_detector.py`
3. Update the scan endpoint to include your data source

### Customizing AI Prompts

Edit the prompts in `src/services/rule_extractor.py`:
- `_build_extraction_prompt()` - Rule extraction
- `generate_justification()` - Violation explanations
- `generate_remediation_steps()` - Fix suggestions

## 📊 Sample Data

The demo includes 20 sample financial transactions with varying amounts:
- Normal transactions: $100 - $5,000
- High-value transactions: $10,000 - $50,000
- Very high transactions: $100,000 - $500,000

Some transactions are designed to violate the sample AML policy rules.

## 🚀 Deployment

### Docker (Coming Soon)

```bash
docker-compose up
```

### Manual Deployment

1. Set up production databases
2. Configure environment variables
3. Run database migrations
4. Start the application with a production WSGI server

```bash
gunicorn src.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

## 🤝 Contributing

This is a hackathon project for GDG DevFest 2026.

## 📝 License

Copyright © 2026 PolicySentinel Team

## 🎓 Hackathon Context

Built for **GDG DevFest 2026 - Round 3: Coding Phase**

**Problem Statement**: Data Policy Compliance Agent

**Tech Stack**:
- Backend: FastAPI, SQLAlchemy, PostgreSQL
- AI: OpenAI GPT-4, LangChain
- Infrastructure: Redis, MongoDB, Celery
- Frontend: Next.js (separate repository)

## 📞 Support

For questions or issues, please contact the development team.

---

**Made with ❤️ for GDG DevFest 2026**
