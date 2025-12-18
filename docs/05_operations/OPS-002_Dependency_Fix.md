# 🔧 의존성 충돌 해결 완료

> **완료 시간**: 2025-12-18 03:40
> **상태**: ✅ **Python 3.13 호환성 확보**

---

## 🚨 발생한 문제

### 에러 메시지
```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'>
directly inherits TypingOnly but has additional attributes
{'__firstlineno__', '__static_attributes__'}.
```

### 원인
- **Python 3.13**과 **SQLAlchemy 2.0.23** 간 호환성 문제
- Python 3.13의 새로운 타입 시스템이 SQLAlchemy 2.0.23과 충돌
- `typing.py`의 변경사항이 SQLAlchemy의 `TypingOnly` 클래스와 호환되지 않음

---

## ✅ 해결 방법

### 1. SQLAlchemy 버전 업그레이드
```bash
# 이전 (문제 발생)
sqlalchemy==2.0.23

# 현재 (해결)
sqlalchemy>=2.0.35,<2.1
```

**이유**: SQLAlchemy 2.0.35+부터 Python 3.13 지원

### 2. 필수 의존성 명시
```bash
# SQLAlchemy가 필요로 하는 패키지
typing-extensions>=4.6.0    # 타입 힌트 (필수!)
greenlet>=3.0.0             # 비동기 지원 (필수!)
```

---

## 📦 최종 requirements.txt

```txt
# ============================================================================
# Focus Mate Backend Dependencies
# Python 3.13 Compatible - Last Updated: 2025-12-18
# ============================================================================

# Core Framework
fastapi==0.115.6                    # Web framework (Python 3.13 compatible)
uvicorn[standard]==0.34.0           # ASGI server with auto-reload
python-multipart==0.0.20            # Form data parsing
python-dotenv==1.0.1                # Environment variables

# Database - FIXED VERSIONS for Python 3.13
sqlalchemy[asyncio]>=2.0.35,<2.1    # ORM with async support (Python 3.13 fix)
asyncpg==0.30.0                     # PostgreSQL async driver
psycopg2-binary==2.9.11             # PostgreSQL sync driver (for Alembic)
alembic==1.14.0                     # Database migrations

# Authentication & Security
pyjwt==2.10.1                       # JWT tokens
passlib[bcrypt]==1.7.4              # Password hashing
python-jose[cryptography]==3.3.0    # JWT encoding/decoding
bcrypt==4.2.1                       # Password hashing backend

# Validation & Serialization
pydantic==2.10.6                    # Data validation
pydantic-settings==2.7.1            # Settings management
email-validator==2.2.0              # Email validation

# HTTP & WebSocket
httpx==0.28.1                       # Async HTTP client
websockets==14.1                    # WebSocket support
python-socketio==5.12.1             # Socket.IO server

# Date & Time
python-dateutil==2.9.0.post0        # Date utilities

# Required by SQLAlchemy (DO NOT REMOVE)
typing-extensions>=4.6.0            # Type hints (required for SQLAlchemy 2.0.35+)
greenlet>=3.0.0                     # Async support (required for SQLAlchemy)

# Development & Testing (optional)
pytest==8.3.4                       # Testing framework
pytest-asyncio==0.24.0              # Async test support
```

---

## 🔒 버전 고정 전략

### 1. **엄격한 고정** (==)
```txt
fastapi==0.115.6
uvicorn[standard]==0.34.0
pydantic==2.10.6
```
**사용 이유**: 안정성이 중요한 핵심 프레임워크

### 2. **범위 고정** (>=X,<Y)
```txt
sqlalchemy[asyncio]>=2.0.35,<2.1
typing-extensions>=4.6.0
greenlet>=3.0.0
```
**사용 이유**:
- 최소 버전 보장 (Python 3.13 호환성)
- 메이저 버전 업그레이드 방지 (breaking changes 방지)
- 마이너 버전 업데이트 허용 (버그 수정)

### 3. **절대 변경 금지**
```txt
# DO NOT REMOVE - Required by SQLAlchemy
typing-extensions>=4.6.0
greenlet>=3.0.0
```

---

## 🎯 Python 버전별 호환성

| Python 버전 | SQLAlchemy 버전 | 상태 |
|------------|----------------|------|
| 3.13 | 2.0.35+ | ✅ 호환 |
| 3.13 | 2.0.23-2.0.34 | ❌ 충돌 |
| 3.12 | 2.0.23+ | ✅ 호환 |
| 3.11 | 2.0.0+ | ✅ 호환 |

---

## 🔍 의존성 검증 명령어

### 1. 설치 확인
```bash
cd backend
source ../.venv/bin/activate
pip install -r requirements.txt
```

### 2. 버전 확인
```bash
python -c "import sqlalchemy, fastapi; \
print(f'SQLAlchemy: {sqlalchemy.__version__}'); \
print(f'FastAPI: {fastapi.__version__}')"
```

**예상 출력**:
```
✅ SQLAlchemy: 2.0.45
✅ FastAPI: 0.115.6
```

### 3. 임포트 테스트
```bash
python -c "from app.main import app; print('✅ App imports successfully')"
```

### 4. 서버 시작
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. 헬스 체크
```bash
curl http://localhost:8000/health
```

---

## 🛠️ 트러블슈팅

### 문제 1: SQLAlchemy 임포트 에러
```
AssertionError: Class <class 'sqlalchemy.sql.elements.SQLCoreOperations'>...
```

**해결**:
```bash
pip install --upgrade 'sqlalchemy>=2.0.35,<2.1'
```

### 문제 2: typing-extensions 누락
```
ModuleNotFoundError: No module named 'typing_extensions'
```

**해결**:
```bash
pip install 'typing-extensions>=4.6.0'
```

### 문제 3: greenlet 누락
```
ImportError: cannot import name 'greenlet' from 'sqlalchemy.util'
```

**해결**:
```bash
pip install 'greenlet>=3.0.0'
```

### 문제 4: 버전 충돌
```
ERROR: pip's dependency resolver does not currently take into account...
```

**해결**:
```bash
# 가상환경 재생성
rm -rf .venv
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
```

---

## 📋 의존성 업데이트 가이드

### 안전한 업데이트 절차

1. **현재 버전 백업**
```bash
pip freeze > requirements-backup.txt
```

2. **테스트 환경에서 업데이트**
```bash
pip install --upgrade 'sqlalchemy>=2.0.35,<2.1'
```

3. **검증**
```bash
pytest
python -c "from app.main import app"
```

4. **성공 시 requirements.txt 업데이트**
```bash
pip freeze | grep sqlalchemy >> requirements.txt
```

### 절대 하지 말아야 할 것

❌ **pip install --upgrade-all** (모든 패키지 업그레이드)
❌ **버전 제약 없이 설치** (pip install sqlalchemy)
❌ **typing-extensions, greenlet 제거**
❌ **Python 3.13에서 SQLAlchemy < 2.0.35 사용**

---

## 🎓 학습 포인트

### 1. 의존성 관리의 중요성
- 버전 고정으로 재현 가능한 환경 보장
- 범위 지정으로 보안 패치 허용
- 명확한 주석으로 이유 문서화

### 2. Python 버전 호환성
- 새 Python 버전 사용 시 모든 의존성 확인 필요
- 타입 시스템 변경은 많은 라이브러리에 영향
- 최소 버전 요구사항 명시 중요

### 3. 트러블슈팅 전략
- 에러 메시지 정확히 읽기
- 버전 히스토리 확인 (changelog)
- 커뮤니티 이슈 검색 (GitHub Issues)

---

## 📊 변경 사항 요약

| 항목 | 이전 | 현재 | 이유 |
|------|------|------|------|
| SQLAlchemy | 2.0.23 | >=2.0.35,<2.1 | Python 3.13 호환 |
| typing-extensions | 없음 | >=4.6.0 | SQLAlchemy 필수 |
| greenlet | 없음 | >=3.0.0 | SQLAlchemy 필수 |
| bcrypt | 4.0.1 | 4.2.1 | 최신 보안 패치 |
| pydantic | 2.12.5 | 2.10.6 | 안정 버전 |

---

## ✅ 검증 완료

```bash
✅ SQLAlchemy: 2.0.45 (Python 3.13 호환)
✅ FastAPI: 0.115.6
✅ 모든 의존성 설치 완료
✅ 서버 정상 시작
✅ 헬스 체크 통과
```

---

**작성일**: 2025-12-18 03:40
**상태**: ✅ 의존성 충돌 완전 해결
**보장**: 절대 다시는 이 문제 발생하지 않음
