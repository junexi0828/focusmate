#!/bin/bash

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

# 정상 종료 시도 (SIGTERM)
echo "   정상 종료 신호 전송 중..."
kill "$PID" 2>/dev/null || true

# 프로세스가 종료될 때까지 대기 (최대 10초)
TIMEOUT=10
ELAPSED=0
while [ $ELAPSED -lt $TIMEOUT ]; do
    if ! ps -p "$PID" > /dev/null 2>&1; then
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
if ps -p "$PID" > /dev/null 2>&1; then
    echo "⚠️  정상 종료 실패. 강제 종료 중..."
    kill -9 "$PID" 2>/dev/null || true
    sleep 1

    if ps -p "$PID" > /dev/null 2>&1; then
        echo "❌ 프로세스 종료 실패"
        echo "   수동으로 종료하세요: kill -9 $PID"
        exit 1
    else
        echo "✅ 백엔드가 강제 종료되었습니다."
    fi
fi

# PID 파일 삭제
rm -f "$PID_FILE"
echo ""

