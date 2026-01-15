#!/bin/bash

# PATH에 /usr/local/bin 추가 (cloudflared 경로)
export PATH="/usr/local/bin:$PATH"

# Focus Mate Backend - NAS 중지 스크립트 (Miniconda 환경)
# NAS에서 백엔드를 안전하게 중지하기 위한 스크립트

# 2025-12-30

set -e

# 프로젝트 디렉토리 (NAS 경로)
PROJECT_DIR="/volume1/web/focusmate-backend"
PID_FILE="$PROJECT_DIR/app.pid"

# PID 파일 확인
if [ ! -f "$PID_FILE" ]; then
    echo "⚠️  PID 파일이 없습니다. ($PID_FILE)"
    echo "   백엔드가 실행 중이지 않을 수 있습니다."

    # 포트 8000을 사용하는 프로세스 확인
    PORT_PID=$(lsof -ti:8000 2>/dev/null || echo "")
    if [ -n "$PORT_PID" ]; then
        echo "   하지만 포트 8000을 사용하는 프로세스가 있습니다. (PID: $PORT_PID)"
        read -p "   이 프로세스를 중지하시겠습니까? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill "$PORT_PID" 2>/dev/null || true
            sleep 1
            if ps -p "$PORT_PID" > /dev/null 2>&1; then
                echo "   강제 종료 중..."
                kill -9 "$PORT_PID" 2>/dev/null || true
            fi
            echo "✅ 프로세스가 중지되었습니다."
        fi
    else
        echo "   포트 8000을 사용하는 프로세스도 없습니다."
    fi
    exit 0
fi

# PID 읽기
PID=$(cat "$PID_FILE")

# 프로세스 확인
if ! ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️  프로세스가 실행 중이지 않습니다. (PID: $PID)"
    echo "   PID 파일을 삭제합니다."
    rm -f "$PID_FILE"
    exit 0
fi

# 프로세스 정보 확인
PROCESS_INFO=$(ps -p "$PID" -o comm=,args= 2>/dev/null || echo "")
if [ -z "$PROCESS_INFO" ]; then
    echo "⚠️  프로세스 정보를 가져올 수 없습니다."
    rm -f "$PID_FILE"
    exit 0
fi

echo "🛑 Focus Mate Backend 중지 중..."
echo "   PID: $PID"
echo "   프로세스: $PROCESS_INFO"
echo ""

# 프로세스 그룹 ID 가져오기 (uvicorn은 여러 워커 프로세스를 생성할 수 있음)
PGID=$(ps -p "$PID" -o pgid= 2>/dev/null | tr -d ' ' || echo "")

# 정상 종료 시도 (SIGTERM)
echo "   정상 종료 신호 전송 중..."

# 프로세스 그룹 전체에 종료 신호 전송 (모든 워커 프로세스 포함)
if [ -n "$PGID" ] && [ "$PGID" != "0" ]; then
    # 프로세스 그룹 전체 종료 (더 확실함)
    kill -TERM -"$PGID" 2>/dev/null || kill "$PID" 2>/dev/null || true
else
    # 프로세스 그룹을 찾을 수 없으면 메인 PID만 종료
    kill "$PID" 2>/dev/null || true
fi

# uvicorn의 모든 워커 프로세스도 찾아서 종료
UVICORN_PIDS=$(ps aux | grep '[u]vicorn.*app.main:app' | awk '{print $2}' || echo "")
if [ -n "$UVICORN_PIDS" ]; then
    for UVICORN_PID in $UVICORN_PIDS; do
        if [ "$UVICORN_PID" != "$PID" ]; then
            kill "$UVICORN_PID" 2>/dev/null || true
        fi
    done
fi

# 프로세스가 종료될 때까지 대기 (최대 10초)
TIMEOUT=10
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    # 메인 프로세스와 모든 uvicorn 프로세스가 종료되었는지 확인
    if ! ps -p "$PID" > /dev/null 2>&1 && [ -z "$(ps aux | grep '[u]vicorn.*app.main:app' | awk '{print $2}')" ]; then
        echo "✅ 백엔드가 정상적으로 중지되었습니다."
        rm -f "$PID_FILE"
        exit 0
    fi
    sleep 1
    ELAPSED=$((ELAPSED + 1))
    echo -n "."
done
echo ""

# 정상 종료 실패 시 강제 종료
REMAINING_PIDS=$(ps aux | grep '[u]vicorn.*app.main:app' | awk '{print $2}' || echo "")
if [ -n "$REMAINING_PIDS" ] || ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️  정상 종료 실패. 강제 종료 중..."

    # 프로세스 그룹 전체 강제 종료
    if [ -n "$PGID" ] && [ "$PGID" != "0" ]; then
        kill -9 -"$PGID" 2>/dev/null || true
    fi

    # 남은 모든 uvicorn 프로세스 강제 종료
    for REMAINING_PID in $REMAINING_PIDS; do
        kill -9 "$REMAINING_PID" 2>/dev/null || true
    done

    # 메인 PID도 강제 종료
    kill -9 "$PID" 2>/dev/null || true

    sleep 1

    # 최종 확인
    FINAL_REMAINING=$(ps aux | grep '[u]vicorn.*app.main:app' | awk '{print $2}' || echo "")
    if [ -n "$FINAL_REMAINING" ] || ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ 일부 프로세스 종료 실패"
        echo "   남은 프로세스: $FINAL_REMAINING $PID"
        echo "   수동으로 종료하세요: kill -9 $FINAL_REMAINING $PID"
        exit 1
    else
        echo "✅ 백엔드가 강제 종료되었습니다."
    fi
fi

# PID 파일 삭제
rm -f "$PID_FILE"
echo ""

# GitHub Webhook Listener 중지
WEBHOOK_PID_FILE="$PROJECT_DIR/webhook-listener.pid"
if [ -f "$WEBHOOK_PID_FILE" ]; then
    WEBHOOK_PID=$(cat "$WEBHOOK_PID_FILE" 2>/dev/null || echo "")
    if [ -n "$WEBHOOK_PID" ] && ps -p "$WEBHOOK_PID" > /dev/null 2>&1; then
        echo "🛑 GitHub Webhook Listener (PID: $WEBHOOK_PID) 중지 중..."
        kill "$WEBHOOK_PID" 2>/dev/null || true
        sleep 1
        if ps -p "$WEBHOOK_PID" > /dev/null 2>&1; then
            kill -9 "$WEBHOOK_PID" 2>/dev/null || true
        fi
        rm -f "$WEBHOOK_PID_FILE"
        echo "✅ GitHub Webhook Listener가 중지되었습니다."
    else
        rm -f "$WEBHOOK_PID_FILE"
    fi
fi

# Log Alerter 중지
LOG_ALERTER_PID_FILE="$PROJECT_DIR/log-alerter.pid"
if [ -f "$LOG_ALERTER_PID_FILE" ]; then
    ALERTER_PID=$(cat "$LOG_ALERTER_PID_FILE" 2>/dev/null || echo "")
    if [ -n "$ALERTER_PID" ] && ps -p "$ALERTER_PID" > /dev/null 2>&1; then
        echo "🛑 Log Alerter (PID: $ALERTER_PID) 중지 중..."
        kill "$ALERTER_PID" 2>/dev/null || true
        sleep 1
        if ps -p "$ALERTER_PID" > /dev/null 2>&1; then
            kill -9 "$ALERTER_PID" 2>/dev/null || true
        fi
        rm -f "$LOG_ALERTER_PID_FILE"
        echo "✅ Log Alerter가 중지되었습니다."
    else
        rm -f "$LOG_ALERTER_PID_FILE"
    fi
fi

# Cloudflare Tunnel 중지
TUNNEL_DIR="/volume1/web/cloudflare-tunnel"
TUNNEL_PID_FILE="$TUNNEL_DIR/tunnel.pid"

if [ -f "$TUNNEL_PID_FILE" ]; then
    TUNNEL_PID=$(cat "$TUNNEL_PID_FILE" 2>/dev/null || echo "")
    if [ -n "$TUNNEL_PID" ] && ps -p "$TUNNEL_PID" > /dev/null 2>&1; then
        echo "🛑 Cloudflare Tunnel (PID: $TUNNEL_PID) 중지 중..."
        kill "$TUNNEL_PID" 2>/dev/null || true
        sleep 2
        if ps -p "$TUNNEL_PID" > /dev/null 2>&1; then
            kill -9 "$TUNNEL_PID" 2>/dev/null || true
        fi
        rm -f "$TUNNEL_PID_FILE"
        echo "✅ Cloudflare Tunnel이 중지되었습니다."
    else
        rm -f "$TUNNEL_PID_FILE"
    fi
fi

# Architect Agent 중지
AGENT_PID_FILE="$PROJECT_DIR/architect_agent.pid"
if [ -f "$AGENT_PID_FILE" ]; then
    AGENT_PID=$(cat "$AGENT_PID_FILE" 2>/dev/null || echo "")
    if [ -n "$AGENT_PID" ] && ps -p "$AGENT_PID" > /dev/null 2>&1; then
        echo "🛑 Architect Agent (PID: $AGENT_PID) 중지 중..."
        # 프로세스 그룹 전체 종료 시도 (codex exec 포함)
        AGENT_PGID=$(ps -p "$AGENT_PID" -o pgid= 2>/dev/null | tr -d ' ' || echo "")
        if [ -n "$AGENT_PGID" ] && [ "$AGENT_PGID" != "0" ]; then
            kill -TERM -"$AGENT_PGID" 2>/dev/null || kill "$AGENT_PID" 2>/dev/null || true
        else
            kill "$AGENT_PID" 2>/dev/null || true
        fi
        sleep 1
        if ps -p "$AGENT_PID" > /dev/null 2>&1; then
            kill -9 "$AGENT_PID" 2>/dev/null || true
        fi
        rm -f "$AGENT_PID_FILE"
        echo "✅ Architect Agent가 중지되었습니다."
    else
        rm -f "$AGENT_PID_FILE"
    fi
fi
