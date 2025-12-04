#!/bin/bash
# Focus Mate Backend - Fix Python Version Script
# Recreates virtual environment with compatible Python version

set -e

echo "🔧 Fixing Python Version for Backend..."
echo ""

# Find compatible Python version
PYTHON_CMD=""
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
    echo "✅ Found Python 3.13"
elif command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    echo "✅ Found Python 3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -ge 14 ]; then
        echo "⚠️  Python 3.14+ detected. Setting compatibility flag..."
        export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
    fi
    PYTHON_CMD="python3"
    echo "⚠️  Using Python $PYTHON_VERSION (may have compatibility issues)"
else
    echo "❌ Error: Python 3 not found"
    echo "   Please install Python 3.12 or 3.13"
    exit 1
fi

echo "   Version: $($PYTHON_CMD --version)"
echo ""

# Backup .env if exists
if [ -f .env ]; then
    echo "📝 Backing up .env..."
    cp .env .env.backup
fi

# Remove old virtual environment
if [ -d "venv" ]; then
    echo "🗑️  Removing old virtual environment..."
    rm -rf venv
fi

# Create new virtual environment
echo "📦 Creating new virtual environment with $PYTHON_CMD..."
$PYTHON_CMD -m venv venv
source venv/bin/activate

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
if [ -n "$PYO3_USE_ABI3_FORWARD_COMPATIBILITY" ]; then
    echo "   Using compatibility flag for Python 3.14+"
fi

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error: Failed to install dependencies"
    if [ -n "$PYO3_USE_ABI3_FORWARD_COMPATIBILITY" ]; then
        echo "   Compatibility flag is already set"
    else
        echo "   Try: export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1"
    fi
    exit 1
fi

# Install dev dependencies
if [ -f requirements-dev.txt ]; then
    echo "📦 Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

echo ""
echo "✅ Virtual environment fixed!"
echo ""
echo "Next steps:"
echo "  1. Run: ./run.sh"
echo "  2. Or: source venv/bin/activate && uvicorn app.main:app --reload"
echo ""

