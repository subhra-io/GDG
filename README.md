# PolicySentinel

AI-powered compliance monitoring platform for automated policy interpretation, violation detection, and risk management.

## Features

- **Automated Rule Extraction**: Extract compliance rules from policy documents using LLM
- **Interactive Rule Graphs**: Visualize rule relationships with conflict and cycle detection
- **Violation Detection**: Automated monitoring and detection with AI-powered reasoning
- **Predictive Analytics**: ML-based risk predictions with what-if scenario testing
- **Human Review Workflow**: Complete governance layer with review queue and assignments
- **Multi-Channel Alerts**: Email, Slack, and in-app notifications
- **Audit Trail**: Automatic logging of all system activities
- **Feedback Loop**: Continuous learning from human corrections

## Tech Stack

### Backend
- Python 3.11+
- FastAPI
- PostgreSQL
- MongoDB
- Redis
- Celery
- SQLAlchemy
- OpenAI / Google Gemini

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- D3.js

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- MongoDB 6+
- Redis 7+

## Installation

### Backend Setup

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your database credentials and API keys

# Run database migrations
python scripts/migrate_rule_graph.py
python scripts/migrate_overnight_features.py
python scripts/migrate_reviews.py
python scripts/migrate_alerts.py
python scripts/migrate_audit.py
python scripts/migrate_feedback_loop.py

# Start backend server
uvicorn src.main:app --reload --port 8000
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Load Sample Data

```bash
# Load IBM AML dataset
python scripts/load_ibm_dataset.py

# Create sample policy
python scripts/create_sample_policy.py
```

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=policysentinel
POSTGRES_USER=your_user
POSTGRES_PASSWORD=your_password

MONGODB_HOST=localhost
MONGODB_PORT=27017
MONGODB_DB=policysentinel_audit

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# LLM API Keys
OPENAI_API_KEY=your_openai_key
GOOGLE_API_KEY=your_google_key
LLM_PROVIDER=openai  # or gemini

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your_email
SMTP_PASSWORD=your_password
EMAIL_ENABLED=false

# Slack (optional)
SLACK_WEBHOOK_URL=your_webhook_url
SLACK_ENABLED=false
```

## Usage

### Starting the Application

```bash
# Terminal 1: Backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Terminal 3: Celery Worker (optional)
celery -A src.workers.tasks worker --loglevel=info
```

### Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## API Endpoints

### Policy Management
- `POST /api/v1/policy/upload` - Upload policy document
- `GET /api/v1/policy/documents` - List all policies
- `POST /api/v1/policy/extract-rules` - Extract rules from policy

### Violations
- `GET /api/v1/violations` - List violations
- `GET /api/v1/violations/{id}` - Get violation details
- `GET /api/v1/violations/{id}/reasoning` - Get AI reasoning

### Predictions
- `POST /api/v1/predictions/predict` - Predict violation risk
- `POST /api/v1/predictions/what-if` - Run what-if scenario
- `GET /api/v1/predictions/high-risk` - Get high-risk records

### Reviews
- `GET /api/v1/reviews/queue` - Get review queue
- `POST /api/v1/reviews/{violation_id}` - Submit review
- `PUT /api/v1/reviews/{violation_id}/assign` - Assign reviewer

### Alerts & Notifications
- `GET /api/v1/notifications/{user_id}` - Get user notifications
- `POST /api/v1/alerts/rules` - Create alert rule
- `GET /api/v1/alerts/history` - Get alert history

### Audit & Feedback
- `GET /api/v1/audit/logs` - Get audit logs
- `GET /api/v1/feedback/metrics` - Get AI accuracy metrics
- `GET /api/v1/feedback/suggestions` - Get improvement suggestions

## Architecture

```
┌─────────────────────────────────────────┐
│           PolicySentinel                │
├─────────────────────────────────────────┤
│                                         │
│  INPUT LAYER                            │
│  ├── Policy PDFs                        │
│  └── Database Records                   │
│                                         │
│  AI COMPLIANCE ENGINE                   │
│  ├── Rule Extraction (LLM)             │
│  ├── Rule Graph Engine                  │
│  ├── Violation Detection                │
│  ├── Risk Prediction (ML)               │
│  └── Monitoring Agent                   │
│                                         │
│  GOVERNANCE LAYER                       │
│  ├── Explainability Engine              │
│  ├── Human Review Interface             │
│  └── Feedback Loop                      │
│                                         │
│  OUTPUT LAYER                           │
│  ├── Dashboard                          │
│  ├── Alerts & Notifications             │
│  ├── Audit Trail                        │
│  └── Reports                            │
│                                         │
└─────────────────────────────────────────┘
```

## Development

### Running Tests

```bash
# Backend tests
pytest

# Frontend tests
cd frontend
npm test
```

### Code Style

```bash
# Python
black src/
flake8 src/

# TypeScript
cd frontend
npm run lint
```

## Deployment

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Production Considerations

- Use environment-specific configuration
- Enable SSL/TLS for API endpoints
- Configure proper database backups
- Set up monitoring and logging
- Use production-grade WSGI server (Gunicorn)
- Enable rate limiting
- Configure CORS properly

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Support

For issues and questions, please open an issue on GitHub.
