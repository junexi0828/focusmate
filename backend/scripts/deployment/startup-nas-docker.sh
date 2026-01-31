#!/bin/bash
# NAS Startup Script for FocusMate Docker
#
# Usage: Add to Synology Task Scheduler
# - Type: Triggered Task -> User-defined script
# - Event: Boot-up
# - User: root (recommended for docker) or your user
#
# Note: Ensure paths match your NAS environment.

#--- CONFIG ---
# Path where docker-compose.yml resides on the NAS
# Adjust this to match your setup (check your .env or nas-setup-initial.sh default)
TARGET_DIR="/volume1/web/focusmate-backend"

# Docker Compose Command (Synology often puts it in /usr/local/bin or /usr/bin)
# You can use 'docker-compose' or 'docker compose' depending on version
DOCKER_COMPOSE_CMD="docker-compose"

# Logging
LOG_FILE="/volume1/homes/juns/focusmate_startup.log"
#--------------

echo "=======================================================" >> "$LOG_FILE"
echo "[$(date)] NAS Boot-up: Starting FocusMate Docker..." >> "$LOG_FILE"

# Check directory
if [ -d "$TARGET_DIR" ]; then
    cd "$TARGET_DIR" || exit 1
    echo "[$(date)] Changed directory to $TARGET_DIR" >> "$LOG_FILE"
else
    echo "[$(date)] ERROR: Directory $TARGET_DIR not found!" >> "$LOG_FILE"
    exit 1
fi

# Run Docker Compose
# -d: Detached mode
# --remove-orphans: Clean up old containers
output=$($DOCKER_COMPOSE_CMD up -d --remove-orphans 2>&1)
exit_code=$?

echo "$output" >> "$LOG_FILE"

if [ $exit_code -eq 0 ]; then
    echo "[$(date)] SUCCESS: Docker services started." >> "$LOG_FILE"

    # Start Webhook Listener
    echo "[$(date)] Webhook: Starting listener..." >> "$LOG_FILE"
    bash scripts/deployment/start-webhook-listener.sh >> "$LOG_FILE" 2>&1
else
    echo "[$(date)] FAILED: Docker services failed to start (Exit code: $exit_code)" >> "$LOG_FILE"
fi

echo "=======================================================" >> "$LOG_FILE"
exit $exit_code
