#!/bin/bash
# If OS environments differ, run the dev server via Docker for consistency.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

export DATABASE_URL="postgresql+asyncpg://postgres:postgres@localhost:5432/focus_mate"
export REDIS_URL="redis://localhost:6379/0"

echo "🔧 Local DB override enabled"
echo "   DATABASE_URL=$DATABASE_URL"
echo "   REDIS_URL=$REDIS_URL"
echo ""

# Docker dev flow (commented out by default).
# docker-compose -f docker-compose.yml up -d postgres redis
# docker-compose -f docker-compose.yml build backend
# docker-compose -f docker-compose.yml up -d backend

echo "🔍 Checking local services..."

# Check Redis
if ! pgrep -x "redis-server" > /dev/null; then
    echo "⚠️  Redis is not running. Starting via Homebrew..."
    brew services start redis
    sleep 1
else
    echo "✅ Redis is running"
fi

# Check Postgres
if ! pgrep -x "postgres" > /dev/null && ! pgrep -x "postmaster" > /dev/null; then
    echo "⚠️  Postgres is not running. Starting via Homebrew..."
    brew services start postgresql
    sleep 1
else
    echo "✅ Postgres is running"
fi

echo ""

echo "🗄️  Running Alembic migrations (local DB)..."
if [ -x "venv/bin/alembic" ]; then
    DATABASE_URL="$DATABASE_URL" REDIS_URL="$REDIS_URL" venv/bin/alembic upgrade head
elif command -v alembic > /dev/null 2>&1; then
    DATABASE_URL="$DATABASE_URL" REDIS_URL="$REDIS_URL" alembic upgrade head
else
    echo "⚠️  Alembic not found; run.sh will attempt migrations"
fi
echo ""

./run.sh
