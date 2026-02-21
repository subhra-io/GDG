#!/bin/bash

# PolicySentinel Pre-Demo Check Script
# Run this before your demo to verify everything is working

echo "🔍 PolicySentinel Pre-Demo Check"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check counter
CHECKS_PASSED=0
CHECKS_FAILED=0

# Function to check command
check_command() {
    if command -v $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $1 is installed"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $1 is not installed"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# Function to check service
check_service() {
    if $1 &> /dev/null; then
        echo -e "${GREEN}✓${NC} $2 is running"
        ((CHECKS_PASSED++))
        return 0
    else
        echo -e "${RED}✗${NC} $2 is not running"
        ((CHECKS_FAILED++))
        return 1
    fi
}

# 1. Check Python
echo "1. Checking Python..."
check_command python3

# 2. Check virtual environment
echo ""
echo "2. Checking virtual environment..."
if [ -d "venv" ]; then
    echo -e "${GREEN}✓${NC} Virtual environment exists"
    ((CHECKS_PASSED++))
else
    echo -e "${RED}✗${NC} Virtual environment not found"
    echo -e "${YELLOW}→${NC} Run: python3 -m venv venv"
    ((CHECKS_FAILED++))
fi

# 3. Check databases
echo ""
echo "3. Checking databases..."
check_service "psql -U postgres -c 'SELECT 1' &> /dev/null" "PostgreSQL"
check_service "mongosh --eval 'db.adminCommand({ping:1})' &> /dev/null" "MongoDB"
check_service "redis-cli ping &> /dev/null" "Redis"

# 4. Check .env file
echo ""
echo "4. Checking configuration..."
if [ -f ".env" ]; then
    echo -e "${GREEN}✓${NC} .env file exists"
    ((CHECKS_PASSED++))
    
    # Check for OpenAI key
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        echo -e "${GREEN}✓${NC} OpenAI API key is configured"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} OpenAI API key not found in .env"
        echo -e "${YELLOW}→${NC} Add your key: OPENAI_API_KEY=sk-your-key"
    fi
else
    echo -e "${RED}✗${NC} .env file not found"
    echo -e "${YELLOW}→${NC} Run: cp .env.example .env"
    ((CHECKS_FAILED++))
fi

# 5. Check if server is running
echo ""
echo "5. Checking server..."
if curl -s http://localhost:8000/health &> /dev/null; then
    echo -e "${GREEN}✓${NC} Server is running"
    ((CHECKS_PASSED++))
    
    # Check health status
    HEALTH=$(curl -s http://localhost:8000/health)
    if echo $HEALTH | grep -q '"status":"healthy"'; then
        echo -e "${GREEN}✓${NC} All services are healthy"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} Some services may be unhealthy"
        echo $HEALTH | jq
    fi
else
    echo -e "${YELLOW}⚠${NC} Server is not running"
    echo -e "${YELLOW}→${NC} Start with: python src/main.py"
fi

# 6. Check sample data
echo ""
echo "6. Checking sample data..."
if curl -s http://localhost:8000/health &> /dev/null; then
    METRICS=$(curl -s http://localhost:8000/api/v1/dashboard/metrics)
    RECORDS=$(echo $METRICS | jq -r '.total_records')
    
    if [ "$RECORDS" -gt "0" ]; then
        echo -e "${GREEN}✓${NC} Sample data loaded ($RECORDS records)"
        ((CHECKS_PASSED++))
    else
        echo -e "${YELLOW}⚠${NC} No sample data found"
        echo -e "${YELLOW}→${NC} Run: python scripts/setup_demo.py"
    fi
fi

# 7. Check sample policy
echo ""
echo "7. Checking sample policy..."
if [ -f "sample_aml_policy.pdf" ]; then
    echo -e "${GREEN}✓${NC} Sample policy PDF exists"
    ((CHECKS_PASSED++))
else
    echo -e "${YELLOW}⚠${NC} Sample policy not found"
    echo -e "${YELLOW}→${NC} Run: python scripts/create_sample_policy.py"
fi

# Summary
echo ""
echo "================================"
echo "Summary:"
echo -e "${GREEN}✓ Passed: $CHECKS_PASSED${NC}"
if [ $CHECKS_FAILED -gt 0 ]; then
    echo -e "${RED}✗ Failed: $CHECKS_FAILED${NC}"
fi
echo ""

if [ $CHECKS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All checks passed! You're ready for the demo!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠ Some checks failed. Please fix the issues above.${NC}"
    exit 1
fi
