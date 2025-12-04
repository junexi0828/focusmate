#!/bin/bash
# Focus Mate Backend - Setup Script
# Sets up environment and installs dependencies

set -e

echo "🔧 Focus Mate Backend - Setup..."
echo ""

# Find compatible Python version
PYTHON_CMD=""
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
    echo "✅ Using Python 3.13"
elif command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    echo "✅ Using Python 3.12"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
        echo "❌ Error: Python 3.12 or 3.13 is required"
        echo "   Current version: $PYTHON_VERSION"
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

echo "   Version: $($PYTHON_CMD --version)"
echo ""

# Create .env from .env.example
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        echo "📝 Creating .env from .env.example..."
        cp .env.example .env
        echo "✅ .env file created"
        echo "   ⚠️  Important: Update SECRET_KEY in .env before production use!"
    else
        echo "❌ Error: .env.example not found!"
        exit 1
    fi
else
    echo "✅ .env file already exists"
fi
echo ""

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
    # Check if we should recreate with correct Python version
    if [ -f venv/bin/python ]; then
        VENV_PYTHON=$(venv/bin/python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        CURRENT_PYTHON=$($PYTHON_CMD --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
        if [ "$VENV_PYTHON" != "$CURRENT_PYTHON" ]; then
            echo "⚠️  Python version mismatch detected"
            echo "   Venv: $VENV_PYTHON, Preferred: $CURRENT_PYTHON"
            read -p "Recreate virtual environment? (y/N) " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                echo "📦 Recreating virtual environment..."
                rm -rf venv
                $PYTHON_CMD -m venv venv
                echo "✅ Virtual environment recreated"
            fi
        fi
    fi
fi
echo ""

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📥 Upgrading pip..."
pip install --upgrade pip
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
if [ ! -f requirements.txt ]; then
    echo "❌ Error: requirements.txt not found!"
    exit 1
fi

pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Error: Failed to install dependencies"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check Python version (should be 3.12 or 3.13)"
    echo "2. Try: pip install --upgrade pip setuptools wheel"
    echo "3. For Python 3.14, you may need to set:"
    echo "   export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1"
    exit 1
fi

# Install dev dependencies if available
if [ -f requirements-dev.txt ]; then
    echo ""
    echo "📦 Installing development dependencies..."
    pip install -r requirements-dev.txt
fi

# Run migrations
echo ""
echo "🗄️  Running database migrations..."
if command -v alembic &> /dev/null; then
    alembic upgrade head || echo "⚠️  Migration skipped (database may not be initialized)"
else
    echo "⚠️  Alembic not found, skipping migrations"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Review and update .env file if needed"
echo "  2. Run: ./run.sh (or uvicorn app.main:app --reload)"
echo ""

