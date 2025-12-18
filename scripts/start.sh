#!/bin/bash
# Focus Mate - Start Both Backend and Frontend

set -e

# Color codes for better visibility
COLOR_RESET='\033[0m'
COLOR_BLUE='\033[0;34m'
COLOR_CYAN='\033[0;36m'
COLOR_GREEN='\033[0;32m'
COLOR_YELLOW='\033[1;33m'
COLOR_MAGENTA='\033[0;35m'
COLOR_RED='\033[0;31m'
COLOR_WHITE='\033[1;37m'

# Section separator function
print_section() {
    local color=$1
    local title=$2
    echo ""
    echo -e "${color}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLOR_RESET}"
    echo -e "${color}  ${title}${COLOR_RESET}"
    echo -e "${color}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${COLOR_RESET}"
    echo ""
}

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

print_section "$COLOR_BLUE" "🚀 Focus Mate - Starting Backend and Frontend"
echo -e "${COLOR_WHITE}   Working directory: $(pwd)${COLOR_RESET}"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    [ -n "$BACKEND_PID" ] && kill $BACKEND_PID 2>/dev/null || true
    [ -n "$FRONTEND_PID" ] && kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
print_section "$COLOR_CYAN" "🔧 Backend Setup"
cd "$PROJECT_ROOT/backend"

# Find compatible Python version (prefer 3.13, then 3.12, fallback to 3.x)
PYTHON_CMD=""
if command -v python3.13 &> /dev/null; then
    PYTHON_CMD="python3.13"
    echo -e "${COLOR_GREEN}✅ Using Python 3.13${COLOR_RESET}"
elif command -v python3.12 &> /dev/null; then
    PYTHON_CMD="python3.12"
    echo -e "${COLOR_GREEN}✅ Using Python 3.12${COLOR_RESET}"
elif command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}' | cut -d. -f1,2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)

    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 12 ]); then
        echo -e "${COLOR_RED}❌ Error: Python 3.12 or 3.13 is required for backend${COLOR_RESET}"
        echo "   Current version: $(python3 --version)"
        echo "   Please install Python 3.12 or 3.13"
        exit 1
    fi

    if [ "$PYTHON_MINOR" -ge 14 ]; then
        echo -e "${COLOR_YELLOW}⚠️  Warning: Python 3.14+ detected. This may cause compatibility issues.${COLOR_RESET}"
        echo "   Recommended: Install Python 3.13 or 3.12"
        echo "   Setting compatibility flag..."
        export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1
    fi

    PYTHON_CMD="python3"
else
    echo -e "${COLOR_RED}❌ Error: Python 3 not found${COLOR_RESET}"
    exit 1
fi

echo -e "${COLOR_WHITE}   Using: $($PYTHON_CMD --version)${COLOR_RESET}"

print_section "$COLOR_GREEN" "📦 Environment Setup"

if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${COLOR_GREEN}✅ Created .env from .env.example${COLOR_RESET}"
    else
        echo -e "${COLOR_YELLOW}⚠️  Warning: .env.example not found${COLOR_RESET}"
    fi
fi

VENV_DIR="venv"
NEEDS_INSTALL=false
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Creating virtual environment with $PYTHON_CMD..."
    $PYTHON_CMD -m venv $VENV_DIR
    NEEDS_INSTALL=true
else
    # Check if the Python version used to create the venv is the same as the current one
    VENV_PYTHON_PATH="$VENV_DIR/bin/python"
    if [ -f "$VENV_PYTHON_PATH" ]; then
        VENV_PYTHON_VERSION=$($VENV_PYTHON_PATH --version 2>&1 | awk '{print $2}')
        CURRENT_PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | awk '{print $2}')
        if [ "$VENV_PYTHON_VERSION" != "$CURRENT_PYTHON_VERSION" ]; then
            echo -e "${COLOR_YELLOW}⚠️  Virtual environment Python version mismatch (Venv: $VENV_PYTHON_VERSION, Current: $CURRENT_PYTHON_VERSION)${COLOR_RESET}"
            echo "   Recreating virtual environment for compatibility..."
            rm -rf $VENV_DIR
            $PYTHON_CMD -m venv $VENV_DIR
            NEEDS_INSTALL=true
        fi
    else
        echo -e "${COLOR_YELLOW}⚠️  Virtual environment is corrupted. Recreating...${COLOR_RESET}"
        rm -rf $VENV_DIR
        $PYTHON_CMD -m venv $VENV_DIR
        NEEDS_INSTALL=true
    fi
fi

# Activate the virtual environment
source "$VENV_DIR/bin/activate"

# Install or sync dependencies
if [ "$NEEDS_INSTALL" = true ]; then
    echo "📥 Upgrading pip and installing dependencies for the first time..."
    pip install --upgrade pip
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${COLOR_RED}❌ Error: Failed to install dependencies${COLOR_RESET}"
        echo "   This might be due to Python version compatibility."
        echo "   If you see errors related to 'pyo3', try running:"
        echo "   export PYO3_USE_ABI3_FORWARD_COMPATIBILITY=1"
        exit 1
    fi
    echo -e "${COLOR_GREEN}✅ Virtual environment created and dependencies installed${COLOR_RESET}"
else
    echo "🔄 Syncing dependencies from requirements.txt..."
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo -e "${COLOR_RED}❌ Error: Failed to sync dependencies${COLOR_RESET}"
        exit 1
    fi
    echo -e "${COLOR_GREEN}✅ Dependencies are up to date.${COLOR_RESET}"
fi

# Verify uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo -e "${COLOR_RED}❌ Error: uvicorn not found in virtual environment${COLOR_RESET}"
    echo "   Installing dependencies..."
    pip install -r requirements.txt
    if ! command -v uvicorn &> /dev/null; then
        echo -e "${COLOR_RED}❌ Error: Failed to install uvicorn${COLOR_RESET}"
        exit 1
    fi
fi

# Check DATABASE_URL in .env
print_section "$COLOR_MAGENTA" "🗄️  Database Configuration"

SUPABASE_URL=""
if [ -f .env ]; then
    DATABASE_URL=$(grep "^DATABASE_URL=" .env | cut -d'=' -f2- | tr -d '"' | tr -d "'" | head -1)
    if [ -z "$DATABASE_URL" ]; then
        echo -e "${COLOR_YELLOW}⚠️  Warning: DATABASE_URL not found in .env file${COLOR_RESET}"
        echo "   Using default local PostgreSQL connection"
    else
        # Check if it's Supabase and extract project reference
        if echo "$DATABASE_URL" | grep -qi "supabase"; then
            echo -e "${COLOR_GREEN}✅ Supabase connection detected${COLOR_RESET}"
            echo "   Connection: ${DATABASE_URL:0:60}..."

            # Extract Supabase project reference from DATABASE_URL
            if echo "$DATABASE_URL" | grep -qoE "xevhqwaxxlcsqzhmawjr|db\.[a-z0-9]+\.supabase\.co"; then
                SUPABASE_PROJECT=$(echo "$DATABASE_URL" | grep -oE "xevhqwaxxlcsqzhmawjr|db\.[a-z0-9]+\.supabase\.co" | head -1)
                if [[ "$SUPABASE_PROJECT" == "xevhqwaxxlcsqzhmawjr" ]]; then
                    SUPABASE_URL="https://supabase.com/dashboard/project/xevhqwaxxlcsqzhmawjr"
                elif [[ "$SUPABASE_PROJECT" =~ ^db\. ]]; then
                    PROJECT_REF=$(echo "$SUPABASE_PROJECT" | sed 's/db\.\([^.]*\)\.supabase\.co/\1/')
                    SUPABASE_URL="https://supabase.com/dashboard/project/$PROJECT_REF"
                fi
            fi
        elif echo "$DATABASE_URL" | grep -qi "localhost\|127.0.0.1"; then
            echo -e "${COLOR_GREEN}✅ Local PostgreSQL connection detected${COLOR_RESET}"
        else
            echo -e "${COLOR_GREEN}✅ Database connection configured${COLOR_RESET}"
        fi
    fi
else
    echo -e "${COLOR_YELLOW}⚠️  Warning: .env file not found${COLOR_RESET}"
fi
echo ""

# Test database connection before migrations
print_section "$COLOR_MAGENTA" "🔌 Database Connection Test"
if [ -f "venv/bin/python" ] && [ -f "scripts/check_supabase_connection.py" ]; then
    # Use existing connection check script if available
    if venv/bin/python scripts/check_supabase_connection.py > /tmp/db_connection_test.log 2>&1; then
        cat /tmp/db_connection_test.log
        echo ""
    else
        # If script fails, try simple connection test
        cat /tmp/db_connection_test.log 2>/dev/null || true
        echo ""
        echo "⚠️  Warning: Database connection test failed"
        echo "   Migrations may fail if database is not accessible"
        echo "   Continuing anyway..."
        echo ""
    fi
    rm -f /tmp/db_connection_test.log
elif [ -f "venv/bin/python" ]; then
    # Fallback: Create a simple connection test script
    TEST_SCRIPT="/tmp/test_db_connection_$$.py"
    cat > "$TEST_SCRIPT" << 'PYEOF'
import asyncio
import sys
import os
from pathlib import Path

# Change to backend directory
backend_dir = Path(__file__).parent.parent / "backend"
os.chdir(backend_dir)
sys.path.insert(0, str(backend_dir))

try:
    from dotenv import load_dotenv
    load_dotenv(backend_dir / ".env")

    database_url = os.getenv("DATABASE_URL", "")
    if not database_url:
        print("⚠️  DATABASE_URL not found in .env")
        sys.exit(0)  # Not an error, just skip

    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    engine = create_async_engine(database_url, pool_pre_ping=True)

    async def test():
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT version()"))
                version = result.scalar()
                print(f"✅ Database connection successful!")
                print(f"   PostgreSQL: {version.split(',')[0]}")

                # Check if alembic_version table exists
                try:
                    result = await conn.execute(text("SELECT version_num FROM alembic_version LIMIT 1"))
                    alembic_version = result.scalar()
                    print(f"   Current migration: {alembic_version}")
                except:
                    print("   Migration status: No migrations applied yet")

                await engine.dispose()
                return True
        except Exception as e:
            error_msg = str(e)
            if len(error_msg) > 100:
                error_msg = error_msg[:100] + "..."
            print(f"❌ Database connection failed: {error_msg}")
            await engine.dispose()
            return False

    success = asyncio.run(test())
    sys.exit(0 if success else 1)
except ImportError as e:
    print(f"⚠️  Cannot test connection: {e}")
    print("   Dependencies may not be installed yet")
    sys.exit(0)  # Not fatal, continue
except Exception as e:
    print(f"⚠️  Connection test error: {e}")
    sys.exit(0)  # Not fatal, continue
PYEOF

    # Run connection test
    if venv/bin/python "$TEST_SCRIPT"; then
        echo ""
    else
        echo ""
        echo "⚠️  Warning: Database connection test failed"
        echo "   Migrations may fail if database is not accessible"
        echo "   Continuing anyway..."
        echo ""
    fi
    rm -f "$TEST_SCRIPT"
else
    echo "⚠️  Cannot test connection: venv/bin/python not found"
fi

# Run migrations
print_section "$COLOR_YELLOW" "🔄 Database Migrations"
if [ -f "venv/bin/alembic" ]; then
    # Use venv's alembic explicitly
    if venv/bin/alembic upgrade head; then
        echo -e "${COLOR_GREEN}✅ Database migrations completed successfully${COLOR_RESET}"
    else
        echo -e "${COLOR_YELLOW}⚠️  Warning: Database migration failed or already up to date${COLOR_RESET}"
        echo "   This is normal if migrations are already applied"
        echo "   Check logs above for details if needed"
    fi
elif command -v alembic &> /dev/null; then
    # Fallback to system alembic if venv alembic not found
    if alembic upgrade head; then
        echo -e "${COLOR_GREEN}✅ Database migrations completed successfully${COLOR_RESET}"
    else
        echo -e "${COLOR_YELLOW}⚠️  Warning: Database migration failed or already up to date${COLOR_RESET}"
    fi
else
    echo -e "${COLOR_YELLOW}⚠️  Alembic not found, skipping migrations${COLOR_RESET}"
    echo "   Install dependencies: pip install -r requirements.txt"
fi

# Check if port 8000 is already in use and kill ALL processes
BACKEND_PORT=8000
echo "🔎 Checking for processes on port $BACKEND_PORT..."
PIDS_TO_KILL=$(lsof -ti:$BACKEND_PORT 2>/dev/null || true)

if [ -n "$PIDS_TO_KILL" ]; then
    echo -e "${COLOR_YELLOW}⚠️  Port $BACKEND_PORT is already in use by PID(s): $PIDS_TO_KILL${COLOR_RESET}"
    echo "   This script will automatically terminate them."
    
    # Kill all found PIDs
    if echo "$PIDS_TO_KILL" | xargs kill -9; then
        sleep 1
        echo -e "${COLOR_GREEN}✅ Conflicting processes terminated.${COLOR_RESET}"
    else
        echo -e "${COLOR_RED}❌ Failed to terminate conflicting processes. Please do it manually.${COLOR_RESET}"
        exit 1
    fi
else
    echo -e "${COLOR_GREEN}✅ Port $BACKEND_PORT is free.${COLOR_RESET}"
fi

# Start backend in background using venv python
print_section "$COLOR_RED" "🚀 Backend Server"
venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > /tmp/focusmate-backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for process to start
sleep 2

# Check if process is still running
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${COLOR_RED}❌ Error: Backend failed to start!${COLOR_RESET}"
    echo "📋 Checking logs..."
    tail -20 /tmp/focusmate-backend.log
    exit 1
fi

echo -e "${COLOR_GREEN}✅ Backend started (PID: $BACKEND_PID)${COLOR_RESET}"
echo -e "   ${COLOR_CYAN}📍 API:${COLOR_RESET} http://localhost:8000"
echo -e "   ${COLOR_CYAN}📚 Docs:${COLOR_RESET} http://localhost:8000/docs"

# Wait for backend to be ready
echo ""
echo -e "${COLOR_YELLOW}⏳ Waiting for backend to be ready...${COLOR_RESET}"
BACKEND_READY=false
for i in {1..30}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${COLOR_GREEN}✅ Backend is ready!${COLOR_RESET}"
        BACKEND_READY=true
        break
    fi
    # Check if process is still running
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${COLOR_RED}❌ Error: Backend process died!${COLOR_RESET}"
        echo "📋 Last 20 lines of log:"
        tail -20 /tmp/focusmate-backend.log
        exit 1
    fi
    sleep 1
done

if [ "$BACKEND_READY" = false ]; then
    echo -e "${COLOR_YELLOW}⚠️  Warning: Backend did not become ready within 30 seconds${COLOR_RESET}"
    echo "📋 Checking logs..."
    tail -20 /tmp/focusmate-backend.log
    echo ""
    echo "💡 Tip: Check logs manually: tail -f /tmp/focusmate-backend.log"
fi

# Start Frontend
print_section "$COLOR_MAGENTA" "🎨 Frontend Setup"
cd "$PROJECT_ROOT/frontend"
if [ ! -d "node_modules" ]; then
    npm install
fi
if [ ! -f .env ]; then
    cp .env.example .env 2>/dev/null || true
fi

# Check if port 3000 is already in use
FRONTEND_PORT=3000
FRONTEND_PORT_PID=$(lsof -ti:$FRONTEND_PORT 2>/dev/null || true)

SKIP_FRONTEND=false
if [ -n "$FRONTEND_PORT_PID" ]; then
    echo -e "${COLOR_YELLOW}⚠️  Port $FRONTEND_PORT is already in use (PID: $FRONTEND_PORT_PID)${COLOR_RESET}"
    echo "   Port is already in use. Kill the process and restart? (y/n)"
    echo "   (Auto-restart in 5 seconds if no response)"

    # Read with timeout (5 seconds)
    read -t 5 -r RESPONSE || RESPONSE="y"

    if [[ "$RESPONSE" =~ ^[Yy]$ ]] || [ -z "$RESPONSE" ]; then
        echo "🛑 Killing the process..."
        kill -9 $FRONTEND_PORT_PID 2>/dev/null || true
        sleep 1
        echo -e "${COLOR_GREEN}✅ Process terminated.${COLOR_RESET}"
    else
        echo -e "${COLOR_YELLOW}❌ User cancelled. Skipping frontend.${COLOR_RESET}"
        SKIP_FRONTEND=true
    fi
fi

# Start frontend in background (only if not cancelled)
if [ "$SKIP_FRONTEND" = false ]; then
    npm run dev > /tmp/focusmate-frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo -e "${COLOR_GREEN}✅ Frontend started (PID: $FRONTEND_PID)${COLOR_RESET}"
    echo -e "   ${COLOR_MAGENTA}📍 Frontend:${COLOR_RESET} http://localhost:3000"
else
    FRONTEND_PID=""
    echo -e "${COLOR_YELLOW}⏭️  Skipping frontend startup.${COLOR_RESET}"
fi

if [ "$SKIP_FRONTEND" = true ]; then
    print_section "$COLOR_GREEN" "🎉 Backend Service Running"
    echo -e "${COLOR_WHITE}📋 Service Status:${COLOR_RESET}"
    echo -e "   ${COLOR_CYAN}Backend:${COLOR_RESET}  http://localhost:8000"
    echo -e "   ${COLOR_CYAN}API Docs:${COLOR_RESET} http://localhost:8000/docs"
    echo -e "   ${COLOR_YELLOW}WS Test:${COLOR_RESET}  file://${PROJECT_ROOT}/backend/test_websocket.html"
    echo -e "   ${COLOR_YELLOW}Frontend:${COLOR_RESET} (skipped)"
    if [ -n "$SUPABASE_URL" ]; then
        echo -e "   ${COLOR_MAGENTA}Supabase:${COLOR_RESET} $SUPABASE_URL"
    fi
    echo ""
    echo -e "${COLOR_WHITE}📝 Logs:${COLOR_RESET}"
    echo -e "   ${COLOR_CYAN}Backend:${COLOR_RESET}  tail -f /tmp/focusmate-backend.log"
    echo ""
    echo -e "${COLOR_YELLOW}Press Ctrl+C to stop the service${COLOR_RESET}"
    echo ""
    # Wait only for backend
    wait $BACKEND_PID
else
    print_section "$COLOR_GREEN" "🎉 All Services Running"
    echo -e "${COLOR_WHITE}📋 Service Status:${COLOR_RESET}"
    echo -e "   ${COLOR_CYAN}Backend:${COLOR_RESET}  http://localhost:8000"
    echo -e "   ${COLOR_MAGENTA}Frontend:${COLOR_RESET} http://localhost:3000"
    echo -e "   ${COLOR_CYAN}API Docs:${COLOR_RESET} http://localhost:8000/docs"
    echo -e "   ${COLOR_YELLOW}WS Test:${COLOR_RESET}  file://${PROJECT_ROOT}/backend/test_websocket.html"
    if [ -n "$SUPABASE_URL" ]; then
        echo -e "   ${COLOR_MAGENTA}Supabase:${COLOR_RESET} $SUPABASE_URL"
    fi
    echo ""
    echo -e "${COLOR_WHITE}📝 Logs:${COLOR_RESET}"
    echo -e "   ${COLOR_CYAN}Backend:${COLOR_RESET}  tail -f /tmp/focusmate-backend.log"
    echo -e "   ${COLOR_MAGENTA}Frontend:${COLOR_RESET} tail -f /tmp/focusmate-frontend.log"
    echo ""
    echo -e "${COLOR_YELLOW}Press Ctrl+C to stop all services${COLOR_RESET}"
    echo ""
    # Wait for both processes
    wait
fi

