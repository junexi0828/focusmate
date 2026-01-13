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

# Ensure we are in the 'backend' directory (where this script lives)
cd "$(dirname "$0")"

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
echo "🛑 Stopping Remote Service..."
ssh "$NAS_USER@$NAS_HOST" "cd $NAS_DIR && bash stop-nas.sh"

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
    --exclude '.env' \
    --exclude '._*' \
    --exclude '*.env' \
    --rsync-path="/usr/bin/rsync" \
    ./ "$NAS_USER@$NAS_HOST:$NAS_DIR/"

echo "✅ File sync complete."

# 1.5 Optional: Install dependencies on NAS (mirrors old webhook safety)
if [ "${INSTALL_DEPS:-1}" = "1" ]; then
    echo "📦 Installing dependencies on NAS (requirements.txt)..."
    ssh "$NAS_USER@$NAS_HOST" "cd $NAS_DIR && if [ -f requirements.txt ] && [ -x $REMOTE_PYTHON ]; then $REMOTE_PYTHON -m pip install -r requirements.txt --quiet; else echo 'ℹ️  requirements.txt or python missing, skipping deps'; fi"
fi

# 1.6 Optional: Run Database Migrations
if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
    echo "🗄️  Running Database Migrations..."
    ssh "$NAS_USER@$NAS_HOST" "cd $NAS_DIR && export PYTHONPATH=. && $REMOTE_PYTHON scripts/database/smart_migrate.py"
fi

# 2. Restart Service (Start only)
echo "🔄 Starting Remote Service..."
ssh "$NAS_USER@$NAS_HOST" "cd $NAS_DIR && bash start-nas.sh"

echo "🎉 Deployment & Restart Successfully Completed!"
