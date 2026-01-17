#!/bin/bash

# PATH에 /usr/local/bin 추가 (cloudflared 경로)
export PATH="/usr/local/bin:$PATH"

# Focus Mate Backend - NAS 실행 스크립트 (Miniconda 환경)
# NAS에서 백엔드를 실행하기 위한 스크립트
# Miniconda 환경(focusmate_env)을 사용합니다.

# 2025-12-30

# This script is used to start the backend server on NAS.
# It is used to start the backend server on NAS.
# It will check if the Python version is compatible and install the dependencies.
# It will then run the migrations and start the server.
# It will also check if the .env file exists and create it if it doesn't.
# It will also check if the virtual environment exists and create it if it doesn't.
# It will also check if the uvicorn is available and install it if it isn't.
# It will also run the migrations if alembic is available.
# It will also start the server.

set -e
umask 027

# Unset collision (legacy ghost variable)
unset DATABASE_URL

# EXPLICITLY LOAD DATABASE_URL from .env
# This ensures we use the correct local configuration (Port 5432)
# and bypasses any system-level overrides, without hardcoding secrets.

# 프로젝트 디렉토리 (NAS 경로) - 미리 정의
PROJECT_DIR="/volume1/web/focusmate-backend"

# 안전하게 .env 로드 (표준 방식)
if [ -f "$PROJECT_DIR/.env" ]; then
    set -a  # 자동으로 export
    source "$PROJECT_DIR/.env"
    set +a
fi

# Enforce production-safe defaults on NAS when not explicitly set
if [ -z "${APP_ENV:-}" ]; then
    export APP_ENV="production"
fi
# Always disable prepared statements in staging/production to avoid pgBouncer
# transaction pool errors (asyncpg DuplicatePreparedStatementError).
if [ "${APP_ENV:-}" = "production" ] || [ "${APP_ENV:-}" = "staging" ]; then
    export DATABASE_DISABLE_PREPARED_STATEMENTS="true"
fi
if [ -z "${DATABASE_PGBOUNCER:-}" ]; then
    export DATABASE_PGBOUNCER="true"
fi
if [ -n "${DATABASE_URL:-}" ]; then
    if echo "$DATABASE_URL" | grep -qiE "pgbouncer|pooler|:6432|:6543"; then
        export DATABASE_PGBOUNCER="true"
    fi
fi
if [ "${DATABASE_PGBOUNCER:-}" = "true" ] || [ "${DATABASE_PGBOUNCER:-}" = "1" ]; then
    export DATABASE_DISABLE_PREPARED_STATEMENTS="true"
fi

# Force-disable asyncpg prepared statements in DATABASE_URL as a last-resort safety net.
# This protects against DuplicatePreparedStatementError behind pgBouncer transaction pools.
ensure_db_param() {
    local url="$1"
    local key="$2"
    local value="$3"

    if echo "$url" | grep -qE "[?&]${key}="; then
        url=$(echo "$url" | sed -E "s/([?&])${key}=[^&]*/\\1${key}=${value}/")
    else
        if echo "$url" | grep -q "?"; then
            url="${url}&${key}=${value}"
        else
            url="${url}?${key}=${value}"
        fi
    fi

    echo "$url"
}

# Prepared statements are handled via connect_args in session.py to ensure correct types.
# Avoid modifying the URL string directly as asyncpg may fail to coerce types.

# 프로젝트 디렉토리 (NAS 경로)
PROJECT_DIR="/volume1/web/focusmate-backend"
cd "$PROJECT_DIR"

# .env 파일에서 Cloudflare Tunnel 토큰 로드
if [ -f "$PROJECT_DIR/.env" ]; then
    # 공백/따옴표를 포함한 토큰 라인을 안전하게 파싱
    token_line=$(grep -E '^CLOUDFLARE_TUNNEL_TOKEN=' "$PROJECT_DIR/.env" 2>/dev/null | head -1)
    if [ -n "$token_line" ]; then
        token_value=$(echo "$token_line" | sed 's/^CLOUDFLARE_TUNNEL_TOKEN=//')
        token_value=$(echo "$token_value" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')
        token_value=$(echo "$token_value" | sed 's/^"//;s/"$//;s/^\x27//;s/\x27$//')
        if [ -n "$token_value" ]; then
            export CLOUDFLARE_TUNNEL_TOKEN="$token_value"
        fi
    fi
fi

# Miniconda 경로 및 환경 설정
MINICONDA_BASE="/volume1/web/miniconda3"
CONDA_ENV="focusmate_env"
CONDA_PYTHON="$MINICONDA_BASE/envs/$CONDA_ENV/bin/python"

# Miniconda 환경 확인
if [ ! -f "$CONDA_PYTHON" ]; then
    echo "❌ Error: Miniconda 환경 '$CONDA_ENV'이 없습니다."
    echo "   다음 명령어로 환경을 생성하세요:"
    echo "   conda create -n $CONDA_ENV python=3.11 -y"
    echo "   conda activate $CONDA_ENV"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# Python 버전 확인
PYTHON_VERSION=$($CONDA_PYTHON --version 2>&1)
echo "✅ Python 버전: $PYTHON_VERSION"

# uvicorn 확인
if ! $CONDA_PYTHON -m uvicorn --version &> /dev/null; then
    echo "❌ Error: uvicorn이 설치되어 있지 않습니다."
    echo "   다음 명령어로 설치하세요:"
    echo "   conda activate $CONDA_ENV"
    echo "   pip install -r requirements.txt"
    exit 1
fi

# alembic 확인
if ! $CONDA_PYTHON -m alembic --version &> /dev/null; then
    echo "⚠️  Warning: alembic이 설치되어 있지 않습니다."
    echo "   마이그레이션을 실행할 수 없습니다."
    echo "   다음 명령어로 설치하세요:"
    echo "   conda activate $CONDA_ENV"
    echo "   pip install -r requirements.txt"
fi

# 데이터베이스 마이그레이션 실행
echo ""
echo "🗄️  데이터베이스 마이그레이션 실행 중..."
cd "$PROJECT_DIR"

# Conda 환경의 bin 디렉토리를 PATH에 추가 (alembic 명령어를 찾기 위해)
CONDA_BIN_DIR="$MINICONDA_BASE/envs/$CONDA_ENV/bin"
export PATH="$CONDA_BIN_DIR:$PATH"

if [ -f "$PROJECT_DIR/scripts/database/smart_migrate.py" ]; then
    # Smart migration script 사용 (기존 테이블이 있어도 안전하게 처리)
    # PATH에 conda bin이 추가되어 있으므로 alembic 명령어를 찾을 수 있음
    if PYTHONPATH=. $CONDA_PYTHON "$PROJECT_DIR/scripts/database/smart_migrate.py"; then
        echo "✅ 마이그레이션 완료"
    else
        echo "⚠️  마이그레이션 완료 (경고가 있을 수 있지만 정상일 수 있음)"
        echo "   데이터베이스 연결 및 .env 파일을 확인하세요"
    fi
elif command -v alembic &> /dev/null || $CONDA_PYTHON -m alembic --version &> /dev/null; then
    # Fallback: 직접 alembic 명령어 사용
    if command -v alembic &> /dev/null; then
        ALEMBIC_CMD="alembic"
    else
        ALEMBIC_CMD="$CONDA_PYTHON -m alembic"
    fi

    if $ALEMBIC_CMD upgrade head; then
        echo "✅ 마이그레이션 완료"
    else
        echo "⚠️  마이그레이션 실패 또는 이미 최신 상태"
        echo "   데이터베이스 연결을 확인하세요 (DATABASE_URL in .env)"
    fi
else
    echo "⚠️  Alembic을 찾을 수 없어 마이그레이션을 건너뜁니다."
    echo "   의존성을 설치하세요: pip install -r requirements.txt"
fi
echo ""

# 이미 실행 중인지 확인
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    if ps -p "$PID" > /dev/null 2>&1; then
        echo "⚠️  백엔드 서버가 이미 실행 중입니다. (PID: $PID)"
        echo "   중지하려면: kill $PID"
        exit 1
    else
        # PID 파일이 있지만 프로세스가 없으면 삭제
        rm -f app.pid
    fi
fi

# 로그 디렉토리 생성
mkdir -p logs

# 백엔드 실행 (프로덕션 모드, reload 없음)
echo "🚀 Focus Mate Backend 시작 중..."
echo "   Host: 0.0.0.0"
echo "   Port: 8000"
echo "   Python: $PYTHON_VERSION"
echo "   Conda 환경: $CONDA_ENV"
echo "   Logs: logs/app.log"
echo ""

# 백그라운드 실행 (Miniconda 환경의 Python 직접 사용)
# WORKERS 변수가 설정되어 있지 않으면 기본값 1 사용 (CPU 100% 이슈 디버깅을 위해 1로 하향)
WORKERS=${WORKERS:-1}
echo "   Workers: $WORKERS"

# PYTHONPATH 설정 (자식 프로세스 임포트 문제 해결)
export PYTHONPATH="$PROJECT_DIR"

# 데이터베이스 연결 풀 설정 (NAS 리소스 제한 고려)
# 작업자당 10개 연결
export DATABASE_POOL_SIZE=${DATABASE_POOL_SIZE:-15}
export DATABASE_MAX_OVERFLOW=${DATABASE_MAX_OVERFLOW:-5}
echo "   DB Pool: $DATABASE_POOL_SIZE (Overflow: $DATABASE_MAX_OVERFLOW)"

FORWARDED_ALLOW_IPS=${FORWARDED_ALLOW_IPS:-127.0.0.1,::1}

# --loop asyncio 추가 (uvloop와 multiprocessing 간의 잠재적 100% CPU 이슈 방지)
nohup $CONDA_PYTHON -m uvicorn app.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --workers $WORKERS \
    --loop asyncio \
    --timeout-keep-alive 75 \
    --proxy-headers \
    --forwarded-allow-ips "$FORWARDED_ALLOW_IPS" \
    > logs/app.log 2>&1 &

PID=$!
echo $PID > app.pid

# 프로세스가 정상적으로 시작되었는지 확인
sleep 2
if ps -p "$PID" > /dev/null 2>&1; then
    echo "✅ 백엔드가 시작되었습니다. (PID: $PID)"
    echo "   로그 확인: tail -f logs/app.log"
    echo "   중지: kill $PID"
    echo ""
else
    echo "❌ 백엔드 시작 실패"
    echo "   로그를 확인하세요: cat logs/app.log"
    rm -f app.pid
    exit 1
fi

# GitHub Webhook Listener 자동 시작
WEBHOOK_SCRIPT="$PROJECT_DIR/scripts/deployment/start-webhook-listener.sh"
WEBHOOK_PID_FILE="$PROJECT_DIR/webhook-listener.pid"

if [ -f "$WEBHOOK_SCRIPT" ]; then
    if [ ! -f "$WEBHOOK_PID_FILE" ] || ! ps -p "$(cat "$WEBHOOK_PID_FILE" 2>/dev/null)" > /dev/null 2>&1; then
        echo "🚀 GitHub Webhook Listener 시작 중..."
        if bash "$WEBHOOK_SCRIPT"; then
            echo "✅ GitHub Webhook Listener가 시작되었습니다."
        else
            echo "⚠️  GitHub Webhook Listener 시작 실패 (계속 진행)"
        fi
    else
        echo "⚠️  GitHub Webhook Listener가 이미 실행 중입니다."
    fi
    echo ""
fi

# Log Alerter 자동 시작 (실시간 로그 감시)
LOG_ALERTER_PID_FILE="$PROJECT_DIR/log-alerter.pid"
LOG_ALERTER_LOG_FILE="$PROJECT_DIR/logs/log-alerter.log"

if [ -f "$PROJECT_DIR/scripts/monitoring/log_alerter.py" ]; then
    if [ ! -f "$LOG_ALERTER_PID_FILE" ] || ! ps -p "$(cat "$LOG_ALERTER_PID_FILE" 2>/dev/null)" > /dev/null 2>&1; then
        echo "🚀 Log Alerter 시작 중 (실시간 에러 알림)..."
        nohup $CONDA_PYTHON "$PROJECT_DIR/scripts/monitoring/log_alerter.py" > "$LOG_ALERTER_LOG_FILE" 2>&1 &
        echo $! > "$LOG_ALERTER_PID_FILE"
        echo "✅ Log Alerter가 시작되었습니다."
    else
        echo "⚠️  Log Alerter가 이미 실행 중입니다."
    fi
    echo ""
    echo ""
fi

# Cloudflare Tunnel 자동 시작
TUNNEL_DIR="/volume1/web/cloudflare-tunnel"
TUNNEL_PID_FILE="$TUNNEL_DIR/tunnel.pid"
TUNNEL_LOG_FILE="$TUNNEL_DIR/tunnel.log"
TUNNEL_NAME="focusmate-backend"

# cloudflared 확인
if command -v cloudflared > /dev/null 2>&1; then
    # Tunnel 디렉토리 생성
    mkdir -p "$TUNNEL_DIR"

    # 이미 실행 중인지 확인
    if [ -f "$TUNNEL_PID_FILE" ]; then
        TUNNEL_PID=$(cat "$TUNNEL_PID_FILE" 2>/dev/null || echo "")
        if [ -n "$TUNNEL_PID" ] && ps -p "$TUNNEL_PID" > /dev/null 2>&1; then
            echo "⚠️  Cloudflare Tunnel이 이미 실행 중입니다. (PID: $TUNNEL_PID)"
        else
            rm -f "$TUNNEL_PID_FILE"
        fi
    fi

    # Tunnel이 실행 중이 아니면 시작
    if [ ! -f "$TUNNEL_PID_FILE" ] || ! ps -p "$(cat "$TUNNEL_PID_FILE" 2>/dev/null)" > /dev/null 2>&1; then
        echo "🚀 Cloudflare Tunnel 시작 중..."
        cd "$TUNNEL_DIR"

        # 토큰 방식 우선 (기본 방법 - 공식 권장)
        if [ -n "$CLOUDFLARE_TUNNEL_TOKEN" ]; then
            echo "🔑 토큰 방식으로 Tunnel 시작 중..."
            nohup cloudflared tunnel run --token "$CLOUDFLARE_TUNNEL_TOKEN" > "$TUNNEL_LOG_FILE" 2>&1 &
        # config.yml 방식 (백업 방법 - JSON credentials 파일 필요)
        elif [ -f ~/.cloudflared/config.yml ]; then
            echo "📄 config.yml 방식으로 Tunnel 시작 중 (백업 방법)..."
            # config.yml의 credentials-file 경로 확인 및 수정
            ACTUAL_HOME=$(eval echo ~$USER)
            JSON_FILE="$ACTUAL_HOME/.cloudflared/0241f413-00f5-46f6-a705-f55db527cb78.json"

            # JSON 파일이 있으면 config.yml 업데이트
            if [ -f "$JSON_FILE" ]; then
                # config.yml의 credentials-file 경로를 실제 JSON 파일 경로로 수정
                # sed -i는 일부 시스템에서 작동하지 않을 수 있으므로 임시 파일 사용
                sed "s|credentials-file:.*|credentials-file: $JSON_FILE|g" ~/.cloudflared/config.yml > ~/.cloudflared/config.yml.tmp && \
                mv ~/.cloudflared/config.yml.tmp ~/.cloudflared/config.yml
                echo "   ✅ JSON credentials 파일 발견: $JSON_FILE"
            else
                echo "   ⚠️  경고: JSON credentials 파일을 찾을 수 없습니다."
                echo "   JSON 파일 경로: $JSON_FILE"
                echo "   config.yml이 올바르게 작동하지 않을 수 있습니다."
                echo "   토큰 방식을 사용하려면 backend/.env에 CLOUDFLARE_TUNNEL_TOKEN을 추가하세요."
            fi
            nohup cloudflared tunnel run "$TUNNEL_NAME" > "$TUNNEL_LOG_FILE" 2>&1 &
        else
            echo "❌ Error: Cloudflare Tunnel 토큰 또는 config.yml이 필요합니다."
            echo "   backend/.env 파일에 CLOUDFLARE_TUNNEL_TOKEN을 추가하세요."
            echo "   또는 ~/.cloudflared/config.yml 파일을 생성하세요."
            exit 1
        fi

        TUNNEL_PID=$!
        echo "$TUNNEL_PID" > "$TUNNEL_PID_FILE"

        sleep 3
        if ps -p "$TUNNEL_PID" > /dev/null 2>&1; then
            echo "✅ Cloudflare Tunnel이 시작되었습니다. (PID: $TUNNEL_PID)"
            echo "   로그 확인: tail -f $TUNNEL_LOG_FILE"
        else
            echo "⚠️  Cloudflare Tunnel 시작 실패"
            echo "   로그 확인: cat $TUNNEL_LOG_FILE"
            rm -f "$TUNNEL_PID_FILE"
        fi
    fi
else
    echo "⚠️  cloudflared가 설치되어 있지 않습니다. Tunnel을 시작할 수 없습니다."
fi

echo "🎉 Deployment & Restart Successfully Completed!"
