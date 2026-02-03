#!/bin/bash
# Webhook Listener Health Check & Auto-Restart Script
# 이 스크립트는 Synology Task Scheduler에서 5분마다 실행되어야 합니다.

PROJECT_DIR="/volume1/web/focusmate-backend"
PID_FILE="$PROJECT_DIR/webhook-listener.pid"
WEBHOOK_URL="http://localhost:9000/health"
START_SCRIPT="$PROJECT_DIR/scripts/deployment/start-webhook-listener.sh"
LOG_FILE="$PROJECT_DIR/logs/webhook-health-check.log"

# 로그 함수
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" >> "$LOG_FILE"
}

# PID 파일 확인
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")

    # 프로세스가 실행 중인지 확인
    if ps -p "$PID" > /dev/null 2>&1; then
        # Health check
        if curl -s --max-time 5 "$WEBHOOK_URL" > /dev/null 2>&1; then
            # 정상 작동 중
            exit 0
        else
            log "⚠️  Webhook listener is running but not responding to health checks (PID: $PID)"
            log "🔄 Killing unresponsive process and restarting..."
            kill -9 "$PID" 2>/dev/null
            rm -f "$PID_FILE"
        fi
    else
        log "⚠️  PID file exists but process is not running (stale PID: $PID)"
        rm -f "$PID_FILE"
    fi
fi

# Webhook listener가 실행 중이 아니면 시작
log "🚀 Starting webhook listener..."
bash "$START_SCRIPT" >> "$LOG_FILE" 2>&1

if [ $? -eq 0 ]; then
    log "✅ Webhook listener started successfully"
else
    log "❌ Failed to start webhook listener"
    exit 1
fi
