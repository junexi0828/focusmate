#!/bin/bash
# GitHub Webhook Listener 시작 스크립트 (NAS용)

# 프로젝트 디렉토리 (NAS 경로)
PROJECT_DIR="/volume1/web/focusmate-backend"
WEBHOOK_SCRIPT="$PROJECT_DIR/scripts/deployment/github-webhook-listener.py"
PID_FILE="$PROJECT_DIR/webhook-listener.pid"
LOG_FILE="$PROJECT_DIR/logs/webhook-listener.log"

# Miniconda 경로
MINICONDA_BASE="/volume1/web/miniconda3"
CONDA_ENV="focusmate_env"
CONDA_PYTHON="$MINICONDA_BASE/envs/$CONDA_ENV/bin/python"

# 로그 디렉토리 생성
mkdir -p "$PROJECT_DIR/logs"

# 이미 실행 중인지 확인
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Webhook listener가 이미 실행 중입니다. (PID: $PID)"
        exit 1
    else
        rm -f "$PID_FILE"
    fi
fi

# Webhook listener 시작
echo "🚀 GitHub Webhook Listener 시작 중..."
echo "   Script: $WEBHOOK_SCRIPT"
echo "   Log: $LOG_FILE"
echo ""

nohup "$CONDA_PYTHON" "$WEBHOOK_SCRIPT" > "$LOG_FILE" 2>&1 &

PID=$!
echo $PID > "$PID_FILE"

# 프로세스 확인
sleep 2
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ Webhook listener가 시작되었습니다. (PID: $PID)"
    echo "   로그 확인: tail -f $LOG_FILE"
    echo "   중지: kill $PID"
else
    echo "❌ Webhook listener 시작 실패"
    echo "   로그 확인: cat $LOG_FILE"
    rm -f "$PID_FILE"
    exit 1
fi

