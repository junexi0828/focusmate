#!/bin/bash

# Cloudflare Tunnel 실행 스크립트
# 사용법: ./scripts/start-cloudflare-tunnel.sh
# 백엔드가 실행 중이 아니면 자동으로 시작합니다.

set -e

# 프로젝트 루트 경로
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Tunnel 토큰 (Zero Trust 대시보드에서 생성)
TUNNEL_TOKEN="eyJhIjoiZWQyNzU0OGI3ZjNlNTUxY2Y0ZjliM2M4YmFmMzk0MmUiLCJ0IjoiMDI0MWY0MTMtMDBmNS00NmY2LWE3MDUtZjU1ZGI1MjdjYjc4IiwicyI6IlltTTFaVFEwWm1VdFlXSmpZUzAwTldJeExUaG1ZMlF0TnpCbVptWTRNVFJrTkRRNSJ9"

LOG_DIR="$HOME/.cloudflare-tunnel"
LOG_FILE="$LOG_DIR/tunnel.log"
PID_FILE="$LOG_DIR/tunnel.pid"
BACKEND_PID_FILE="$LOG_DIR/backend.pid"

# 로그 디렉토리 생성
mkdir -p "$LOG_DIR"

# 이미 실행 중인지 확인
if [ -f "$PID_FILE" ]; then
    PID=$(cat "$PID_FILE")
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  Tunnel이 이미 실행 중입니다. (PID: $PID)"
        echo "   중지하려면: ./scripts/stop-cloudflare-tunnel.sh"
        exit 1
    else
        # PID 파일이 있지만 프로세스가 없으면 삭제
        rm -f "$PID_FILE"
    fi
fi

# cloudflared 확인
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared가 설치되어 있지 않습니다."
    echo "   설치: brew install cloudflare/cloudflare/cloudflared"
    exit 1
fi

# 백엔드 서버 확인 및 자동 시작
BACKEND_STARTED=false
if ! curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "⚠️  백엔드 서버가 실행되지 않았습니다."
    echo "   백엔드를 자동으로 시작합니다..."
    echo ""

    cd "$PROJECT_ROOT/backend"

    # 가상환경 확인 및 생성
    if [ ! -d "venv" ]; then
        echo "📦 가상환경이 없습니다. 생성 중..."
        python3 -m venv venv
    fi

    # 가상환경 활성화
    source venv/bin/activate

    # 의존성 확인
    if [ ! -f "venv/bin/uvicorn" ]; then
        echo "📥 의존성 설치 중..."
        pip install -q -r requirements.txt
    fi

    # 포트 확인 및 정리
    BACKEND_PORT=8000
    PIDS_TO_KILL=$(lsof -ti:$BACKEND_PORT 2>/dev/null || true)
    if [ -n "$PIDS_TO_KILL" ]; then
        echo "🔧 포트 $BACKEND_PORT 정리 중..."
        echo "$PIDS_TO_KILL" | xargs kill -9 2>/dev/null || true
        sleep 1
    fi

    # 백엔드 시작
    echo "🚀 백엔드 서버 시작 중..."
    nohup venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port $BACKEND_PORT > /tmp/focusmate-backend.log 2>&1 &
    BACKEND_PID=$!
    echo "$BACKEND_PID" > "$BACKEND_PID_FILE"

    sleep 2

    # 백엔드 프로세스 확인
    if ! kill -0 $BACKEND_PID 2>/dev/null; then
        echo "❌ 백엔드 시작 실패"
        tail -20 /tmp/focusmate-backend.log
        exit 1
    fi

    echo "✅ 백엔드 시작됨 (PID: $BACKEND_PID)"
    echo "   로그: tail -f /tmp/focusmate-backend.log"
    echo ""

    # 백엔드 준비 대기
    echo "⏳ 백엔드가 준비될 때까지 대기 중..."
    BACKEND_READY=false
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ 백엔드가 준비되었습니다!"
            BACKEND_READY=true
            break
        fi
        if ! kill -0 $BACKEND_PID 2>/dev/null; then
            echo "❌ 백엔드 프로세스가 종료되었습니다."
            tail -20 /tmp/focusmate-backend.log
            exit 1
        fi
        sleep 1
    done

    if [ "$BACKEND_READY" = false ]; then
        echo "⚠️  경고: 백엔드가 30초 내에 준비되지 않았습니다."
        tail -20 /tmp/focusmate-backend.log
        echo ""
        echo "계속 진행하시겠습니까? (y/n)"
        read -t 5 -r RESPONSE || RESPONSE="n"
        if [[ ! $RESPONSE =~ ^[Yy]$ ]]; then
            kill $BACKEND_PID 2>/dev/null || true
            rm -f "$BACKEND_PID_FILE"
            exit 1
        fi
    fi

    BACKEND_STARTED=true
    echo ""
else
    echo "✅ 백엔드 서버가 이미 실행 중입니다."
    echo ""
fi

echo "🚀 Cloudflare Tunnel 시작 중..."
echo "   백엔드 URL: http://localhost:8000"
echo "   로그 파일: $LOG_FILE"
echo ""

# Tunnel 실행 (토큰 기반, 백그라운드)
nohup cloudflared tunnel run --token "$TUNNEL_TOKEN" > "$LOG_FILE" 2>&1 &
TUNNEL_PID=$!

# PID 저장
echo "$TUNNEL_PID" > "$PID_FILE"

# 잠시 대기 후 상태 확인
sleep 2

if ps -p "$TUNNEL_PID" > /dev/null 2>&1; then
    echo "✅ Tunnel이 시작되었습니다. (PID: $TUNNEL_PID)"
    echo ""
    if [ "$BACKEND_STARTED" = true ]; then
        echo "📋 실행 중인 서비스:"
        echo "   백엔드: http://localhost:8000 (PID: $BACKEND_PID)"
        echo "   Tunnel: (PID: $TUNNEL_PID)"
        echo ""
    fi
    echo "📋 관리 명령어:"
    echo "   Tunnel 로그: tail -f $LOG_FILE"
    if [ "$BACKEND_STARTED" = true ]; then
        echo "   백엔드 로그: tail -f /tmp/focusmate-backend.log"
    fi
    echo "   Tunnel 중지: ./scripts/stop-cloudflare-tunnel.sh"
    echo "   상태 확인: ps aux | grep cloudflared"
    echo ""
    echo "📝 Zero Trust 대시보드에서 Public Hostname을 설정했는지 확인하세요:"
    echo "   https://one.dash.cloudflare.com/ → Networks → Tunnels → focusmate-backend → Public Hostname"
    echo ""
else
    echo "❌ Tunnel 시작 실패"
    echo "   로그 확인: cat $LOG_FILE"
    rm -f "$PID_FILE"
    if [ "$BACKEND_STARTED" = true ]; then
        echo ""
        echo "⚠️  백엔드는 계속 실행 중입니다. (PID: $BACKEND_PID)"
        echo "   중지하려면: kill $BACKEND_PID"
    fi
    exit 1
fi

