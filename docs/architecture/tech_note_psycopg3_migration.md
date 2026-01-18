# 🛠️ Tech Note: Psycopg3 Migration & Docker Strategy

이 문서는 `asyncpg`에서 `psycopg3`로의 마이그레이션 절차와, 왜 Docker가 필수적인지에 대한 기술적 분석입니다.

## 1. Psycopg3 마이그레이션 절차 (코드 변경이 거의 없음)

`SQLAlchemy`는 'Dialect'라는 시스템을 통해 드라이버 차이를 추상화합니다. 따라서 비즈니스 로직 수정 없이 아래 3단계만으로 전환이 가능합니다.

### Step 1: 의존성 패키지 변경 (`requirements.txt`)
```diff
- asyncpg==0.30.0
+ psycopg[binary]==3.2.3
```
*   `[binary]` 옵션: 컴파일 없이 바로 실행 가능한 버전을 설치합니다.

### Step 2: DB 접속 URL 스키마 변경 (`.env`)
```diff
- DATABASE_URL=postgresql+asyncpg://user:pass@host:6543/db
+ DATABASE_URL=postgresql+psycopg://user:pass@host:6543/db
```
*   `+asyncpg`를 `+psycopg`로 바꾸면 끝입니다.

### Step 3: 연결 설정 간소화 (`session.py`)
기존에 `asyncpg`를 위해 넣었던 복잡한 "Prepared Statement 비활성화" 코드를 모두 제거할 수 있습니다. `psycopg3`는 PgBouncer와 기본적으로 잘 호환됩니다.

---

## 2. NAS 직접 실행 vs Docker 실행 (매우 중요)

질문하신 **"NAS에서도 사용 가능한가?"**에 대한 답은 **"가능하지만 위험하다"**입니다. 대신 **Docker를 강력히 추천**합니다.

| 구분 | NAS 직접 실행 (Native) | Docker 실행 (Container) 🏆 |
| :-- | :--- | :--- |
| **운영체제** | Synology OS (제한된 Linux) | Standard Linux (Debian/Alpine) |
| **라이브러리** | NAS에 깔린 `glibc` 버전에 종속됨 | 최신 라이브러리 자유롭게 사용 |
| **Redis 문제** | **CPU 100% Hang 발생 (현재 이슈)** | **정상 작동 (격리된 환경)** |
| **DB 드라이버** | `psycopg3` 빌드 실패 가능성 있음 | 100% 호환성 보장 |
| **결론** | **비추천 (언제든 또 터질 수 있음)** | **강력 추천 (Enterprise 표준)** |

### 왜 Docker인가?
현재 겪고 계신 **"Redis를 켜면 CPU가 치솟는 문제"**는 코드가 잘못된 게 아니라, **NAS의 운영체제가 Python의 비동기 처리(asyncio/uvloop)를 완벽하게 지원하지 않아서** 생기는 호환성 문제입니다.

Docker로 감싸면 NAS OS가 아닌, **컨테이너 내부의 완벽한 Linux 환경**에서 코드가 돌아가므로 **Redis 문제도 자연스럽게 해결**될 가능성이 매우 높습니다.

---

## 3. 최종 권장 전략

1.  **Phase 1 (지금)**: **NAS Native (Session Mode 5432)**로 일단 서비스 안정화. (현재 완료)
2.  **Phase 2 (다음)**: **Docker 환경 구축**.
    *   코드는 그대로 두고, 실행 환경만 Docker로 옮깁니다.
    *   이때 Redis도 다시 켜서 테스트해봅니다. (Docker 안에서는 잘 돌아갈 수 있음)
3.  **Phase 3 (완성)**: **Psycopg3 + 6543 포트 적용**.
    *   Docker 위에서 `psycopg3`로 드라이버만 싹 바꿔서 Transaction Mode(6543)로 연결합니다.
    *   동시 접속자 제한 없는 완전체 서비스가 됩니다.
