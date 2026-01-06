# FocusMate Scripts Documentation

> **작성일**: 2026-01-07
> **버전**: 3.0.0 (AI Testing Automation)

---

## 📊 Script Hierarchy Overview

```
start.sh (최상위 계층 - Main Entry Point)
├── run_ai_testing.sh (AI Testing Automation - V-Model)
│   ├── verify_api.sh (System Tests)
│   └── backend/tests/ (pytest 직접 호출)
│       ├── unit/
│       ├── integration/
│       ├── e2e/
│       └── performance/
├── run_tests.sh (Modular Test Runner - 독립 실행 가능)
│   └── backend/tests/ (pytest 직접 호출)
│       ├── unit/
│       ├── integration/
│       ├── e2e/
│       ├── performance/
│       └── security/
├── test_security.sh (Security Tests)
│   └── backend/tests/security/ (pytest)
├── verify_api.sh (API Verification)
│   └── curl 명령어 (독립적 코드)
├── Individual Test Scripts (하위 계층)
│   ├── test_e2e.sh → backend/tests/e2e/
│   ├── test_integration.sh → backend/tests/integration/
│   ├── test_performance.sh → backend/tests/performance/
│   └── test_security.sh → backend/tests/security/
└── Infrastructure Scripts (독립적)
    ├── cloudflare-tunnel-setup.sh
    ├── start-cloudflare-tunnel.sh
    ├── stop-cloudflare-tunnel.sh
    ├── install-cloudflare-service.sh
    ├── setup-nas-initial.sh
    ├── test-nas-sync.sh
    └── check-services.sh
```
## 🎯 Script Categories

### 1. **Main Entry Point (최상위)**
- `start.sh` - 통합 실행 및 테스트 스크립트 (1889 lines)

### 2. **Test Orchestrators (상위 계층)**
- `run_ai_testing.sh` - AI Testing Automation with V-Model (532 lines)
- `run_tests.sh` - Modular Test Runner (260 lines)

### 3. **Specialized Test Scripts (중간 계층)**
- `test_e2e.sh` - E2E 테스트 전용
- `test_integration.sh` - 통합 테스트 전용
- `test_performance.sh` - 성능 테스트 전용
- `test_security.sh` - 보안 테스트 전용
- `verify_api.sh` - API 검증 스크립트

### 4. **Infrastructure Scripts (독립적)**
- Cloudflare Tunnel 관련 (4개)
- NAS 동기화 관련 (2개)
- 서비스 체크 (1개)

---

## 📋 Detailed Script Analysis

### `start.sh` (Main Entry Point)

**Purpose**: 통합 실행 및 테스트 메뉴 시스템

**Calls to Other Scripts**:

---

## 📋 Test Scripts Reference

### `run_ai_testing.sh` - AI Testing Automation

**V-Model 기반 종합 테스트 자동화**

**사용법**:
```bash
./scripts/run_ai_testing.sh [--docker|--local]
```

**특징**:
- ✅ V-Model 5단계 테스트 (Unit → Integration → System → Acceptance → Performance)
- ✅ JSON + Markdown 리포트 자동 생성
- ✅ Health check with 10회 재시도
- ✅ 실패해도 모든 테스트 계속 실행

**리포트 위치**:
- `reports/test_automation_report_YYYYMMDD_HHMMSS.md`
- `reports/automation_result.json`

---

### `run_tests.sh` - Modular Test Runner

**카테고리별 선택 실행 가능한 테스트 러너**

**사용법**:
```bash
# 전체 테스트 실행
./scripts/run_tests.sh --all

# 특정 카테고리만 실행
./scripts/run_tests.sh --unit
./scripts/run_tests.sh --integration
./scripts/run_tests.sh --e2e
./scripts/run_tests.sh --performance
./scripts/run_tests.sh --security

# 커버리지 리포트 생성
./scripts/run_tests.sh --all --coverage

# 상세 출력
./scripts/run_tests.sh --all --verbose

# 테스트 리포트 생성
./scripts/run_tests.sh --all --report
```

**옵션**:
- `-a, --all`: 모든 테스트 실행
- `-u, --unit`: 단위 테스트만 실행
- `-i, --integration`: 통합 테스트만 실행
- `-e, --e2e`: E2E 테스트만 실행
- `-p, --performance`: 성능 테스트만 실행
- `-s, --security`: 보안 테스트만 실행
- `-r, --report`: 테스트 리포트 생성
- `-v, --verbose`: 상세 출력
- `-c, --coverage`: 커버리지 리포트 생성
- `-h, --help`: 도움말 표시

**특징**:
- ✅ start.sh 없이 독립 실행 가능
- ✅ 카테고리별 선택 실행
- ✅ Coverage 리포트 지원

---

### Individual Test Scripts

#### `test_e2e.sh`
**E2E 테스트 전용 실행 스크립트**

**사용법**:
```bash
./scripts/test_e2e.sh
```

**테스트 대상**: `backend/tests/e2e/`

---

#### `test_integration.sh`
**통합 테스트 전용 실행 스크립트**

**사용법**:
```bash
./scripts/test_integration.sh
```

**테스트 대상**: `backend/tests/integration/`

---

#### `test_performance.sh`
**성능 테스트 전용 실행 스크립트**

**사용법**:
```bash
./scripts/test_performance.sh
```

**테스트 대상**: `backend/tests/performance/`

---

#### `test_security.sh`
**보안 테스트 전용 실행 스크립트**

**사용법**:
```bash
./scripts/test_security.sh
```

**테스트 대상**: `backend/tests/security/`

---

## 🔍 Backend Tests Structure

```
backend/tests/
├── conftest.py              # Pytest configuration
├── unit/                    # 단위 테스트 (58+ tests)
│   ├── test_rbac.py
│   ├── test_chat_service.py
│   ├── test_matching_service.py
│   ├── test_achievement_service.py
│   └── ...
├── integration/             # 통합 테스트
│   ├── test_api_integration.py
│   └── ...
├── e2e/                     # E2E 테스트
│   ├── test_user_workflow.py
│   ├── test_api_integration.py
│   └── test_basic_e2e.py
├── performance/             # 성능 테스트
│   ├── test_api_performance.py
│   ├── test_matching_performance.py
│   └── test_n_plus_one.py
└── security/                # 보안 테스트
    └── test_security.py
```

---

## 📊 Script Dependency Matrix

| Script | Called by start.sh | Uses Backend Tests | Independent Code | Standalone |
|:-------|:------------------:|:------------------:|:----------------:|:----------:|
| `run_ai_testing.sh` | ✅ Line 678 | ✅ pytest | ✅ V-Model | ✅ |
| `run_tests.sh` | ❌ | ✅ pytest | ✅ Runner | ✅ |
| `test_e2e.sh` | ❌ | ✅ pytest | ❌ | ✅ |
| `test_integration.sh` | ❌ | ✅ pytest | ❌ | ✅ |
| `test_performance.sh` | ❌ | ✅ pytest | ❌ | ✅ |
| `test_security.sh` | ✅ Line 831 | ✅ pytest | ❌ | ✅ |
| `verify_api.sh` | ✅ Line 1003 | ❌ | ✅ curl | ✅ |

---

## 🎯 Recommended Usage

### For General Testing
```bash
./scripts/start.sh
# 메뉴에서 "All Tests" 선택
```

### For Specific Categories
```bash
./scripts/run_tests.sh --unit
./scripts/run_tests.sh --integration
./scripts/run_tests.sh --e2e
```

### For CI/CD
```bash
./scripts/run_ai_testing.sh --local
```

### For Quick Development
```bash
cd backend
source venv/bin/activate
pytest tests/unit/test_rbac.py -v
```

---

## 📝 Test Reports

### AI Testing Automation Reports
- **Location**: `reports/`
- **Markdown**: `test_automation_report_YYYYMMDD_HHMMSS.md`
- **JSON**: `automation_result.json` (CI/CD용)

### Legacy Test Reports
- **Location**: `backend/test_reports/`
- **JSON**: `test_report_YYYYMMDD_HHMMSS.json`
- **Markdown**: `test_report_YYYYMMDD_HHMMSS.md`

---

## 🔑 Key Differences

### `run_ai_testing.sh` vs `run_tests.sh`

| Feature | run_ai_testing.sh | run_tests.sh |
|:--------|:------------------|:-------------|
| **방법론** | V-Model (5단계) | 카테고리별 |
| **리포트** | JSON + Markdown | Console only |
| **Health Check** | ✅ 10회 재시도 | ❌ |
| **start.sh 통합** | ✅ | ❌ |
| **독립 실행** | ✅ | ✅ |
| **Coverage** | ❌ | ✅ |
| **선택 실행** | ❌ (전체만) | ✅ (카테고리별) |

---

## 🚀 Quick Start

### 1. Via start.sh (Recommended)
```bash
./scripts/start.sh
# Select "All Tests" from menu
```

### 2. Direct AI Testing
```bash
./scripts/run_ai_testing.sh --local
```

### 3. Modular Testing
```bash
./scripts/run_tests.sh --unit --verbose
```

### 4. Individual Category
```bash
./scripts/test_e2e.sh
```
