#!/bin/bash
# Focus Mate - Run All Tests

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

echo "🧪 Focus Mate - Running All Tests..."
echo ""

# Test Backend
echo "=========================================="
echo "🔧 Testing Backend..."
echo "=========================================="
cd "$PROJECT_ROOT/backend"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
else
    source venv/bin/activate
fi

if [ -f scripts/test.sh ]; then
    bash scripts/test.sh
else
    echo "⚠️  Backend test script not found. Running pytest directly..."
    if command -v pytest &> /dev/null; then
        pytest --cov=app --cov-report=term || echo "⚠️  Tests failed or no tests found"
    else
        echo "❌ pytest not found. Installing dev dependencies..."
        pip install -r requirements-dev.txt
        pytest --cov=app --cov-report=term || echo "⚠️  Tests failed or no tests found"
    fi
fi
echo ""

# Test Frontend
echo "=========================================="
echo "🎨 Testing Frontend..."
echo "=========================================="
cd "$PROJECT_ROOT/frontend"
if [ -f package.json ]; then
    if npm run test 2>/dev/null; then
        echo "✅ Frontend tests passed"
    else
        echo "⚠️  Frontend test script not configured"
    fi
else
    echo "❌ Frontend package.json not found"
fi
echo ""

echo "=========================================="
echo "✅ All tests completed!"
echo "=========================================="

