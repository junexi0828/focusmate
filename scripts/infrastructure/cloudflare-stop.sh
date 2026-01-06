#!/bin/bash

# Cloudflare Tunnel 중지 스크립트
# 사용법: ./scripts/stop-cloudflare-tunnel.sh
# 이 스크립트로 시작된 백엔드도 함께 종료할 수 있습니다.

PID_FILE="$HOME/.cloudflare-tunnel/tunnel.pid"
BACKEND_PID_FILE="$HOME/.cloudflare-tunnel/backend.pid"

# Tunnel 중지
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")

    if ps -p "$PID" > /dev/null 2>&1; then
        echo "🛑 Cloudflare Tunnel 중지 중... (PID: $PID)"
        kill "$PID"

        # 프로세스 종료 대기
        for i in {1..10}; do
            if ! ps -p "$PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done

        if ps -p "$PID" > /dev/null 2>&1; then
            echo "⚠️  강제 종료 중..."
            kill -9 "$PID"
        fi

        rm -f "$PID_FILE"
        echo "✅ Tunnel이 중지되었습니다."
    else
        echo "⚠️  Tunnel 프로세스를 찾을 수 없습니다. (PID: $PID)"
        rm -f "$PID_FILE"
    fi
else
    echo "⚠️  Tunnel이 실행되지 않았습니다."
fi

# 백엔드 중지 (이 스크립트로 시작된 경우)
if [ -f "$BACKEND_PID_FILE" ]; then
    BACKEND_PID=$(cat "$BACKEND_PID_FILE")

    if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
        echo ""
        echo "🛑 백엔드 서버 중지 중... (PID: $BACKEND_PID)"
        kill "$BACKEND_PID"

        # 프로세스 종료 대기
        for i in {1..10}; do
            if ! ps -p "$BACKEND_PID" > /dev/null 2>&1; then
                break
            fi
            sleep 1
        done

        if ps -p "$BACKEND_PID" > /dev/null 2>&1; then
            echo "⚠️  강제 종료 중..."
            kill -9 "$BACKEND_PID"
        fi

        rm -f "$BACKEND_PID_FILE"
        echo "✅ 백엔드가 중지되었습니다."
    else
        rm -f "$BACKEND_PID_FILE"
    fi
fi

