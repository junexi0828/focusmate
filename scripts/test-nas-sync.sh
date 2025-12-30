#!/bin/bash

# NAS 동기화 테스트 스크립트
# Git hook이 제대로 작동하는지 테스트합니다.

set -e

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# 백엔드 .env 파일에서 NAS 설정 로드
ENV_FILE="$PROJECT_ROOT/backend/.env"
if [ -f "$ENV_FILE" ]; then
    # .env 파일에서 NAS 관련 변수만 추출하여 export
    # 주석과 빈 줄을 제외하고 NAS_로 시작하는 변수만 로드
    while IFS='=' read -r key value; do
        # 주석 제거 및 공백 제거
        key=$(echo "$key" | sed 's/#.*$//' | xargs)
        value=$(echo "$value" | sed 's/#.*$//' | xargs)
        # 빈 줄이나 주석만 있는 줄 건너뛰기
        if [ -n "$key" ] && [[ "$key" =~ ^NAS_ ]]; then
            export "$key=$value"
        fi
    done < <(grep -E '^NAS_' "$ENV_FILE" 2>/dev/null || true)
else
    echo "⚠️  Warning: $ENV_FILE 파일을 찾을 수 없습니다."
    echo "   기본값을 사용합니다."
fi

# 환경변수 기본값 설정 (env 파일에 없을 경우)
# 보안상 실제 IP 주소는 기본값으로 설정하지 않음
if [ -z "$NAS_USER" ] || [ -z "$NAS_IP" ] || [ -z "$NAS_BACKEND_PATH" ]; then
    echo "❌ Error: NAS 설정이 .env 파일에 없습니다."
    echo "   backend/.env 파일에 다음 설정을 추가하세요:"
    echo "   NAS_USER=your-nas-username"
    echo "   NAS_IP=192.168.x.x"
    echo "   NAS_BACKEND_PATH=/volume1/web/focusmate-backend"
    exit 1
fi

NAS_PATH="$NAS_BACKEND_PATH"

echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                    NAS 동기화 테스트                                     ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""

# 1. Git hook 확인
echo "📋 1/5 Git hook 확인 중..."
if [ ! -f "$PROJECT_ROOT/.git/hooks/post-commit" ]; then
    echo "❌ post-commit hook이 없습니다!"
    exit 1
fi

if [ ! -x "$PROJECT_ROOT/.git/hooks/post-commit" ]; then
    echo "⚠️  post-commit hook에 실행 권한이 없습니다. 권한 부여 중..."
    chmod +x "$PROJECT_ROOT/.git/hooks/post-commit"
fi
echo "✅ Git hook 확인 완료"
echo ""

# 2. SSH 연결 테스트
echo "🔌 2/5 SSH 연결 테스트 중..."
if ssh -o BatchMode=yes -o ConnectTimeout=5 "${NAS_USER}@${NAS_IP}" "echo 'SSH 연결 성공'" 2>/dev/null; then
    echo "✅ SSH 연결 성공"
else
    echo "❌ SSH 연결 실패"
    echo "   SSH 키 인증이 설정되어 있는지 확인하세요."
    exit 1
fi
echo ""

# 3. 테스트 파일 생성
echo "📝 3/5 테스트 파일 생성 중..."
TEST_FILE="$BACKEND_DIR/.nas-sync-test"
TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
echo "NAS 동기화 테스트 - $TIMESTAMP" > "$TEST_FILE"
echo "✅ 테스트 파일 생성: $TEST_FILE"
echo ""

# 4. Git 커밋 (hook 자동 실행)
echo "📦 4/5 Git 커밋 중 (hook 자동 실행)..."
cd "$PROJECT_ROOT"

# 변경사항이 있는지 확인
if ! git diff --quiet "$TEST_FILE" 2>/dev/null; then
    git add "$TEST_FILE"
    echo "   커밋 메시지: [TEST] NAS 동기화 테스트"
    git commit -m "[TEST] NAS 동기화 테스트 - $TIMESTAMP" || {
        echo "❌ Git 커밋 실패"
        rm -f "$TEST_FILE"
        exit 1
    }
    echo "✅ Git 커밋 완료 (hook 자동 실행됨)"
else
    echo "⚠️  변경사항이 없습니다. 강제 커밋 시도..."
    git add -f "$TEST_FILE"
    git commit -m "[TEST] NAS 동기화 테스트 - $TIMESTAMP" --allow-empty || {
        echo "❌ Git 커밋 실패"
        rm -f "$TEST_FILE"
        exit 1
    }
    echo "✅ Git 커밋 완료 (hook 자동 실행됨)"
fi
echo ""

# 5. NAS에서 파일 확인
echo "🔍 5/5 NAS에서 파일 확인 중..."
sleep 2  # 동기화 완료 대기

if ssh "${NAS_USER}@${NAS_IP}" "test -f ${NAS_PATH}/.nas-sync-test" 2>/dev/null; then
    echo "✅ NAS에 테스트 파일이 동기화되었습니다!"

    # NAS의 파일 내용 확인
    NAS_CONTENT=$(ssh "${NAS_USER}@${NAS_IP}" "cat ${NAS_PATH}/.nas-sync-test" 2>/dev/null)
    LOCAL_CONTENT=$(cat "$TEST_FILE" 2>/dev/null)

    if [ "$NAS_CONTENT" = "$LOCAL_CONTENT" ]; then
        echo "✅ 파일 내용 일치 확인"
    else
        echo "⚠️  파일 내용이 다릅니다."
        echo "   로컬: $LOCAL_CONTENT"
        echo "   NAS: $NAS_CONTENT"
    fi

    # NAS의 테스트 파일 삭제
    ssh "${NAS_USER}@${NAS_IP}" "rm -f ${NAS_PATH}/.nas-sync-test" 2>/dev/null
    echo "   NAS의 테스트 파일 삭제 완료"
else
    echo "❌ NAS에 테스트 파일이 없습니다!"
    echo "   동기화가 실패했을 수 있습니다."
    echo ""
    echo "   수동 확인:"
    echo "   ssh ${NAS_USER}@${NAS_IP} 'ls -la ${NAS_PATH}/.nas-sync-test'"
    exit 1
fi

# 로컬 테스트 파일 삭제
rm -f "$TEST_FILE"
git add "$TEST_FILE" 2>/dev/null || true
git commit -m "[TEST] 테스트 파일 정리" --allow-empty 2>/dev/null || true

echo ""
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                    ✅ 테스트 완료                                         ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo ""
echo "🎉 NAS 동기화가 정상적으로 작동합니다!"
echo ""
echo "💡 다음 단계:"
echo "   1. 실제 코드 변경 후 커밋하면 자동으로 NAS에 동기화됩니다."
echo "   2. 동기화 후 NAS에서 서버 재시작:"
echo "      ssh ${NAS_USER}@${NAS_IP}"
echo "      /volume1/web/focusmate-backend/stop-nas.sh"
echo "      /volume1/web/focusmate-backend/start-nas.sh"

