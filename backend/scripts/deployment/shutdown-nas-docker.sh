#!/bin/bash
# NAS Shutdown Script for FocusMate Docker
#
# Usage: Add to Synology Task Scheduler
# - Type: Triggered Task -> User-defined script
# - Event: Shutdown
# - User: root (recommended for docker)
#
# Note: Run this BEFORE the system force-kills processes to ensure data integrity.

#--- CONFIG ---
TARGET_DIR="/volume1/web/focusmate-backend"
DOCKER_COMPOSE_CMD="docker-compose"
LOG_FILE="/volume1/homes/juns/focusmate_shutdown.log"
#--------------

echo "=======================================================" >> "$LOG_FILE"
echo "[$(date)] NAS Shutdown: Stopping FocusMate Docker..." >> "$LOG_FILE"

if [ -d "$TARGET_DIR" ]; then
    cd "$TARGET_DIR" || exit 1
else
    echo "[$(date)] ERROR: Directory $TARGET_DIR not found!" >> "$LOG_FILE"
    exit 1
fi

# Stop containers gracefully
# 'stop' preserves containers. 'down' removes them.
# 'stop' is safer for 'restart: unless-stopped' policies and preserving logs.
output=$($DOCKER_COMPOSE_CMD stop 2>&1)
exit_code=$?

echo "$output" >> "$LOG_FILE"

if [ $exit_code -eq 0 ]; then
    echo "[$(date)] SUCCESS: Docker services stopped." >> "$LOG_FILE"
else
    echo "[$(date)] WARNING: Failed to stop cleanly (Exit code: $exit_code)" >> "$LOG_FILE"
fi

echo "=======================================================" >> "$LOG_FILE"
exit $exit_code
