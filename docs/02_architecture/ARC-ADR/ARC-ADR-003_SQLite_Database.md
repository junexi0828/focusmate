# ADR-003: SQLite 데이터베이스 선택

**날짜**: 2025-12-04
**상태**: 승인됨
**결정자**: 아키텍처 팀

---

## 컨텍스트 (Context)

데이터베이스 선택 시 개발 편의성, 배포 안정성, 확장성을 모두 고려해야 했습니다.

옵션:

1. **SQLite**: 파일 기반, 서버 불필요
2. **PostgreSQL**: 강력한 기능, 프로덕션 적합
3. **MySQL**: 널리 사용됨, 중간 복잡도

AI 채점 환경과 Docker 기반 배포를 고려할 때, **이식성(Portability)**과 **설치 용이성(Installability)**이 최우선이었습니다.

---

## 결정 (Decision)

**개발 환경**: SQLite 사용
**프로덕션 환경**: SQLite (v1.0), PostgreSQL (v2.0 선택적)

**이유**:

- SQLAlchemy ORM 사용으로 데이터베이스 추상화
- 개발 환경에서 즉시 실행 가능 (서버 설정 불필요)
- Docker 환경에서 안정적인 파일 기반 저장

---

## 근거 (Rationale)

### 1. 이식성 (Portability)

**ISO 25010 이식성 특성 준수**:

- **설치 용이성**: 별도 데이터베이스 서버 불필요
- **환경 불가지론**: 동일한 파일이 모든 환경에서 동작
- **Docker 호환성**: 볼륨 마운트로 데이터 영속성 보장

### 2. 개발 편의성

**장점**:

- **즉시 시작**: `docker-compose up` 한 번으로 전체 스택 실행
- **테스트 용이성**: 인메모리 SQLite로 빠른 테스트
- **디버깅**: 파일 직접 확인 가능

### 3. 배포 안정성

**AI 채점 환경 최적화**:

- 네트워크 지연 없음 (로컬 파일)
- 인증 오류 없음 (파일 권한만)
- 의존성 최소화 (별도 서비스 불필요)

### 4. 확장성 고려

**SQLAlchemy ORM 사용**:

```python
# 개발: SQLite
DATABASE_URL = "sqlite:///./data/focusmate.db"

# 프로덕션: PostgreSQL (변경만으로 전환)
DATABASE_URL = "postgresql://user:pass@localhost/focusmate"
```

---

## 대안 (Alternatives)

### 대안 1: PostgreSQL (개발/프로덕션 동일)

**장점**:

- 프로덕션과 동일한 환경
- 고급 기능 (JSON, Full-text search 등)
- 동시성 처리 우수

**단점**:

- 별도 서버 필요 (Docker Compose 복잡도 증가)
- 초기 설정 시간 소요
- AI 채점 환경에서 네트워크/인증 이슈 가능

**결론**: 개발 편의성과 배포 안정성을 고려하여 채택하지 않음

### 대안 2: MySQL

**장점**:

- 널리 사용됨
- 중간 복잡도

**단점**:

- PostgreSQL과 유사한 단점
- SQLite 대비 이점 부족

**결론**: SQLite가 더 적합하여 채택하지 않음

### 대안 3: 인메모리 데이터베이스 (Redis)

**장점**:

- 매우 빠른 성능
- 실시간 데이터에 적합

**단점**:

- 영속성 보장 어려움
- 복잡한 쿼리 제한
- 추가 서비스 필요

**결론**: 영속성 요구사항을 충족하지 못하여 채택하지 않음

---

## 결과 (Consequences)

### 긍정적 결과

✅ **빠른 개발**: 데이터베이스 서버 설정 불필요
✅ **안정적 배포**: 네트워크/인증 이슈 없음
✅ **테스트 용이성**: 인메모리 모드로 빠른 테스트
✅ **ISO 25010 준수**: 이식성 요구사항 충족

### 부정적 결과

⚠️ **동시성 제한**: 쓰기 작업 시 락 발생 가능
⚠️ **확장성 제한**: 단일 파일로 인한 크기 제한
⚠️ **고급 기능 부족**: Full-text search, JSON 쿼리 등 제한

### 완화 전략

**v1.0**: SQLite로 충분 (예상 사용자: < 1000명)
**v2.0**: PostgreSQL 전환 고려 (사용자 증가 시)
**ORM 추상화**: SQLAlchemy로 데이터베이스 전환 용이

---

## 마이그레이션 전략

### SQLite → PostgreSQL 전환

```python
# 1. 환경 변수로 데이터베이스 선택
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/focusmate.db")

# 2. SQLAlchemy 모델은 변경 불필요
# 3. 마이그레이션 스크립트로 데이터 이전
```

---

## 참조 (References)

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [ISO/IEC 25010 - Portability](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)
- [REQ-NF-011](./../SRS.md#req-nf-011-컨테이너화): 컨테이너화 요구사항
- [ARCHITECTURE.md](./../ARCHITECTURE.md#adr-003-sqlite-개발--postgresql-프로덕션): 아키텍처 문서

---

**문서 끝**
