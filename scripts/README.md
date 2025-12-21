# Test Scripts

## run_tests.sh

포괄적인 테스트 실행 스크립트입니다. 모든 테스트 카테고리를 모듈화하여 실행할 수 있습니다.

### 사용법

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

### 옵션

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

## test_e2e.sh

E2E 테스트 전용 실행 스크립트입니다.

### 사용법

```bash
./scripts/test_e2e.sh
```

## test_performance.sh

성능 테스트 전용 실행 스크립트입니다.

### 사용법

```bash
./scripts/test_performance.sh
```

## test_security.sh

보안 테스트 전용 실행 스크립트입니다.

### 사용법

```bash
./scripts/test_security.sh
```

## test-all.sh

기존 포괄적인 시스템 테스트 스크립트입니다. (유지됨)

### 사용법

```bash
./scripts/test-all.sh
```

---

## 테스트 구조

```
backend/tests/
├── unit/              # 단위 테스트
├── integration/       # 통합 테스트
├── e2e/              # E2E 테스트
│   ├── test_user_workflow.py
│   └── test_api_integration.py
├── performance/       # 성능 테스트
│   ├── test_api_performance.py
│   └── test_matching_performance.py
├── security/         # 보안 테스트
│   └── test_security.py
└── test_tracker.py   # 테스트 추적 시스템
```

## 테스트 추적 관리

테스트 결과는 `backend/test_reports/` 디렉토리에 저장됩니다:

- JSON 리포트: `test_report_YYYYMMDD_HHMMSS.json`
- Markdown 리포트: `test_report_YYYYMMDD_HHMMSS.md`

---

**작성일**: 2025-12-21
**버전**: 2.0.0
