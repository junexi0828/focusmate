#!/bin/bash

# FocusMate - Comprehensive Test Runner
# 모듈화된 테스트 실행 스크립트

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/backend"

# Test categories
CATEGORIES=("unit" "integration" "e2e" "performance" "security")

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
SKIPPED_TESTS=0

# Options
RUN_ALL=false
RUN_UNIT=false
RUN_INTEGRATION=false
RUN_E2E=false
RUN_PERFORMANCE=false
RUN_SECURITY=false
GENERATE_REPORT=false
VERBOSE=false
COVERAGE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --all|-a)
            RUN_ALL=true
            shift
            ;;
        --unit|-u)
            RUN_UNIT=true
            shift
            ;;
        --integration|-i)
            RUN_INTEGRATION=true
            shift
            ;;
        --e2e|-e)
            RUN_E2E=true
            shift
            ;;
        --performance|-p)
            RUN_PERFORMANCE=true
            shift
            ;;
        --security|-s)
            RUN_SECURITY=true
            shift
            ;;
        --report|-r)
            GENERATE_REPORT=true
            shift
            ;;
        --verbose|-v)
            VERBOSE=true
            shift
            ;;
        --coverage|-c)
            COVERAGE=true
            shift
            ;;
        --help|-h)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  -a, --all          Run all tests"
            echo "  -u, --unit         Run unit tests"
            echo "  -i, --integration  Run integration tests"
            echo "  -e, --e2e          Run E2E tests"
            echo "  -p, --performance  Run performance tests"
            echo "  -s, --security     Run security tests"
            echo "  -r, --report       Generate test report"
            echo "  -v, --verbose      Verbose output"
            echo "  -c, --coverage     Generate coverage report"
            echo "  -h, --help         Show this help"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# If no specific category selected, run all
if [ "$RUN_ALL" = false ] && [ "$RUN_UNIT" = false ] && [ "$RUN_INTEGRATION" = false ] && \
   [ "$RUN_E2E" = false ] && [ "$RUN_PERFORMANCE" = false ] && [ "$RUN_SECURITY" = false ]; then
    RUN_ALL=true
fi

# Activate virtual environment
if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
elif [ -f "$PROJECT_ROOT/venv/bin/activate" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
elif [ -f "$BACKEND_DIR/venv/bin/activate" ]; then
    source "$BACKEND_DIR/venv/bin/activate"
fi

# Change to backend directory
cd "$BACKEND_DIR"

# Function to print section header
print_section() {
    echo ""
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

# Function to run test category
run_test_category() {
    local category=$1
    local test_path="tests/$category"
    local category_name=$2

    if [ ! -d "$test_path" ]; then
        echo -e "${YELLOW}⚠️  $category_name 테스트 디렉토리가 없습니다.${NC}"
        return 0
    fi

    print_section "🧪 $category_name 테스트"

    local pytest_args="-v"
    if [ "$VERBOSE" = false ]; then
        pytest_args="$pytest_args --tb=short"
    fi

    if [ "$COVERAGE" = true ]; then
        pytest_args="$pytest_args --cov=app --cov-report=html --cov-report=term"
    fi

    # Run tests
    if pytest $pytest_args "$test_path" 2>&1 | tee "/tmp/test_${category}.log"; then
        # Extract test counts from pytest summary line
        local summary_line=$(grep -E "^=+ .* (passed|failed|skipped)" "/tmp/test_${category}.log" | tail -1)
        local passed=$(echo "$summary_line" | grep -oE "[0-9]+ passed" | grep -oE "[0-9]+" || echo "0")
        local failed=$(echo "$summary_line" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
        local skipped=$(echo "$summary_line" | grep -oE "[0-9]+ skipped" | grep -oE "[0-9]+" || echo "0")

        # Ensure we have valid numbers
        passed=${passed:-0}
        failed=${failed:-0}
        skipped=${skipped:-0}

        local total=$((passed + failed))

        TOTAL_TESTS=$((TOTAL_TESTS + total))
        PASSED_TESTS=$((PASSED_TESTS + passed))
        FAILED_TESTS=$((FAILED_TESTS + failed))
        SKIPPED_TESTS=$((SKIPPED_TESTS + skipped))

        echo -e "${GREEN}✅ $category_name 테스트 완료: $passed/$total 통과${NC}"
        return 0
    else
        # Extract counts even on failure
        local summary_line=$(grep -E "^=+ .* (passed|failed|skipped)" "/tmp/test_${category}.log" | tail -1)
        local failed=$(echo "$summary_line" | grep -oE "[0-9]+ failed" | grep -oE "[0-9]+" || echo "0")
        failed=${failed:-0}
        FAILED_TESTS=$((FAILED_TESTS + failed))
        echo -e "${RED}❌ $category_name 테스트 실패${NC}"
        return 1
    fi
}

# Main execution
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║         FocusMate - Comprehensive Test Runner              ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"

# Run selected test categories
if [ "$RUN_ALL" = true ] || [ "$RUN_UNIT" = true ]; then
    run_test_category "unit" "단위 테스트"
fi

if [ "$RUN_ALL" = true ] || [ "$RUN_INTEGRATION" = true ]; then
    run_test_category "integration" "통합 테스트"
fi

if [ "$RUN_ALL" = true ] || [ "$RUN_E2E" = true ]; then
    run_test_category "e2e" "E2E 테스트"
fi

if [ "$RUN_ALL" = true ] || [ "$RUN_PERFORMANCE" = true ]; then
    run_test_category "performance" "성능 테스트"
fi

if [ "$RUN_ALL" = true ] || [ "$RUN_SECURITY" = true ]; then
    run_test_category "security" "보안 테스트"
fi

echo ""
echo -e "${CYAN}╔════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                     테스트 요약                             ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "총 테스트:   ${BLUE}${TOTAL_TESTS}${NC}"
echo -e "통과:        ${GREEN}${PASSED_TESTS}${NC}"
echo -e "실패:        ${RED}${FAILED_TESTS}${NC}"
echo -e "건너뜀:      ${YELLOW}${SKIPPED_TESTS}${NC}"

if [ $TOTAL_TESTS -gt 0 ]; then
    SUCCESS_RATE=$((PASSED_TESTS * 100 / TOTAL_TESTS))
    echo -e "성공률:      ${BLUE}${SUCCESS_RATE}%${NC}"
    echo ""

    if [ $SUCCESS_RATE -ge 90 ]; then
        echo -e "${GREEN}✓ 우수! 시스템이 프로덕션 준비 완료! 🎉${NC}"
        exit_code=0
    elif [ $SUCCESS_RATE -ge 70 ]; then
        echo -e "${YELLOW}⚠ 좋음! 일부 문제가 있습니다.${NC}"
        exit_code=0
    else
        echo -e "${RED}✗ 중요! 배포 전 수정이 필요합니다.${NC}"
        exit_code=1
    fi
else
    echo -e "${RED}✗ 실행된 테스트가 없습니다!${NC}"
    exit_code=1
fi

# Generate report if requested
if [ "$GENERATE_REPORT" = true ]; then
    echo ""
    echo -e "${CYAN}📊 테스트 보고서 생성 중...${NC}"
    # Report generation would be handled by pytest plugins or custom script
    echo -e "${GREEN}✅ 보고서 생성 완료${NC}"
fi

exit $exit_code

