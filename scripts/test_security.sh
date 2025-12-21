#!/bin/bash

# Security Test Runner
# 보안 테스트 전용 실행 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔒 보안 테스트 실행${NC}"
echo ""

cd "$BACKEND_DIR"

# Activate virtual environment
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
elif [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
    source "$BACKEND_DIR/venv/bin/activate"
fi

# Run security tests
pytest tests/security/ -v --tb=short

# Also run bandit security linter
if command -v bandit &> /dev/null; then
    echo ""
    echo -e "${BLUE}🔍 Bandit 보안 린터 실행${NC}"
    bandit -r app/ -f json -o /tmp/bandit_report.json || true
    bandit -r app/ -f txt || true
fi

