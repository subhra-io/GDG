# Logging and Monitoring Guide

## Backend Logs

### Console Logs (Default)

By default, logs are output to **stdout** (console) with colored formatting.

**To view logs while running**:
```bash
# Start backend and see logs in real-time
uvicorn src.main:app --reload

# You'll see logs like:
# 2024-02-19T17:30:45 [info] Starting PolicySentinel API
# 2024-02-19T17:30:46 [info] Database connected
```

### Redirect Logs to File

**Option 1: Redirect stdout**
```bash
# Save all logs to file
uvicorn src.main:app --reload > logs/app.log 2>&1

# View logs in real-time
tail -f logs/app.log
```

**Option 2: Use tee to see logs AND save them**
```bash
# See logs in console AND save to file
uvicorn src.main:app --reload 2>&1 | tee logs/app.log
```

### Log Levels

Configure in `.env`:
```bash
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT=console  # console or json
```

**Change log level**:
```bash
# More verbose (for debugging)
LOG_LEVEL=DEBUG uvicorn src.main:app --reload

# Less verbose (for production)
LOG_LEVEL=WARNING uvicorn src.main:app --reload
```

### Log Locations

```
Current Setup:
├── Console (stdout) - Default, real-time logs
├── logs/app.log - If you redirect output
└── Docker logs - If running in container
```

### View Specific Logs

**Filter by level**:
```bash
# Show only errors
uvicorn src.main:app --reload 2>&1 | grep ERROR

# Show only warnings and errors
uvicorn src.main:app --reload 2>&1 | grep -E "WARNING|ERROR"
```

**Filter by component**:
```bash
# Show only rule extraction logs
uvicorn src.main:app --reload 2>&1 | grep rule_extractor

# Show only database logs
uvicorn src.main:app --reload 2>&1 | grep database
```

### Structured Logging

The system uses **structlog** for structured logging. Each log entry includes:
- Timestamp (ISO format)
- Log level (DEBUG, INFO, WARNING, ERROR)
- Logger name (module name)
- App name (policysentinel)
- Message and context

**Example log entry**:
```
2024-02-19T17:30:45 [info] rule_extractor: Extracting rules using OpenAI
  policy_id=abc123
  app=policysentinel
```

## Database Logs

### PostgreSQL Logs

**View PostgreSQL logs**:
```bash
# If using Docker
docker logs postgres-container

# If using local PostgreSQL
tail -f /usr/local/var/log/postgresql@14.log  # macOS
tail -f /var/log/postgresql/postgresql-14-main.log  # Linux
```

**Enable query logging** (for debugging):
```sql
-- Connect to PostgreSQL
psql -U postgres -d policysentinel

-- Enable query logging
ALTER SYSTEM SET log_statement = 'all';
SELECT pg_reload_conf();

-- View slow queries
ALTER SYSTEM SET log_min_duration_statement = 1000;  -- Log queries > 1 second
```

**Check database connections**:
```sql
-- See active connections
SELECT * FROM pg_stat_activity WHERE datname = 'policysentinel';

-- See database size
SELECT pg_size_pretty(pg_database_size('policysentinel'));
```

### MongoDB Logs

**View MongoDB logs**:
```bash
# If using Docker
docker logs mongodb-container

# If using local MongoDB
tail -f /usr/local/var/log/mongodb/mongo.log  # macOS
tail -f /var/log/mongodb/mongod.log  # Linux
```

**Check MongoDB status**:
```bash
# Connect to MongoDB
mongosh

# Check database stats
use policysentinel
db.stats()

# View collections
show collections

# Count documents
db.audit_logs.countDocuments()
```

### Redis Logs

**View Redis logs**:
```bash
# If using Docker
docker logs redis-container

# If using local Redis
tail -f /usr/local/var/log/redis.log  # macOS
tail -f /var/log/redis/redis-server.log  # Linux
```

**Check Redis status**:
```bash
# Connect to Redis
redis-cli

# Check info
INFO

# Monitor commands in real-time
MONITOR
```

## Docker Logs

If running with Docker Compose:

```bash
# View all container logs
docker-compose logs

# Follow logs in real-time
docker-compose logs -f

# View specific service logs
docker-compose logs backend
docker-compose logs postgres
docker-compose logs mongodb
docker-compose logs redis

# View last 100 lines
docker-compose logs --tail=100

# View logs with timestamps
docker-compose logs -t
```

## Application Monitoring

### Health Check Endpoint

```bash
# Check if backend is running
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-02-19T17:30:45",
  "version": "1.0.0"
}
```

### Database Connection Check

```bash
# Check database connectivity
curl http://localhost:8000/api/v1/health/database

# Expected response:
{
  "postgres": "connected",
  "mongodb": "connected",
  "redis": "connected"
}
```

### Metrics Endpoint

```bash
# Get application metrics
curl http://localhost:8000/api/v1/dashboard/metrics

# Returns:
{
  "total_policies": 3,
  "total_rules": 10,
  "total_violations": 13,
  "compliance_score": 85.5
}
```

## Log Analysis

### Common Log Patterns

**Successful operations**:
```
[info] Policy uploaded successfully policy_id=abc123
[info] Rules extracted successfully rules_count=4
[info] Violations detected violations_count=13
```

**Errors to watch for**:
```
[error] OpenAI API key not configured
[error] Database connection failed
[error] Failed to extract rules error=...
[error] Failed to parse OpenAI response
```

**Performance indicators**:
```
[info] Rule extraction completed duration=3.2s
[info] Violation scan completed records_scanned=1000 duration=1.5s
```

### Debugging Tips

**Enable debug logging**:
```bash
# Set in .env
LOG_LEVEL=DEBUG

# Or run with debug
LOG_LEVEL=DEBUG uvicorn src.main:app --reload
```

**Debug specific issues**:

1. **OpenAI API issues**:
```bash
# Check logs for OpenAI errors
uvicorn src.main:app --reload 2>&1 | grep -i openai
```

2. **Database issues**:
```bash
# Check database connection logs
uvicorn src.main:app --reload 2>&1 | grep -i database
```

3. **Rule extraction issues**:
```bash
# Check rule extraction logs
uvicorn src.main:app --reload 2>&1 | grep rule_extractor
```

## Production Logging Setup

For production, use JSON logging:

```bash
# In .env
LOG_LEVEL=INFO
LOG_FORMAT=json
```

**Benefits**:
- Machine-readable logs
- Easy to parse and analyze
- Works with log aggregation tools (ELK, Splunk, etc.)

**Example JSON log**:
```json
{
  "event": "Rules extracted successfully",
  "level": "info",
  "logger": "rule_extractor",
  "timestamp": "2024-02-19T17:30:45.123456",
  "app": "policysentinel",
  "policy_id": "abc123",
  "rules_count": 4
}
```

## Log Rotation

**Setup log rotation** (for production):

```bash
# Create logrotate config
sudo nano /etc/logrotate.d/policysentinel

# Add:
/path/to/logs/app.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 0644 user group
}
```

## Troubleshooting

### No logs appearing

**Check**:
1. Log level is not too high (use INFO or DEBUG)
2. Output is not redirected elsewhere
3. Application is actually running

```bash
# Verify process is running
ps aux | grep uvicorn

# Check if port is listening
lsof -i :8000
```

### Too many logs

**Reduce verbosity**:
```bash
# Set higher log level
LOG_LEVEL=WARNING uvicorn src.main:app --reload

# Filter out third-party logs
# Already configured in logging.py:
# - uvicorn: WARNING
# - sqlalchemy: WARNING
# - pymongo: WARNING
```

### Logs not structured

**Check format**:
```bash
# Ensure using console format for development
LOG_FORMAT=console

# Use JSON for production
LOG_FORMAT=json
```

## Quick Reference

```bash
# View backend logs
uvicorn src.main:app --reload

# Save logs to file
uvicorn src.main:app --reload 2>&1 | tee logs/app.log

# View PostgreSQL logs
docker logs postgres-container

# View MongoDB logs
docker logs mongodb-container

# View all Docker logs
docker-compose logs -f

# Check health
curl http://localhost:8000/health

# Debug mode
LOG_LEVEL=DEBUG uvicorn src.main:app --reload

# Filter errors only
uvicorn src.main:app --reload 2>&1 | grep ERROR
```

## Summary

**Default Setup**:
- ✅ Logs to console (stdout)
- ✅ Structured logging with structlog
- ✅ Color-coded by level
- ✅ Includes context (policy_id, etc.)

**To Save Logs**:
```bash
uvicorn src.main:app --reload 2>&1 | tee logs/app.log
```

**To Debug**:
```bash
LOG_LEVEL=DEBUG uvicorn src.main:app --reload
```

**To Monitor Databases**:
```bash
docker-compose logs -f postgres
docker-compose logs -f mongodb
```
