#!/bin/bash
# Focus Mate Backend - Quick Start Script

set -e

echo "🚀 Focus Mate Backend - Starting..."
echo ""

# Find compatible Python version (prefer 3.13, then 3.12, fallback to 3.x)
PYTHON_CMD=""
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
    echo "✅ Using Python 3.13"
elif command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    echo "✅ Using Python 3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
        echo "❌ Error: Python 3.12 or 3.13 is required"
        echo "   Current version: $(python3 --version)"
        echo "   Please install Python 3.12 or 3.13"
        exit 1
    fi

    if [ "$PYTHON_MINOR" -ge 14 ]; then
        echo "⚠️  Warning: Python 3.14+ detected. This may cause compatibility issues."
        echo "   Recommended: Install Python 3.13 or 3.12"
        echo "   Setting compatibility flag..."
        export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
    fi

    PYTHON_CMD="python3"
else
    echo "❌ Error: Python 3 not found"
    exit 1
fi

echo "   Using: $($PYTHON_CMD --version)"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from .env.example..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ .env file created. Please review and update if needed."
        echo "   ⚠️  Important: Update SECRET_KEY in .env before production use!"
    else
        echo "❌ Error: .env.example not found!"
        exit 1
    fi
    echo ""
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
    echo ""
else
    # Check if venv Python version matches
    if [ -f venv/bin/python ]; then
        VENV_PYTHON=$(venv/bin/python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        CURRENT_PYTHON=$($PYTHON_CMD --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        if [ "$VENV_PYTHON" != "$CURRENT_PYTHON" ]; then
            echo "⚠️  Virtual environment Python version mismatch"
            echo "   Venv: $VENV_PYTHON, Preferred: $CURRENT_PYTHON"
            echo "   Recreating virtual environment..."
            rm -rf venv
            $PYTHON_CMD -m venv venv
            echo "✅ Virtual environment recreated"
            echo ""
        fi
    fi
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
echo ""

# Check if requirements.txt exists
if [ ! -f requirements.txt ]; then
    echo "❌ Error: requirements.txt not found!"
    exit 1
fi

echo "Installing from requirements.txt..."
pip install -r requirements.txt

# Check if installation was successful
if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error: Failed to install dependencies"
    echo "   This might be due to Python version compatibility issues"
    echo "   Recommended: Use Python 3.12 or 3.13"
    exit 1
fi

# Verify uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "❌ Error: uvicorn not found after installation"
    echo "   Trying to reinstall..."
    pip install uvicorn[standard]
    if ! command -v uvicorn &> /dev/null; then
        echo "❌ Error: Failed to install uvicorn"
        exit 1
    fi
fi

# Run migrations if alembic is available
if command -v alembic &> /dev/null; then
    echo ""
    echo "🗄️  Running database migrations..."
    alembic upgrade head 2>/dev/null || echo "⚠️  Migration skipped"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Starting server..."
echo "📍 API: http://localhost:8000"
echo "📚 Docs: http://localhost:8000/docs"
echo ""

# Run server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
