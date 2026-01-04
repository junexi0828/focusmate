#!/bin/bash
# Focus Mate Backend - Test Script

set -e

# Change to backend directory (script is in backend/scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "🧪 Focus Mate Backend - Running Tests..."
echo "   Working directory: $(pwd)"
echo ""

# Find compatible Python version
PYTHON_CMD=""
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
elif command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 14 ]; then
        export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
    fi
    PYTHON_CMD="python3"
else
    echo "❌ Error: Python 3 not found"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install -r requirements-dev.txt
else
    source venv/bin/activate
fi

# Verify pytest is available
if ! command -v pytest &> /dev/null; then
    echo "❌ Error: pytest not found. Installing dev dependencies..."
    pip install -r requirements-dev.txt
    if ! command -v pytest &> /dev/null; then
        echo "❌ Error: Failed to install pytest"
        exit 1
    fi
fi

# Run tests
echo "📋 Running unit tests..."
if [ -d "tests/unit" ] && [ "$(ls -A tests/unit 2>/dev/null)" ]; then
    pytest tests/unit -v
else
    echo "⚠️  No unit tests found, skipping..."
fi

echo ""
echo "📋 Running integration tests..."
if [ -d "tests/integration" ] && [ "$(ls -A tests/integration 2>/dev/null)" ]; then
    pytest tests/integration -v
else
    echo "⚠️  No integration tests found, skipping..."
fi

echo ""
echo "📋 Running E2E tests..."
if [ -d "tests/e2e" ] && [ "$(ls -A tests/e2e 2>/dev/null)" ]; then
    pytest tests/e2e -v
else
    echo "⚠️  No E2E tests found, skipping..."
fi

echo ""
echo "📊 Generating coverage report..."
pytest --cov=app --cov-report=html --cov-report=term

echo ""
echo "✅ All tests completed!"
echo "📊 Coverage report: htmlcov/index.html"

