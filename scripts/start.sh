#!/bin/bash
# Focus Mate - Start Both Backend and Frontend

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo "🚀 Focus Mate - Starting Backend and Frontend..."
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo "🔧 Starting Backend..."
cd "$PROJECT_ROOT/backend"

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
        echo "❌ Error: Python 3.12 or 3.13 is required for backend"
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

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env from .env.example"
    else
        echo "⚠️  Warning: .env.example not found"
    fi
fi

if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Error: Failed to install dependencies"
        echo "   This might be due to Python version compatibility"
        echo "   Try: export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1"
        exit 1
    fi
    echo "✅ Virtual environment created and dependencies installed"
else
    source venv/bin/activate
    # Check if we need to reinstall with correct Python version
    VENV_PYTHON=$(venv/bin/python --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    CURRENT_PYTHON=$($PYTHON_CMD --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    if [ "$VENV_PYTHON" != "$CURRENT_PYTHON" ]; then
        echo "⚠️  Virtual environment Python version mismatch"
        echo "   Venv: $VENV_PYTHON, Current: $CURRENT_PYTHON"
        echo "   Recreating virtual environment..."
        rm -rf venv
        $PYTHON_CMD -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
    fi
fi

# Verify uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "❌ Error: uvicorn not found in virtual environment"
    echo "   Installing dependencies..."
    pip install -r requirements.txt
    if ! command -v uvicorn &> /dev/null; then
        echo "❌ Error: Failed to install uvicorn"
        exit 1
    fi
fi

# Run migrations
echo "🗄️  Running database migrations..."
if command -v alembic &> /dev/null; then
    alembic upgrade head 2>/dev/null || echo "⚠️  Migration skipped or failed"
else
    echo "⚠️  Alembic not found, skipping migrations"
fi
echo ""

# Start backend in background using venv python
echo "🚀 Starting backend server..."
venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/focusmate-backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for process to start
sleep 2

# Check if process is still running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Error: Backend failed to start!"
    echo "📋 Checking logs..."
    tail -20 /tmp/focusmate-backend.log
    exit 1
fi

echo "✅ Backend started (PID: $BACKEND_PID)"
echo "   📍 API: http://localhost:8000"
echo "   📚 Docs: http://localhost:8000/docs"
echo ""

# Wait for backend to be ready
echo "⏳ Waiting for backend to be ready..."
BACKEND_READY=false
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "✅ Backend is ready!"
        BACKEND_READY=true
        break
    fi
    # Check if process is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ Error: Backend process died!"
        echo "📋 Last 20 lines of log:"
        tail -20 /tmp/focusmate-backend.log
        exit 1
    fi
    sleep 1
done

if [ "$BACKEND_READY" = false ]; then
    echo "⚠️  Warning: Backend did not become ready within 30 seconds"
    echo "📋 Checking logs..."
    tail -20 /tmp/focusmate-backend.log
    echo ""
    echo "💡 Tip: Check logs manually: tail -f /tmp/focusmate-backend.log"
fi
echo ""

# Start Frontend
echo "🎨 Starting Frontend..."
cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    npm install
fi
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || true
fi

# Start frontend in background
npm run dev > /tmp/focusmate-frontend.log 2>&1 &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"
echo "   📍 Frontend: http://localhost:3000"
echo ""

echo "🎉 All services are running!"
echo ""
echo "📋 Service Status:"
echo "   Backend:  http://localhost:8000"
echo "   Frontend: http://localhost:3000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f /tmp/focusmate-backend.log"
echo "   Frontend: tail -f /tmp/focusmate-frontend.log"
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait

