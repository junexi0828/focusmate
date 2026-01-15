#!/bin/bash

set -euo pipefail

# Configuration
# Source .env if it exists in the parent directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

if [ -f "$BACKEND_DIR/.env" ]; then
    set -a
    # shellcheck disable=SC1090
    . "$BACKEND_DIR/.env"
    set +a
fi

WEBHOOK_URL=${SLACK_WEBHOOK_URL:-}
APP_NAME=${APP_NAME:-"FocusMate"}
ENV=${APP_ENV:-"production"}

if [ -z "$WEBHOOK_URL" ]; then
    echo "Error: SLACK_WEBHOOK_URL not set"
    exit 1
fi

send_slack() {
    local level=$1
    local title=$2
    local message=$3
    local color="#36a64f"

    [ "$level" == "warning" ] && color="#ecb22e"
    [ "$level" == "error" ] && color="#e01e5a"

    local payload=$(cat <<EOF
{
  "attachments": [
    {
      "color": "$color",
      "title": "[$ENV] $title",
      "text": "$message",
      "footer": "$APP_NAME Monitoring",
      "ts": $(date +%s)
    }
  ]
}
EOF
)
    curl -sS -X POST -H 'Content-type: application/json' --data "$payload" "$WEBHOOK_URL"
}

# 1. Check CPU Load (Alert if load > 2.0 for 1 min)
CPU_LOAD=$(uptime | awk -F'load average:' '{ print $2 }' | cut -d, -f1 | xargs)
if command -v bc >/dev/null 2>&1; then
    if (( $(echo "$CPU_LOAD > 2.0" | bc -l) )); then
        send_slack "warning" "CPU Load Alert" "Current load average: $CPU_LOAD is higher than normal."
    fi
else
    echo "Warning: bc not installed; skipping CPU load threshold check"
fi

# 2. Check Memory Usage (Alert if free < 100MB)
FREE_MEM=$(free -m | awk '/^Mem:/{print $4}')
if [ "$FREE_MEM" -lt 100 ]; then
    send_slack "warning" "Memory Alert" "Free memory is low: ${FREE_MEM}MB remaining."
fi

# 3. Check Disk Usage (Alert if /volume1 > 90%)
DISK_USAGE=$(df -h /volume1 | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -gt 90 ]; then
    send_slack "warning" "Disk Usage Alert" "Disk usage on /volume1 is at ${DISK_USAGE}%."
fi

# 4. Check if Backend is running (Watchdog)
PID_FILE="$BACKEND_DIR/app.pid"
backend_running=false

if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE" 2>/dev/null || echo "")
    if [ -n "$PID" ] && ps -p "$PID" > /dev/null 2>&1; then
        backend_running=true
    else
        rm -f "$PID_FILE"
    fi
else
    if pgrep -f "uvicorn app.main:app" > /dev/null; then
        backend_running=true
    fi
fi

if [ "$backend_running" != true ]; then
    send_slack "error" "Service Down" "FocusMate backend process is not running! Attempting to restart..."

    # Attempt to restart
    if [ -f "$BACKEND_DIR/start-nas.sh" ]; then
        cd "$BACKEND_DIR" && bash start-nas.sh >> "$BACKEND_DIR/logs/monitor.log" 2>&1

        sleep 5
        if [ -f "$PID_FILE" ] && ps -p "$(cat "$PID_FILE" 2>/dev/null)" > /dev/null 2>&1; then
            send_slack "info" "Watchdog Success" "FocusMate backend has been successfully restarted."
        else
            send_slack "critical" "Watchdog Failure" "Failed to restart FocusMate backend. Manual intervention required."
        fi
    else
        send_slack "error" "Watchdog Error" "start-nas.sh not found at $BACKEND_DIR"
    fi
fi
