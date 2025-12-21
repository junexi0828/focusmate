#!/bin/bash

# AI 체점 환경 설정 스크립트
# Focus Mate 프로젝트용
#
# 사용법:
#   ./scripts/setup_grading_env.sh [--docker|--local]
#
# 옵션:
#   --docker: Docker Compose 사용 (가상환경 불필요, 권장)
#   --local:  로컬 환경에서 직접 실행 (가상환경 생성)

set -e  # 에러 발생 시 즉시 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# 프로젝트 루트 디렉토리로 이동
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

log_info "Focus Mate AI 체점 환경 설정을 시작합니다..."
log_info "프로젝트 루트: $PROJECT_ROOT"
log_info "Working directory: $(pwd)"

# 실행 모드 확인
MODE="${1:---docker}"

if [ "$MODE" = "--docker" ]; then
    log_info "Docker 모드로 설정합니다 (가상환경 불필요)"

    # Docker 및 Docker Compose 확인
    if ! command -v docker &> /dev/null; then
        log_error "Docker가 설치되어 있지 않습니다."
        log_info "설치 방법: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose가 설치되어 있지 않습니다."
        log_info "설치 방법: https://docs.docker.com/compose/install/"
        exit 1
    fi

    log_info "Docker 버전 확인 중..."
    docker --version
    docker-compose --version 2>/dev/null || docker compose version

    # docker-compose.yml 파일 확인
    if [ ! -f "docker-compose.yml" ]; then
        log_warn "docker-compose.yml 파일이 없습니다. 생성이 필요할 수 있습니다."
    fi

    log_info "✅ Docker 환경 설정 완료"
    log_info "다음 명령어로 서비스를 시작할 수 있습니다:"
    log_info "  docker-compose up --build"

elif [ "$MODE" = "--local" ]; then
    log_info "로컬 모드로 설정합니다 (가상환경 생성)"

    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3가 설치되어 있지 않습니다."
        log_info "Python 3.12 이상이 필요합니다."
        exit 1
    fi

    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    log_info "Python 버전: $(python3 --version)"

    # Node.js 확인
    if ! command -v node &> /dev/null; then
        log_error "Node.js가 설치되어 있지 않습니다."
        log_info "Node.js 20 이상이 필요합니다."
        exit 1
    fi

    NODE_VERSION=$(node --version)
    log_info "Node.js 버전: $NODE_VERSION"

    # 백엔드 설정
    if [ -d "backend" ]; then
        log_info "백엔드 환경 설정 중..."
        cd backend

        # 가상환경 생성
        if [ ! -d "venv" ]; then
            log_info "Python 가상환경 생성 중..."
            python3 -m venv venv
        else
            log_info "기존 가상환경 사용"
        fi

        # 가상환경 활성화
        log_info "가상환경 활성화 중..."
        source venv/bin/activate

        # 의존성 설치
        if [ -f "requirements.txt" ]; then
            log_info "Python 의존성 설치 중..."
            pip install --upgrade pip
            pip install -r requirements.txt

            if [ -f "requirements-dev.txt" ]; then
                log_info "개발 의존성 설치 중..."
                pip install -r requirements-dev.txt
            fi
        else
            log_warn "requirements.txt 파일이 없습니다."
        fi

        log_info "✅ 백엔드 환경 설정 완료"
        cd "$PROJECT_ROOT"
    else
        log_warn "backend 디렉토리가 없습니다."
    fi

    # 프론트엔드 설정
    if [ -d "frontend" ]; then
        log_info "프론트엔드 환경 설정 중..."
        cd frontend

        # 의존성 설치
        if [ -f "package.json" ]; then
            log_info "Node.js 의존성 설치 중..."
            npm install
        else
            log_warn "package.json 파일이 없습니다."
        fi

        log_info "✅ 프론트엔드 환경 설정 완료"
        cd "$PROJECT_ROOT"
    else
        log_warn "frontend 디렉토리가 없습니다."
    fi

    log_info "✅ 로컬 환경 설정 완료"
    log_info "다음 명령어로 서비스를 시작할 수 있습니다:"
    log_info "  # 백엔드"
    log_info "  cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    log_info "  # 프론트엔드"
    log_info "  cd frontend && npm run dev"

else
    log_error "잘못된 옵션입니다: $MODE"
    log_info "사용법: $0 [--docker|--local]"
    exit 1
fi

log_info ""
log_info "🎉 환경 설정이 완료되었습니다!"
log_info ""
log_info "다음 단계:"
if [ "$MODE" = "--docker" ]; then
    log_info "  1. docker-compose up --build"
    log_info "  2. http://localhost:3000 (프론트엔드)"
    log_info "  3. http://localhost:8000/docs (백엔드 API 문서)"
else
    log_info "  1. 백엔드: cd backend && source venv/bin/activate && uvicorn app.main:app --reload"
    log_info "  2. 프론트엔드: cd frontend && npm run dev"
    log_info "  3. http://localhost:3000 (프론트엔드)"
    log_info "  4. http://localhost:8000/docs (백엔드 API 문서)"
fi

