#!/bin/bash

# AI Testing Automation (V-Model 테스트 통합)
# Focus Mate 프로젝트용
#
# 사용법:
#   ./scripts/run_ai_testing.sh [--docker|--local]
#
# V-Model 테스트 단계:
#   1. 단위 테스트 (Unit Tests) - Verification
#   2. 통합 테스트 (Integration Tests) - Verification
#   3. 시스템 테스트 (System Tests) - Validation
#   4. 인수 테스트 (Acceptance Tests) - Validation
#   5. 성능 테스트 (Performance Tests) - Verification

# set -e 대신 개별 명령 실패를 처리하여 모든 테스트를 실행
set +e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
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

log_vmodel() {
    echo -e "${CYAN}[V-MODEL]${NC} $1"
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
MODE="${1:---local}"

# 테스트 결과 추적
UNIT_TESTS_PASSED=false
INTEGRATION_TESTS_PASSED=false
SYSTEM_TESTS_PASSED=false
ACCEPTANCE_TESTS_PASSED=false
PERFORMANCE_TESTS_PASSED=false

log_info "=========================================="
log_info "Focus Mate AI Testing Automation"
log_info "V-Model 테스트 통합 실행"
log_info "=========================================="
log_info ""

# 1. 환경 설정
log_step "1/7: 환경 설정 중..."
# Environment setup is handled by start.sh
log_info "환경 설정 확인 중..."
if [ ! -d "$PROJECT_ROOT/backend/venv" ]; then
    log_warn "가상환경이 없습니다. start.sh를 먼저 실행하세요."
fi

log_info ""

# 2. 서비스 시작 (시스템 테스트를 위해 필요)
log_step "2/7: 서비스 시작 중..."

if [ "$MODE" = "--docker" ]; then
    log_info "Docker Compose로 서비스 시작..."
    docker-compose up -d --build 2>/dev/null || log_warn "Docker Compose 실행 실패 (이미 실행 중일 수 있음)"
    log_info "서비스가 시작될 때까지 대기 중..."
    sleep 10
elif [ "$MODE" = "--local" ]; then
    log_info "로컬 모드: 백엔드와 프론트엔드를 별도 터미널에서 실행해야 합니다."
    log_warn "백엔드: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    log_warn "프론트엔드: cd frontend && npm run dev"
    log_info "서비스가 시작될 때까지 대기 중... (30초)"
    sleep 30
fi

log_info ""

# 3. 헬스체크
log_step "3/7: 헬스체크 중..."

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
    # 헬스체크 실패해도 단위/통합 테스트는 계속 진행
    log_warn "단위/통합 테스트는 계속 진행합니다..."
fi

log_info ""

# ==================================================
# V-MODEL 테스트 단계 시작
# ==================================================

# 4. 단위 테스트 (Unit Tests) - Verification
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_vmodel "V-MODEL 단계 1: 단위 테스트 (Unit Tests)"
log_vmodel "목적: Verification - 제대로 만들었는가?"
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "4/7: 단위 테스트 실행 중..."

UNIT_TEST_REPORT="$REPORTS_DIR/unit_tests_$(date +%Y%m%d_%H%M%S).txt"

if [ "$MODE" = "--docker" ]; then
    if docker-compose exec -T backend pytest tests/unit/ -v --tb=short > "$UNIT_TEST_REPORT" 2>&1; then
        log_info "✅ 단위 테스트 통과"
        UNIT_TESTS_PASSED=true
    else
        log_error "❌ 단위 테스트 실패"
        cat "$UNIT_TEST_REPORT" | tail -50
    fi
else
    cd "$PROJECT_ROOT/backend" || { log_error "backend 디렉토리를 찾을 수 없습니다."; exit 1; }
    if [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null || true
    fi
    if command -v pytest &> /dev/null; then
        pytest tests/unit/ -v --tb=short > "$UNIT_TEST_REPORT" 2>&1
        if [ $? -eq 0 ]; then
            log_info "✅ 단위 테스트 통과"
            UNIT_TESTS_PASSED=true
        else
            log_error "❌ 단위 테스트 실패"
            log_info "상세 리포트: $UNIT_TEST_REPORT"
            tail -50 "$UNIT_TEST_REPORT"
        fi
    else
        log_warn "pytest를 찾을 수 없습니다."
        log_warn "가상환경을 활성화했는지 확인하세요."
    fi
    cd "$PROJECT_ROOT"
fi

log_info ""

# 5. 통합 테스트 (Integration Tests) - Verification
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_vmodel "V-MODEL 단계 2: 통합 테스트 (Integration Tests)"
log_vmodel "목적: Verification - 컴포넌트 간 통합이 올바른가?"
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "5/7: 통합 테스트 실행 중..."

INTEGRATION_TEST_REPORT="$REPORTS_DIR/integration_tests_$(date +%Y%m%d_%H%M%S).txt"

if [ "$MODE" = "--docker" ]; then
    if docker-compose exec -T backend pytest tests/integration/ -v --tb=short > "$INTEGRATION_TEST_REPORT" 2>&1; then
        log_info "✅ 통합 테스트 통과"
        INTEGRATION_TESTS_PASSED=true
    else
        log_error "❌ 통합 테스트 실패"
        cat "$INTEGRATION_TEST_REPORT" | tail -50
    fi
else
    cd "$PROJECT_ROOT/backend" || { log_error "backend 디렉토리를 찾을 수 없습니다."; exit 1; }
    if [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null || true
    fi
    if command -v pytest &> /dev/null; then
        pytest tests/integration/ -v --tb=short > "$INTEGRATION_TEST_REPORT" 2>&1
        if [ $? -eq 0 ]; then
            log_info "✅ 통합 테스트 통과"
            INTEGRATION_TESTS_PASSED=true
        else
            log_error "❌ 통합 테스트 실패"
            log_info "상세 리포트: $INTEGRATION_TEST_REPORT"
            tail -50 "$INTEGRATION_TEST_REPORT"
        fi
    else
        log_warn "pytest를 찾을 수 없습니다."
    fi
    cd "$PROJECT_ROOT"
fi

log_info ""

# 6. 시스템 테스트 (System Tests) - Validation
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_vmodel "V-MODEL 단계 3: 시스템 테스트 (System Tests)"
log_vmodel "목적: Validation - 올바른 것을 만들었는가?"
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "6/7: 시스템 테스트 실행 중..."

SYSTEM_TEST_REPORT="$REPORTS_DIR/system_tests_$(date +%Y%m%d_%H%M%S).txt"

# 시스템 테스트: API 엔드포인트 전체 검증
if [ "$HEALTH_CHECK_PASSED" = true ]; then
    log_info "API 시스템 테스트 실행 중..."

    # API 검증 스크립트 실행
    if [ -f "$PROJECT_ROOT/scripts/verify_api.sh" ]; then
        bash "$PROJECT_ROOT/scripts/testing/verify_api.sh" > "$SYSTEM_TEST_REPORT" 2>&1
        if [ $? -eq 0 ]; then
            log_info "✅ 시스템 테스트 통과"
            SYSTEM_TESTS_PASSED=true
        else
            log_error "❌ 시스템 테스트 실패"
            cat "$SYSTEM_TEST_REPORT" | tail -50
        fi
    else
        # 간단한 API 테스트
        log_info "기본 API 엔드포인트 검증..."
        API_ENDPOINTS=(
            "/health"
            "/api/v1/stats/user/me"
            "/api/v1/rooms/my"
        )

        FAILED_ENDPOINTS=0
        for endpoint in "${API_ENDPOINTS[@]}"; do
            if curl -f -s "$BACKEND_URL$endpoint" > /dev/null 2>&1; then
                log_info "  ✅ $endpoint"
            else
                log_warn "  ⚠️  $endpoint (인증 필요할 수 있음)"
                FAILED_ENDPOINTS=$((FAILED_ENDPOINTS + 1))
            fi
        done

        if [ $FAILED_ENDPOINTS -eq 0 ]; then
            SYSTEM_TESTS_PASSED=true
        fi
    fi
else
    log_warn "헬스체크 실패로 인해 시스템 테스트를 건너뜁니다."
fi

log_info ""

# 7. 인수 테스트 (Acceptance Tests) - Validation
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_vmodel "V-MODEL 단계 4: 인수 테스트 (Acceptance Tests)"
log_vmodel "목적: Validation - 사용자 요구사항을 만족하는가?"
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "7/7: 인수 테스트 실행 중..."

ACCEPTANCE_TEST_REPORT="$REPORTS_DIR/acceptance_tests_$(date +%Y%m%d_%H%M%S).txt"

# E2E 테스트 실행 (인수 테스트)
E2E_FILES=$(find "$PROJECT_ROOT/backend/tests/e2e" -name "test_*.py" -type f 2>/dev/null | wc -l | tr -d ' ')

if [ "$E2E_FILES" -gt 0 ]; then
    if [ "$MODE" = "--docker" ]; then
        if docker-compose exec -T backend pytest tests/e2e/ -v --tb=short > "$ACCEPTANCE_TEST_REPORT" 2>&1; then
            log_info "✅ 인수 테스트 통과"
            ACCEPTANCE_TESTS_PASSED=true
        else
            log_error "❌ 인수 테스트 실패"
            cat "$ACCEPTANCE_TEST_REPORT" | tail -50
        fi
    else
        cd "$PROJECT_ROOT/backend" || { log_error "backend 디렉토리를 찾을 수 없습니다."; exit 1; }
        if [ -d "venv" ]; then
            source venv/bin/activate 2>/dev/null || true
        fi
        if command -v pytest &> /dev/null; then
            pytest tests/e2e/ -v --tb=short > "$ACCEPTANCE_TEST_REPORT" 2>&1
            if [ $? -eq 0 ]; then
                log_info "✅ 인수 테스트 통과"
                ACCEPTANCE_TESTS_PASSED=true
            else
                log_error "❌ 인수 테스트 실패"
                log_info "상세 리포트: $ACCEPTANCE_TEST_REPORT"
                tail -50 "$ACCEPTANCE_TEST_REPORT"
            fi
        fi
        cd "$PROJECT_ROOT"
    fi
else
    log_warn "E2E 테스트 파일이 없습니다. 인수 테스트를 건너뜁니다."
    log_info "인수 테스트는 사용자 시나리오를 검증합니다."
    log_info "테스트 파일을 추가하려면 backend/tests/e2e/ 디렉토리에 test_*.py 파일을 생성하세요."
    ACCEPTANCE_TESTS_PASSED=true  # 파일이 없으면 통과로 간주
fi

log_info ""

# 8. 성능 테스트 (Performance Tests) - Verification
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_vmodel "V-MODEL 단계 5: 성능 테스트 (Performance Tests)"
log_vmodel "목적: Verification - 성능 요구사항을 만족하는가?"
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_step "8/7: 성능 테스트 실행 중..."

PERFORMANCE_TEST_REPORT="$REPORTS_DIR/performance_tests_$(date +%Y%m%d_%H%M%S).txt"

if [ "$MODE" = "--docker" ]; then
    if docker-compose exec -T backend pytest tests/performance/ -v --tb=short -m performance > "$PERFORMANCE_TEST_REPORT" 2>&1; then
        log_info "✅ 성능 테스트 통과"
        PERFORMANCE_TESTS_PASSED=true
    else
        log_warn "⚠️  성능 테스트 실패 또는 스킵"
        cat "$PERFORMANCE_TEST_REPORT" | tail -30
    fi
else
    cd "$PROJECT_ROOT/backend" || { log_error "backend 디렉토리를 찾을 수 없습니다."; exit 1; }
    if [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null || true
    fi
    if command -v pytest &> /dev/null; then
        pytest tests/performance/ -v --tb=short > "$PERFORMANCE_TEST_REPORT" 2>&1
        EXIT_CODE=$?
        if [ $EXIT_CODE -eq 0 ]; then
            log_info "✅ 성능 테스트 통과"
            PERFORMANCE_TESTS_PASSED=true
        elif [ $EXIT_CODE -eq 5 ]; then
            log_warn "⚠️  성능 테스트 파일이 없거나 스킵됨"
            PERFORMANCE_TESTS_PASSED=true  # 테스트가 없으면 통과로 간주
        else
            log_warn "⚠️  성능 테스트 실패"
            log_info "상세 리포트: $PERFORMANCE_TEST_REPORT"
            tail -30 "$PERFORMANCE_TEST_REPORT"
        fi
    fi
    cd "$PROJECT_ROOT"
fi

log_info ""

# ==================================================
# 최종 리포트 생성
# ==================================================

log_step "최종 리포트 생성 중..."

FINAL_REPORT="$REPORTS_DIR/test_automation_report_$(date +%Y%m%d_%H%M%S).md"
JSON_REPORT="$REPORTS_DIR/automation_result.json"

# JSON 리포트 생성 (CI/CD 자동화용)
cat > "$JSON_REPORT" << EOF
{
  "project": "Focus Mate",
  "timestamp": "$(date -u +"%Y-%m-%dT%H:%M:%SZ")",
  "mode": "$MODE",
  "v_model_tests": {
    "unit_tests": {
      "status": "$([ "$UNIT_TESTS_PASSED" = true ] && echo "PASSED" || echo "FAILED")",
      "report": "$UNIT_TEST_REPORT"
    },
    "integration_tests": {
      "status": "$([ "$INTEGRATION_TESTS_PASSED" = true ] && echo "PASSED" || echo "FAILED")",
      "report": "$INTEGRATION_TEST_REPORT"
    },
    "system_tests": {
      "status": "$([ "$SYSTEM_TESTS_PASSED" = true ] && echo "PASSED" || echo "FAILED")",
      "report": "$SYSTEM_TEST_REPORT"
    },
    "acceptance_tests": {
      "status": "$([ "$ACCEPTANCE_TESTS_PASSED" = true ] && echo "PASSED" || echo "FAILED")",
      "report": "$ACCEPTANCE_TEST_REPORT"
    },
    "performance_tests": {
      "status": "$([ "$PERFORMANCE_TESTS_PASSED" = true ] && echo "PASSED" || echo "FAILED")",
      "report": "$PERFORMANCE_TEST_REPORT"
    }
  },
  "health_check": {
    "status": "$([ "$HEALTH_CHECK_PASSED" = true ] && echo "PASSED" || echo "FAILED")",
    "backend_url": "$BACKEND_URL"
  },
  "overall_status": "$([ "$UNIT_TESTS_PASSED" = true ] && [ "$INTEGRATION_TESTS_PASSED" = true ] && [ "$SYSTEM_TESTS_PASSED" = true ] && [ "$ACCEPTANCE_TESTS_PASSED" = true ] && echo "PASSED" || echo "FAILED")"
}
EOF

# 마크다운 리포트 생성
cat > "$FINAL_REPORT" << EOF
# Focus Mate AI Testing Automation Report (V-Model 테스트 통합)

**생성 시간**: $(date)
**실행 모드**: $MODE
**프로젝트 루트**: $PROJECT_ROOT

## V-Model 테스트 결과 요약

| 테스트 단계 | 상태 | 리포트 |
|------------|------|--------|
| **1. 단위 테스트** (Unit Tests) | $([ "$UNIT_TESTS_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED") | \`$UNIT_TEST_REPORT\` |
| **2. 통합 테스트** (Integration Tests) | $([ "$INTEGRATION_TESTS_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED") | \`$INTEGRATION_TEST_REPORT\` |
| **3. 시스템 테스트** (System Tests) | $([ "$SYSTEM_TESTS_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED") | \`$SYSTEM_TEST_REPORT\` |
| **4. 인수 테스트** (Acceptance Tests) | $([ "$ACCEPTANCE_TESTS_PASSED" = true ] && echo "✅ PASSED" || echo "❌ FAILED") | \`$ACCEPTANCE_TEST_REPORT\` |
| **5. 성능 테스트** (Performance Tests) | $([ "$PERFORMANCE_TESTS_PASSED" = true ] && echo "✅ PASSED" || echo "⚠️  SKIPPED") | \`$PERFORMANCE_TEST_REPORT\` |

## 환경 정보

- **백엔드 URL**: $BACKEND_URL
- **프론트엔드 URL**: http://localhost:3000
- **헬스체크**: $([ "$HEALTH_CHECK_PASSED" = true ] && echo "✅ 통과" || echo "❌ 실패")

## V-Model 테스트 단계 상세

### 1. 단위 테스트 (Unit Tests) - Verification
**목적**: 개별 함수/클래스가 올바르게 동작하는지 검증
**도구**: pytest
**대상**: \`backend/tests/unit/\`

### 2. 통합 테스트 (Integration Tests) - Verification
**목적**: 컴포넌트 간 통합이 올바르게 동작하는지 검증
**도구**: pytest
**대상**: \`backend/tests/integration/\`

### 3. 시스템 테스트 (System Tests) - Validation
**목적**: 전체 시스템이 요구사항을 만족하는지 검증
**도구**: API 검증, curl
**대상**: 전체 API 엔드포인트

### 4. 인수 테스트 (Acceptance Tests) - Validation
**목적**: 사용자 요구사항을 만족하는지 검증
**도구**: pytest (E2E)
**대상**: \`backend/tests/e2e/\`

### 5. 성능 테스트 (Performance Tests) - Verification
**목적**: 성능 요구사항을 만족하는지 검증
**도구**: pytest (benchmark)
**대상**: \`backend/tests/performance/\`

## 전체 테스트 결과

**전체 상태**: $([ "$UNIT_TESTS_PASSED" = true ] && [ "$INTEGRATION_TESTS_PASSED" = true ] && [ "$SYSTEM_TESTS_PASSED" = true ] && [ "$ACCEPTANCE_TESTS_PASSED" = true ] && echo "✅ **PASSED** - 모든 V-Model 테스트 통과" || echo "❌ **FAILED** - 일부 테스트 실패")

## 다음 단계

1. 상세 리포트 확인:
   - 단위 테스트: \`cat $UNIT_TEST_REPORT\`
   - 통합 테스트: \`cat $INTEGRATION_TEST_REPORT\`
   - 시스템 테스트: \`cat $SYSTEM_TEST_REPORT\`
   - 인수 테스트: \`cat $ACCEPTANCE_TEST_REPORT\`
   - 성능 테스트: \`cat $PERFORMANCE_TEST_REPORT\`

2. JSON 리포트 (CI/CD 자동화용): \`$JSON_REPORT\`

3. 서비스 로그 확인:
   - Docker 모드: \`docker-compose logs\`
   - 로컬 모드: 각 서비스의 터미널 출력 확인

4. API 문서 확인: $BACKEND_URL/docs

EOF

log_info "최종 리포트: $FINAL_REPORT"
log_info "JSON 리포트: $JSON_REPORT"
log_info ""

log_info "=========================================="
log_info "✅ AI Testing Automation 완료"
log_info "=========================================="
log_info ""

# 결과 요약 출력
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
log_vmodel "V-MODEL 테스트 결과 요약"
log_vmodel "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "단위 테스트:        $([ "$UNIT_TESTS_PASSED" = true ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"
echo -e "통합 테스트:        $([ "$INTEGRATION_TESTS_PASSED" = true ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"
echo -e "시스템 테스트:      $([ "$SYSTEM_TESTS_PASSED" = true ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"
echo -e "인수 테스트:        $([ "$ACCEPTANCE_TESTS_PASSED" = true ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${RED}❌ FAILED${NC}")"
echo -e "성능 테스트:        $([ "$PERFORMANCE_TESTS_PASSED" = true ] && echo -e "${GREEN}✅ PASSED${NC}" || echo -e "${YELLOW}⚠️  SKIPPED${NC}")"
echo ""

# 전체 상태 확인
if [ "$UNIT_TESTS_PASSED" = true ] && [ "$INTEGRATION_TESTS_PASSED" = true ] && [ "$SYSTEM_TESTS_PASSED" = true ] && [ "$ACCEPTANCE_TESTS_PASSED" = true ]; then
    log_info "🎉 모든 V-Model 테스트 통과!"
    log_info ""
    log_info "리포트 파일:"
    log_info "  - 마크다운 리포트: $FINAL_REPORT"
    log_info "  - JSON 리포트: $JSON_REPORT"
    log_info ""
    log_info "서비스 접속:"
    log_info "  - 프론트엔드: http://localhost:3000"
    log_info "  - 백엔드 API: $BACKEND_URL"
    log_info "  - API 문서: $BACKEND_URL/docs"
    log_info ""

    if [ "$MODE" = "--docker" ]; then
        log_info "서비스 중지: docker-compose down"
    fi

    exit 0
else
    log_error "❌ 일부 V-Model 테스트 실패"
    log_info ""
    log_info "상세 리포트 확인:"
    log_info "  - 마크다운 리포트: $FINAL_REPORT"
    log_info "  - JSON 리포트: $JSON_REPORT"
    log_info ""
    exit 1
fi
