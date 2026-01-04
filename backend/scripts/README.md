# Scripts Directory

이 디렉토리는 프로젝트의 다양한 유틸리티 스크립트들을 용도별로 분류하여 관리합니다.

## 📁 디렉토리 구조

```
scripts/
├── archive/          # 사용하지 않는 레거시 스크립트
├── database/         # 데이터베이스 관련 스크립트
├── deployment/       # 배포 및 자동화 스크립트
├── docs/             # 문서 파일
├── tools/             # 개발 도구 및 유틸리티
└── verification/     # 검증 및 테스트 스크립트
```

## 📂 각 디렉토리 설명

### `database/` - 데이터베이스 관련

- `check_migration_status.py` - 마이그레이션 상태 확인
- `check_performance.py` - 성능 최적화 점검
- `check_existing_tables.py` - 기존 테이블 확인
- `create_performance_indexes.py` - 성능 인덱스 생성 (Python)
- `create_performance_indexes.sql` - 성능 인덱스 생성 (SQL)
- `create_tables.py` - 테이블 생성
- `seed_comprehensive.py` - 종합 시드 데이터 생성
- `smart_migrate.py` - 스마트 마이그레이션 (기존 테이블 처리)
- `verify_database.py` - 데이터베이스 검증

### `deployment/` - 배포 및 자동화

- `github-webhook-listener.py` - GitHub webhook 리스너 (NAS 자동 배포)
- `start-webhook-listener.sh` - Webhook 리스너 시작 스크립트
- `check_webhook_setup.sh` - Webhook 설정 확인

### `verification/` - 검증 및 테스트

- `verify_ranking_logic.py` - 랭킹 계산 로직 검증
- `test_smtp.py` - SMTP 테스트
- `test.sh` - 통합 테스트 스크립트

### `tools/` - 개발 도구 및 유틸리티

- `format-migration.py` - 마이그레이션 파일 포맷팅 (Alembic hook)
- `fix-python.sh` - Python 버전 호환성 수정
- `setup.sh` - 개발 환경 설정

### `docs/` - 문서

- `production_readiness_check.md` - 프로덕션 준비 체크리스트
- `database_verification_report.md` - 데이터베이스 검증 보고서

### `archive/` - 레거시 스크립트

사용하지 않는 오래된 스크립트들을 보관합니다.

## 🚀 주요 스크립트 사용법

### 데이터베이스 마이그레이션

```bash
# 스마트 마이그레이션 (기존 테이블 처리)
python scripts/database/smart_migrate.py

# 마이그레이션 상태 확인
python scripts/database/check_migration_status.py
```

### 성능 최적화

```bash
# 성능 점검
python scripts/database/check_performance.py

# 인덱스 생성
python scripts/database/create_performance_indexes.py
```

### 검증

```bash
# 랭킹 로직 검증
python scripts/verification/verify_ranking_logic.py

# 데이터베이스 검증
python scripts/database/verify_database.py
```

### 배포

```bash
# Webhook 리스너 시작 (NAS)
./scripts/deployment/start-webhook-listener.sh

# Webhook 설정 확인
./scripts/deployment/check_webhook_setup.sh
```

## 📝 참고

- 모든 스크립트는 `backend/` 디렉토리에서 실행해야 합니다.
- Python 스크립트는 가상환경이 활성화된 상태에서 실행하세요.
- 배포 스크립트는 NAS 환경에서 실행됩니다.

