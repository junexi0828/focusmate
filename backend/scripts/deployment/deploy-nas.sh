#!/bin/bash
set -e
trap 'echo "❌ Deployment failed. Check logs above."' ERR

# ==========================================
# FocusMate NAS Deployment Script
# ==========================================
# Usage: ./deploy-nas.sh
# Run this script from the 'backend' directory.
# ==========================================

NAS_USER="juns"
NAS_HOST="192.168.45.58"
NAS_DIR="/volume1/web/focusmate-backend"
REMOTE_PYTHON="/volume1/web/miniconda3/envs/focusmate_env/bin/python"

# Ensure we are in the 'backend' directory (project root for backend)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$BACKEND_ROOT"

# Safety: ensure we are in a git repo and on main/master
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "❌ Not inside a git repository. Abort."
    exit 1
fi

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
if [ "$CURRENT_BRANCH" != "main" ] && [ "$CURRENT_BRANCH" != "master" ] && [ "$CURRENT_BRANCH" != "develop" ]; then
    echo "⚠️  Current branch is '$CURRENT_BRANCH'. Skipping deployment (main/master/develop only)."
    exit 0
fi

# 0. Stop Service (Release Locks)
# ⚠️ DISABLED: Now using Docker - restart manually with docker-compose
# echo "🛑 Stopping Remote Service..."
# ssh "$NAS_USER@$NAS_HOST" "cd $NAS_DIR && bash stop-nas.sh"

# 1. Deployment: Rsync Code
# Excludes virtual environments, cache, git history, and local .env (protecting remote config)
echo "📦 Syncing files..."
rsync -avz --progress \
    --exclude 'venv' \
    --exclude '.venv' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude '.DS_Store' \
    --exclude '._*' \
    --exclude 'logs' \
    --rsync-path="/usr/bin/rsync" \
    ./ "$NAS_USER@$NAS_HOST:$NAS_DIR/"

echo "✅ File sync complete."

# 1.5 Optional: Install dependencies on NAS (mirrors old webhook safety)
# ⚠️ DISABLED: Now using Docker - dependencies managed in Docker image
# if [ "${INSTALL_DEPS:-1}" = "1" ]; then
#     echo "📦 Installing dependencies on NAS (requirements.txt)..."
#     ssh "$NAS_USER@$NAS_HOST" "cd $NAS_DIR && if [ -f requirements.txt ] && [ -x $REMOTE_PYTHON ]; then $REMOTE_PYTHON -m pip install -r requirements.txt --quiet; else echo 'ℹ️  requirements.txt or python missing, skipping deps'; fi"
# fi

# 1.6 Optional: Run Database Migrations
# ⚠️ DISABLED: Now using Docker - run migrations inside Docker container
# if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
#     echo "🗄️  Running Database Migrations..."
#     ssh "$NAS_USER@$NAS_HOST" "cd $NAS_DIR && export PYTHONPATH=. && $REMOTE_PYTHON scripts/database/smart_migrate.py"
# fi

# 2. Restart Service (Start only)
# ⚠️ DISABLED: Now using Docker - restart manually with docker-compose
# echo "🔄 Starting Remote Service..."
# ssh "$NAS_USER@$NAS_HOST" "cd $NAS_DIR && bash start-nas.sh"

echo "🎉 File Sync Successfully Completed!"

# =============================================================================
# 4. Run Database Migrations (Automatic)
# =============================================================================
# ⚠️  SINGLE INSTANCE ONLY - This approach works for 1 server deployment
#
# Current Setup:
#   - ✅ Safe: Only 1 NAS server runs this script
#   - ✅ No concurrency issues with DB migrations
#
# 🚨 WARNING: Multi-Instance Environment (2+ servers)
#   If you scale to multiple servers in the future, this will cause RACE CONDITIONS:
#   - Multiple servers may run migrations simultaneously
#   - Can lead to duplicate migrations, deadlocks, or data corruption
#
# Solutions for Multi-Instance Deployment:
#   Option 1: Distributed Lock (Recommended)
#     - Use Redis/database lock before running migrations
#     - Example: https://github.com/mosparo/alembic-utils
#     - Code: LOCK_KEY="migration_lock" and check before upgrade
#
#   Option 2: Designated Migration Server
#     - Only run migrations on one designated server (e.g., server-1)
#     - Other servers skip migration step
#     - Add condition: if [ "$HOSTNAME" = "server-1" ]; then alembic upgrade head; fi
#
#   Option 3: Pre-Deployment Migration
#     - Run migrations separately BEFORE deploying to any server
#     - Use CI/CD pipeline to run migrations once
#     - Then deploy code to all servers
#
#   Option 4: Alembic Locking Extension
#     - Install: pip install alembic-postgresql-enum (includes lock support)
#     - Configure alembic to use advisory locks
#
# For now (single NAS): This implementation is safe and recommended ✅
#
# Example Implementation for Multi-Instance (Redis Lock):
#   Before migration:
#     LOCK_ACQUIRED=$(redis-cli SET migration_lock $(hostname) NX EX 300)
#     if [ "$LOCK_ACQUIRED" = "OK" ]; then
#       alembic upgrade head
#       redis-cli DEL migration_lock
#     else
#       echo "Another server is running migrations, skipping..."
#     fi
#
# Example Implementation for Multi-Instance (PostgreSQL Advisory Lock):
#   In Python migration script:
#     from sqlalchemy import text
#     with engine.connect() as conn:
#       conn.execute(text("SELECT pg_advisory_lock(123456789)"))
#       alembic.upgrade("head")
#       conn.execute(text("SELECT pg_advisory_unlock(123456789)"))
# =============================================================================
# 4. Stop Backend (Release DB Locks for Safe Migration)
# We stop the backend to ensure no active connections are holding locks on tables
echo -e "🛑 Stopping backend to release DB locks..."
ssh "juns@$NAS_HOST" "cd $NAS_DIR && sudo /usr/local/bin/docker-compose -f docker-compose.nas.yml stop backend"

# 5. Run Database Migrations
echo -e "🗄️  Running database migrations..."
# Use 'run --rm' to execute migration in a temporary container (since main backend is stopped)
ssh "juns@$NAS_HOST" "cd $NAS_DIR && sudo /usr/local/bin/docker-compose -f docker-compose.nas.yml run --rm backend alembic upgrade head" || {
    echo "⚠️  =========================================="
    echo "⚠️  Migration failed!"
    echo "⚠️  =========================================="
    echo "ℹ️  Attempting to restart backend anyway to restore service..."
}

# 6. Start Backend
echo -e "🚀 Starting backend..."
ssh "juns@$NAS_HOST" "cd $NAS_DIR && sudo chmod -R 777 app .env requirements.txt pyproject.toml && sudo /usr/local/bin/docker-compose -f docker-compose.nas.yml up -d backend"
