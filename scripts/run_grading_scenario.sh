#!/bin/bash

# AI 체점 시나리오 실행 스크립트
# Focus Mate 프로젝트용
#
# 사용법:
#   ./scripts/run_grading_scenario.sh [--docker|--local]
#
# 이 스크립트는 다음을 수행합니다:
#   1. 환경 설정 (setup_grading_env.sh 호출)
#   2. 서비스 시작
#   3. 헬스체크
#   4. 테스트 실행
#   5. 리포트 생성

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# 로그 함수
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# 프로젝트 루트 디렉토리
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

log_info "Working directory: $(pwd)"

# 리포트 디렉토리 생성
REPORTS_DIR="$PROJECT_ROOT/reports"
mkdir -p "$REPORTS_DIR"

# 실행 모드 확인
MODE="${1:---docker}"

log_info "=========================================="
log_info "Focus Mate AI 체점 시나리오 시작"
log_info "=========================================="
log_info ""

# 1. 환경 설정
log_step "1/5: 환경 설정 중..."
if [ -f "$SCRIPT_DIR/setup_grading_env.sh" ]; then
    bash "$SCRIPT_DIR/setup_grading_env.sh" "$MODE"
else
    log_warn "setup_grading_env.sh를 찾을 수 없습니다. 수동 설정이 필요할 수 있습니다."
fi

log_info ""

# 2. 서비스 시작
log_step "2/5: 서비스 시작 중..."

if [ "$MODE" = "--docker" ]; then
    log_info "Docker Compose로 서비스 시작..."
    docker-compose up -d --build

    log_info "서비스가 시작될 때까지 대기 중..."
    sleep 10

elif [ "$MODE" = "--local" ]; then
    log_info "로컬 모드: 백엔드와 프론트엔드를 별도 터미널에서 실행해야 합니다."
    log_warn "백엔드: cd src/backend && source venv/bin/activate && uvicorn app.main:app --reload"
    log_warn "프론트엔드: cd frontend && npm run dev"
    log_info "서비스가 시작될 때까지 대기 중... (30초)"
    sleep 30
fi

log_info ""

# 3. 헬스체크
log_step "3/5: 헬스체크 중..."

BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"
HEALTH_ENDPOINT="$BACKEND_URL/health"

log_info "백엔드 헬스체크: $HEALTH_ENDPOINT"

MAX_RETRIES=10
RETRY_COUNT=0
HEALTH_CHECK_PASSED=false

while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if curl -f -s "$HEALTH_ENDPOINT" > /dev/null 2>&1; then
        log_info "✅ 백엔드 헬스체크 통과"
        HEALTH_CHECK_PASSED=true
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        log_info "헬스체크 재시도 중... ($RETRY_COUNT/$MAX_RETRIES)"
        sleep 2
    fi
done

if [ "$HEALTH_CHECK_PASSED" = false ]; then
    log_error "헬스체크 실패: 백엔드 서비스가 응답하지 않습니다."
    log_error "서비스 로그를 확인하세요."
    exit 1
fi

log_info ""

# 4. 테스트 실행
log_step "4/5: 테스트 실행 중..."

TEST_REPORT="$REPORTS_DIR/test_report_$(date +%Y%m%d_%H%M%S).txt"

if [ "$MODE" = "--docker" ]; then
    log_info "Docker 컨테이너에서 테스트 실행..."

    # 백엔드 테스트
    if docker-compose exec -T backend pytest --version 2>/dev/null; then
        log_info "백엔드 테스트 실행 중..."
        docker-compose exec -T backend pytest --cov --cov-report=term-missing > "$TEST_REPORT" 2>&1 || true
    else
        log_warn "백엔드 테스트를 실행할 수 없습니다."
    fi

    # 프론트엔드 테스트
    if docker-compose exec -T frontend npm test -- --version 2>/dev/null; then
        log_info "프론트엔드 테스트 실행 중..."
        docker-compose exec -T frontend npm test >> "$TEST_REPORT" 2>&1 || true
    else
        log_warn "프론트엔드 테스트를 실행할 수 없습니다."
    fi

elif [ "$MODE" = "--local" ]; then
    log_info "로컬 환경에서 테스트 실행..."

    # 백엔드 테스트
    if [ -d "src/backend" ]; then
        cd src/backend
        if [ -d "venv" ]; then
            source venv/bin/activate
            if command -v pytest &> /dev/null; then
                log_info "백엔드 테스트 실행 중..."
                pytest --cov --cov-report=term-missing > "$TEST_REPORT" 2>&1 || true
            fi
        fi
        cd "$PROJECT_ROOT"
    fi

    # 프론트엔드 테스트
    if [ -d "frontend" ]; then
        cd frontend
        if [ -f "package.json" ] && npm test -- --version 2>/dev/null; then
            log_info "프론트엔드 테스트 실행 중..."
            npm test >> "$TEST_REPORT" 2>&1 || true
        fi
        cd "$PROJECT_ROOT"
    fi
fi

log_info "테스트 리포트: $TEST_REPORT"
log_info ""

# 5. 리포트 생성
log_step "5/5: 리포트 생성 중..."

FINAL_REPORT="$REPORTS_DIR/grading_report_$(date +%Y%m%d_%H%M%S).md"

cat > "$FINAL_REPORT" << EOF
# Focus Mate AI 체점 리포트

**생성 시간**: $(date)
**실행 모드**: $MODE
**프로젝트 루트**: $PROJECT_ROOT

## 환경 정보

- **백엔드 URL**: $BACKEND_URL
- **프론트엔드 URL**: http://localhost:3000

## 헬스체크 결과

- 백엔드: ✅ 통과

## 테스트 결과

테스트 리포트는 다음 파일을 참조하세요:
- \`$TEST_REPORT\`

## 다음 단계

1. 테스트 리포트 확인: \`cat $TEST_REPORT\`
2. 서비스 로그 확인:
   - Docker 모드: \`docker-compose logs\`
   - 로컬 모드: 각 서비스의 터미널 출력 확인
3. API 문서 확인: $BACKEND_URL/docs

EOF

log_info "최종 리포트: $FINAL_REPORT"
log_info ""

log_info "=========================================="
log_info "✅ AI 체점 시나리오 완료"
log_info "=========================================="
log_info ""
log_info "리포트 파일:"
log_info "  - 테스트 리포트: $TEST_REPORT"
log_info "  - 최종 리포트: $FINAL_REPORT"
log_info ""
log_info "서비스 접속:"
log_info "  - 프론트엔드: http://localhost:3000"
log_info "  - 백엔드 API: $BACKEND_URL"
log_info "  - API 문서: $BACKEND_URL/docs"
log_info ""

if [ "$MODE" = "--docker" ]; then
    log_info "서비스 중지: docker-compose down"
fi

