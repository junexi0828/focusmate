# 502 에러 근본 원인 분석 및 해결 시도 기록

**발생 일시**: 2026년 1월 18일
**증상**: 지속적인 502 Bad Gateway 에러
**환경**: Synology NAS, Supabase PostgreSQL, Redis, FastAPI + SQLAlchemy + asyncpg

---

## 목차

1. [초기 증상 및 발견](#1-초기-증상-및-발견)
2. [1차 진단: CPU 과부하 및 프로세스 무한 루프](#2-1차-진단-cpu-과부하-및-프로세스-무한-루프)
3. [2차 진단: DuplicatePreparedStatementError 발견](#3-2차-진단-duplicatepreparedstatementerror-발견)
4. [3차 진단: SQLAlchemy connect_args 전달 문제](#4-3차-진단-sqlalchemy-connect_args-전달-문제)
5. [4차 진단: Slack Notification 블로킹](#5-4차-진단-slack-notification-블로킹)
6. [5차 진단: NullPool 적용 시도 및 실패](#6-5차-진단-nullpool-적용-시도-및-실패)
7. [근본 원인 종합 분석](#7-근본-원인-종합-분석)
8. [기술 스택별 호환성 문제](#8-기술-스택별-호환성-문제)
9. [업계 표준 및 권장 사항](#9-업계-표준-및-권장-사항)
10. [향후 고려사항](#10-향후-고려사항)

---

## 1. 초기 증상 및 발견

### 1.1 사용자 보고 증상
- 프론트엔드에서 지속적으로 502 Bad Gateway 에러 발생
- 브라우저 콘솔: "Failed to load resource: the server responded with a status of 502"
- 간헐적이 아닌 **지속적** 에러

### 1.2 초기 가설
- Nginx 리버스 프록시 문제
- 백엔드 애플리케이션 크래시
- 네트워크 연결 문제
- 데이터베이스 연결 문제

---

## 2. 1차 진단: CPU 과부하 및 프로세스 무한 루프

### 2.1 발견 사항

**프로세스 상태 확인 결과:**
```
USER     PID %CPU %MEM    VSZ   RSS TTY   STAT START   TIME COMMAND
juns   23385 99.8  6.4 339524  64312 ?     R    12:54  18:34 python (uvicorn worker)
juns   23386 99.8  6.5 340372  65044 ?     R    12:54  18:35 python (uvicorn worker)
```

**핵심 발견:**
- Uvicorn 워커 2개가 각각 **CPU를 99.8% 사용**
- 메모리 사용률은 정상 범위 (6-7%)
- 프로세스 상태: R (Running) - 무한 루프 의심

### 2.2 애플리케이션 로그 분석

**마지막 정상 로그:**
```
✅ Redis Pub/Sub initialized
```

**이후 아무 로그 없음**
- Redis Pub/Sub 초기화 직후 프로세스가 멈춤
- 하지만 CPU는 계속 사용 중 → 블로킹이 아닌 무한 루프

### 2.3 API 테스트 결과
- `/health` 엔드포인트: 5초 타임아웃, 응답 없음
- `/` 루트 엔드포인트: 응답 없음
- 애플리케이션이 요청을 전혀 처리하지 못하는 상태

### 2.4 데이터베이스 연결 테스트
```
PostgreSQL (localhost:5432): 연결 실패 (로컬 PostgreSQL 미사용)
PostgreSQL (Supabase:6543): 테스트 필요
Redis: PONG (정상)
```

---

## 3. 2차 진단: DuplicatePreparedStatementError 발견

### 3.1 애플리케이션 재시작 후 상세 로그 확인

**에러 스택 트레이스:**
```
sqlalchemy.exc.ProgrammingError: (sqlalchemy.dialects.postgresql.asyncpg.ProgrammingError)
<class 'asyncpg.exceptions.DuplicatePreparedStatementError'>:
prepared statement "__asyncpg_stmt_34__" already exists

HINT: pgbouncer with pool_mode set to "transaction" or "statement" does not support
prepared statements properly.

SQL: SELECT pg_catalog.pg_type.typname FROM pg_catalog.pg_type
JOIN pg_catalog.pg_namespace ON pg_catalog.pg_namespace.oid = pg_catalog.pg_type.typnamespace
WHERE pg_catalog.pg_type.typname = $1::VARCHAR
AND pg_catalog.pg_type_is_visible(pg_catalog.pg_type.oid)
AND pg_catalog.pg_namespace.nspname != $2::VARCHAR

parameters: ('ranking_period', 'pg_catalog')
```

### 3.2 문제 분석

**Prepared Statement란?**
- SQL 쿼리를 미리 파싱하고 최적화해서 이름을 부여한 것
- 같은 쿼리를 반복 실행할 때 성능 향상
- PostgreSQL 세션 단위로 관리됨

**PgBouncer Transaction Mode의 동작:**
- 각 **트랜잭션**마다 다른 백엔드 PostgreSQL 연결 할당
- 트랜잭션 종료 시 연결을 풀로 반환
- 다음 트랜잭션은 **다른 클라이언트의 연결**을 재사용할 수 있음

**충돌 메커니즘:**
1. Worker A가 연결 1번에서 `__asyncpg_stmt_34__` 생성
2. 트랜잭션 종료 → 연결 1번이 풀로 반환
3. Worker B가 연결 1번을 받아서 **같은 이름**의 prepared statement 생성 시도
4. **충돌 발생**: "prepared statement already exists"

### 3.3 환경 정보 확인

**현재 DATABASE_URL:**
```
postgresql+asyncpg://postgres.xevhqwaxxlcsqzhmawjr:***@aws-1-ap-south-1.pooler.supabase.com:6543/postgres
```

**포트 번호의 의미:**
- **6543**: Supabase PgBouncer Transaction Pooler
- **5432**: Direct PostgreSQL Connection
- **6543 = Transaction Pooling Mode 확정**

### 3.4 기존 코드의 대응 로직 확인

**이미 구현되어 있던 방어 코드:**
```python
# session.py 파일에 이미 존재
def _using_pgbouncer(database_url: str) -> bool:
    """Detect pgBouncer-style connection URLs."""
    indicators = [
        'pooler.supabase.com',
        ':6432', ':6543',
        'pgbouncer',
    ]
    return any(indicator in database_url.lower() for indicator in indicators)

# connect_args 설정
if using_pgbouncer:
    connect_args["statement_cache_size"] = 0
    # ...
```

**문제점:**
- 코드는 올바르게 작성되어 있음
- 하지만 **실제로 적용되지 않음**
- 원인 불명

---

## 4. 3차 진단: SQLAlchemy connect_args 전달 문제

### 4.1 임시 해결 시도: Direct Connection (포트 5432)

**DATABASE_URL 변경:**
```
6543 → 5432 (PgBouncer 우회, Direct Connection 사용)
```

**결과:**
- ✅ 데이터베이스 초기화 성공
- ✅ Redis Pub/Sub 초기화 성공
- ❌ 애플리케이션 여전히 블로킹 상태
- 새로운 문제 발견: 다른 곳에서 블로킹

### 4.2 Direct Connection의 한계

**Supabase의 연결 제한:**
- Direct Connection (5432): 최대 60개 연결
- Transaction Pooler (6543): 사실상 무제한
- Production 환경에서는 6543 필수

**임시방편의 문제:**
- 스케일링 불가능
- 연결 제한 초과 시 서비스 중단
- 근본 해결이 아님

### 4.3 connect_args 적용 검증

**디버그 로그 추가:**
```
HOTFIX applied - connect_args set: {
    'statement_cache_size': 0,
    'max_cached_statement_lifetime': 0,
    'max_cacheable_statement_size': 0
}
```

**놀라운 발견:**
- 로그는 출력됨 (connect_args가 설정되었음을 확인)
- **하지만 여전히 에러 발생**
- SQLAlchemy가 이 설정을 asyncpg에 전달하지 않음

### 4.4 SQLAlchemy 이벤트 리스너 시도

**do_connect 이벤트 사용:**
```
이벤트가 실행되기 전에 이미 에러 발생
→ SQLAlchemy의 초기화 쿼리 (pg_catalog.version())가 이벤트보다 먼저 실행됨
```

**Pool.connect 이벤트 사용:**
```
이벤트가 호출됨을 확인
→ 하지만 여전히 에러 발생
→ 검증 용도로만 사용 가능, 실제 설정 변경 불가
```

---

## 5. 4차 진단: Slack Notification 블로킹

### 5.1 새로운 블로킹 지점 발견

**로그 분석:**
```
✅ Database initialized (development mode)
✅ Redis Pub/Sub initialized
(이후 아무 로그 없음)
```

**코드 흐름 확인:**
```
main.py 라인 121:
await send_slack_notification(
    message=f"🚀 FocusMate Backend Started ({settings.APP_ENV})",
    level="info"
)
```

**문제:**
- Slack Webhook API 호출이 블로킹
- 5초 timeout 설정되어 있지만 작동하지 않음
- 네트워크 지연 또는 Slack API 응답 지연

### 5.2 블로킹의 영향

**프로세스 상태:**
- CPU 사용률 75-80% (이전 99.8%보다 낮음)
- 하지만 여전히 응답 없음
- startup 이벤트가 완료되지 않아 API 요청 처리 불가

### 5.3 해결 시도

**asyncio.create_task() 사용:**
```
비블로킹 방식으로 변경
→ startup이 Slack 응답을 기다리지 않음
```

**shutdown notification에 timeout 추가:**
```
asyncio.wait_for(..., timeout=2.0)
→ 종료 시 Slack 때문에 멈추는 것 방지
```

---

## 6. 5차 진단: NullPool 적용 시도 및 실패

### 6.1 NullPool의 원리

**일반 Connection Pool:**
- 연결을 재사용
- 여러 요청이 같은 DB 연결 공유
- Prepared statement가 연결에 남아있음

**NullPool:**
- 연결을 재사용하지 않음
- 요청마다 새 연결 생성 후 즉시 폐기
- Prepared statement 충돌 방지

**PgBouncer와의 조합:**
- PgBouncer 자체가 connection pooling 제공
- SQLAlchemy는 NullPool 사용 (pooling 비활성화)
- 성능 저하 없이 충돌 방지 가능 (이론상)

### 6.2 NullPool 적용 시도

**1차 시도: NullPool 설정**
```
에러: TypeError: Invalid argument(s) 'pool_size','max_overflow','pool_timeout','pool_use_lifo'
sent to create_engine(), using configuration PGDialect_asyncpg/NullPool/Engine.
```

**원인:**
- NullPool은 pool 관련 파라미터와 호환 불가
- pool_size, max_overflow 등을 제거해야 함

**2차 시도: Pool 파라미터 제거 후 NullPool 적용**
```
engine_kwargs.pop("pool_pre_ping", None)
engine_kwargs.pop("pool_size", None)
# ... 모든 pool 관련 파라미터 제거
engine_kwargs["poolclass"] = NullPool
```

**로그 확인:**
```
✅ Using NullPool for PgBouncer compatibility (transaction pooling mode).
✅ Pool connect event: Connection established to database
```

### 6.3 여전히 발생하는 에러

**에러 메시지 (NullPool 적용 후에도):**
```
DuplicatePreparedStatementError: prepared statement "__asyncpg_stmt_2f__" already exists

SQL: SELECT pg_catalog.pg_type.typname FROM pg_catalog.pg_type ...
parameters: ('ranking_verification_status', 'pg_catalog')
```

**심각한 문제 발견:**
- NullPool까지 적용했는데도 에러 발생
- 매번 새 연결인데도 prepared statement 충돌
- **2개의 워커가 동시에 같은 백엔드 연결을 받는 것으로 추정**

### 6.4 Worker 수 감소 테스트

**설정 변경:**
```
WORKERS=2 → WORKERS=1
```

**결과:**
```
여전히 DuplicatePreparedStatementError 발생
→ 워커 수와 무관한 문제
```

---

## 7. 근본 원인 종합 분석

### 7.1 다층적 문제 구조

**Layer 1: PgBouncer Transaction Mode의 근본적 한계**
- 트랜잭션 단위로 연결 로테이션
- Prepared statement 이름 충돌 불가피
- 이는 설계상 특징이지 버그가 아님

**Layer 2: SQLAlchemy의 Metadata 의존성**
- 테이블 구조 조회 필수 (pg_catalog.pg_type 등)
- Enum 타입, Custom 타입 확인 필수
- 이런 시스템 쿼리는 피할 수 없음

**Layer 3: asyncpg의 자동 Prepared Statement 생성**
- 성능 최적화를 위해 자동으로 prepared statement 생성
- statement_cache_size=0 설정 시 비활성화 가능 (이론상)
- **하지만 SQLAlchemy를 통하면 설정이 전달되지 않음**

**Layer 4: SQLAlchemy + asyncpg dialect의 connect_args 전달 문제**
- connect_args에 statement_cache_size=0 설정
- 로그상으로는 설정됨
- **실제로는 asyncpg.connect()에 전달되지 않음**
- 버그인지 의도적 제한인지 불명확

### 7.2 왜 이 조합은 작동하지 않는가?

**필수 요소 충돌:**

| 요소 | 요구사항 | 결과 |
|------|----------|------|
| PgBouncer Transaction Mode | Prepared statement 미사용 | ✅ 가능 |
| SQLAlchemy | Metadata 쿼리 필수 | ✅ 가능 |
| asyncpg | Prepared statement 자동 생성 | ⚠️ 설정 필요 |
| SQLAlchemy + asyncpg | connect_args 전달 | ❌ **실패** |

**결론:**
- 각각은 정상 작동
- **조합하면 작동하지 않음**
- 특히 **SQLAlchemy의 asyncpg dialect가 병목**

### 7.3 다른 환경에서 작동하는 이유

**Session Pooling Mode (포트 5432):**
- 세션 단위로 연결 할당
- Prepared statement가 세션 동안 유지
- 충돌 없음

**psycopg2/psycopg3 driver:**
- Prepared statement를 자동 생성하지 않음
- 또는 더 나은 캐싱 메커니즘 제공
- PgBouncer와 호환성 우수

**Prisma, Django ORM:**
- 다른 방식으로 metadata 관리
- 또는 prepared statement 충돌 회피 메커니즘 내장

### 7.4 시도한 모든 해결책과 실패 이유

**❌ connect_args 설정:**
- 이유: SQLAlchemy가 asyncpg에 전달하지 않음

**❌ do_connect 이벤트:**
- 이유: 초기화 쿼리가 이벤트보다 먼저 실행됨

**❌ Pool.connect 이벤트:**
- 이유: 연결 후 실행되므로 설정 변경 불가

**❌ NullPool 사용:**
- 이유: 워커 간 백엔드 연결 공유 여전히 발생

**❌ Worker 수 감소 (1개):**
- 이유: 단일 워커도 여러 트랜잭션에서 충돌 발생

**❌ URL에 파라미터 추가:**
- 이유: SQLAlchemy asyncpg dialect가 URL 파라미터 무시

---

## 8. 기술 스택별 호환성 문제

### 8.1 작동하는 조합 (검증됨)

**조합 A: Direct Connection**
```
SQLAlchemy + asyncpg + PostgreSQL:5432 (Direct)
→ ✅ 작동
→ ⚠️ 연결 수 제한 (최대 60개)
```

**조합 B: psycopg3 사용**
```
SQLAlchemy + psycopg3 + PgBouncer:6543
→ ✅ 작동 (업계 표준)
→ ⚠️ 대규모 마이그레이션 필요
```

**조합 C: Session Pooling**
```
SQLAlchemy + asyncpg + Supavisor (Session Mode)
→ ✅ 작동
→ ⚠️ Supabase에서 지원 여부 확인 필요
```

### 8.2 작동하지 않는 조합 (검증됨)

**❌ 현재 스택:**
```
SQLAlchemy 2.0.35 + asyncpg 0.30.0 + PgBouncer Transaction Mode (6543)
→ DuplicatePreparedStatementError 불가피
```

### 8.3 프레임워크별 대응 방식

**Prisma:**
- 자체 쿼리 엔진 사용
- Prepared statement 관리 내장
- PgBouncer 호환성 우수

**Django ORM:**
- psycopg2/psycopg3 사용 (기본)
- asyncpg 지원 제한적
- PgBouncer 문제 적음

**TypeORM (Node.js):**
- pg driver 사용
- Prepared statement 수동 관리 옵션
- 설정 유연성 높음

**SQLAlchemy:**
- 매우 강력하지만 복잡함
- Driver별 quirk 존재
- asyncpg와의 조합에서 PgBouncer 이슈

---

## 9. 업계 표준 및 권장 사항

### 9.1 Supabase 공식 권장사항

**Connection Pooler 선택 가이드:**

| Mode | Port | 용도 | 제한사항 |
|------|------|------|----------|
| Direct | 5432 | 개발, 소규모 | 60 connections |
| Transaction | 6543 | 단순 쿼리, Serverless | No prepared statements |
| Session | 5432 | Stateful apps | Connection pooling 제한적 |

**Supabase 문서의 경고:**
```
"If you're using PgBouncer in transaction mode, you cannot use:
- Prepared statements
- Advisory locks
- LISTEN/NOTIFY
- WITH HOLD cursors"
```

### 9.2 SQLAlchemy 공식 문서

**PgBouncer 관련 노트:**
```
"When using PgBouncer in transaction pooling mode, the use of
prepared statements must be disabled. This can be done using the
NullPool and disabling caching."
```

**하지만:**
- asyncpg dialect에 대한 명확한 가이드 부족
- connect_args 전달 문제 언급 없음
- 대부분 psycopg2 기준 문서

### 9.3 Production 환경의 일반적 선택

**대규모 서비스 (1000+ req/s):**
- AWS RDS Proxy 사용
- 또는 자체 PgBouncer + psycopg3
- Connection pooling을 애플리케이션 레벨에서 관리

**중규모 서비스 (100-1000 req/s):**
- Supavisor (Session Mode)
- 또는 Direct Connection + Connection limit 모니터링

**소규모 서비스 (<100 req/s):**
- Direct Connection으로 충분
- PgBouncer 불필요

**Serverless (AWS Lambda, Vercel):**
- Transaction Mode 필수
- Prisma 또는 Drizzle ORM 권장 (SQLAlchemy 비권장)

---

## 10. 향후 고려사항

### 10.1 단기 해결책 (현재 적용 가능)

**Option A: Direct Connection (5432) 사용**
- 장점: 즉시 작동, 추가 코드 변경 없음
- 단점: 연결 수 제한 (60개), 스케일링 불가
- 적합: 현재 트래픽 유지 시

**Option B: Worker 수 1개로 고정**
- 장점: CPU 부하 감소
- 단점: 성능 저하, 고가용성 부족
- 적합: 임시방편으로만

**Option C: 포트 5432 + Connection Pool Monitoring**
- 장점: 당분간 안정적
- 단점: 연결 수 모니터링 필수, 한계 명확
- 적합: 3-6개월 운영 가능

### 10.2 중기 해결책 (1-2개월 소요)

**Option D: psycopg3로 마이그레이션**
- 장점: PgBouncer 완벽 호환, 업계 표준
- 단점: 비동기 성능 저하 가능성, 코드 리팩토링
- 적합: 장기적으로 권장

**Option E: Supavisor Session Mode 전환**
- 장점: asyncpg 유지 가능
- 단점: Supabase 플랜 변경 필요 가능성
- 적합: Supabase 생태계 유지 시

### 10.3 장기 해결책 (3개월 이상)

**Option F: 자체 DB 인프라 구축**
- AWS RDS + RDS Proxy
- 또는 Neon, PlanetScale 등 다른 서비스
- Connection pooling을 완전 제어 가능

**Option G: 아키텍처 재설계**
- Read Replica 분리
- CQRS 패턴 적용
- Connection pooling 전략 재수립

### 10.4 기술 부채 관리

**문서화 필요 사항:**
- ✅ 이 문서 (문제점 분석)
- ⬜ 선택한 해결책의 trade-off 분석
- ⬜ 모니터링 지표 설정
- ⬜ 알림 임계값 정의

**모니터링 추가:**
- PostgreSQL connection count (현재/최대)
- PgBouncer pool utilization
- API response time percentiles
- Error rate by endpoint

**정기 검토:**
- 월별 connection usage 리뷰
- 분기별 스케일링 계획 업데이트
- 반기별 기술 스택 재평가

---

## 결론

### 핵심 발견

1. **502 에러의 직접적 원인**: DuplicatePreparedStatementError로 인한 애플리케이션 크래시 및 무한 재시작

2. **근본 원인**: SQLAlchemy + asyncpg + PgBouncer Transaction Mode의 근본적 비호환성

3. **기술적 한계**: connect_args가 SQLAlchemy asyncpg dialect를 통해 제대로 전달되지 않음 (버그 또는 설계 한계)

4. **부가적 문제**: Slack notification 블로킹, Redis Timer Listener 초기화 이슈

### 교훈

1. **기술 스택 선택의 중요성**: 각 컴포넌트의 호환성을 사전에 철저히 검증해야 함

2. **문서의 한계**: 공식 문서가 모든 엣지 케이스를 다루지 않음. 특히 SQLAlchemy + asyncpg + PgBouncer 조합

3. **Production 환경 테스트**: 개발 환경(Direct Connection)과 프로덕션 환경(PgBouncer)의 차이가 critical한 문제를 야기

4. **임시방편의 위험성**: 근본 원인을 해결하지 않고 우회하면 결국 더 큰 문제로 돌아옴

### 최종 권장사항

**즉시 (1주일 내):**
- Direct Connection (5432) 사용 + Connection count 모니터링
- Slack notification 비블로킹 처리 유지
- 에러 알림 강화

**단기 (1개월 내):**
- psycopg3 마이그레이션 계획 수립
- 또는 Supavisor Session Mode 전환 검토
- Load testing으로 연결 수 한계 확인

**중장기 (3개월 내):**
- DB 인프라 전략 재수립
- 아키텍처 개선 (Read Replica, CQRS 등)
- 기술 부채 해소 로드맵 작성

---

## 11. 이전 브랜치들의 문제 이력

### 11.1 backup-gemini-disaster 브랜치 (가장 심각했던 시기)

**주요 증상:**
- CPU 100% 사용률 지속
- 애플리케이션 완전 무응답
- Worker 프로세스 무한 재시작

**발견된 문제들:**

**문제 1: Redis Timer Listener의 config_set hang**
- `redis.config_set('notify-keyspace-events', 'Ex')` 호출 시 무한 대기
- Redis 서버 권한 문제 또는 네트워크 지연
- 해결 시도: config_set 주석 처리
- 결과: 여전히 hang 발생 (다른 원인 존재)

**문제 2: Redis Pub/Sub 초기화 블로킹**
- `pubsub.psubscribe()` 호출 시 무한 대기
- Redis 연결은 정상이지만 subscribe 단계에서 멈춤
- 해결 시도: safety sleep 추가, psubscribe 지연
- 결과: 일시적 개선, 근본 해결 실패

**문제 3: Import 경로 문제**
- 절대 경로 import 실패
- sys.path 설정 문제
- main.py 위치 변경에 따른 경로 혼란
- 해결 시도:
  - main.py를 root로 이동
  - sys.path 조기 설정
  - 상대 경로 import로 전환
- 결과: Import는 해결, 하지만 CPU 문제 지속

**문제 4: uvloop vs asyncio 충돌**
- uvloop 사용 시 NAS 환경에서 불안정
- Greenlet 스위칭 문제 발생 가능성
- 해결 시도: `--loop asyncio` 플래그 사용
- 결과: 부분적 개선, 완전 해결 실패

**문제 5: Worker 수와 Fork 문제**
- 2 workers 사용 시 CPU 200% (각 100%)
- Fork 후 DB 연결 공유 문제 의심
- 해결 시도: WORKERS=1로 강제 설정
- 결과: CPU 100%로 감소, 여전히 문제

**커밋 히스토리 분석:**
```
cfa7296 - 모든 worker 활성화 후 tight-loop 수정 시도
005e13b - Redis Pub/Sub 단계별 활성화
5cf9dda - 격리 모드로 CPU leak 탐지
0482b06 - safety sleep 추가
6c6e22b - config_set 주석 처리
...
ae3289b - itsdangerous 의존성 추가
```

**교훈:**
- 단계적 활성화 (incremental activation)가 중요
- 하지만 근본 원인을 찾지 못하면 반복

### 11.2 backup-before-reset-20260118-124339 브랜치 (가장 많은 시도)

**주요 증상:**
- 400 Bad Request 에러 발생
- Startup hang (시작 단계에서 멈춤)
- Redis hang 반복 발생

**발견된 문제들:**

**문제 1: 400 Error - asyncpg + PgBouncer 충돌**
- DuplicatePreparedStatementError의 변종
- 일부 쿼리는 성공, 일부는 400 에러
- 불규칙적 패턴
- 해결 시도:
  - `DEALLOCATE ALL` 실행 (연결 시점)
  - PORT 5432로 강제 전환 (Session Mode)
- 결과: 5432로 전환 시 해결, 하지만 임시방편

**문제 2: Redis PubSub CPU Spin/Hang**
- Pub/Sub 리스너가 CPU를 계속 사용하며 멈춤
- Busy-wait 루프 의심
- 메시지는 없지만 계속 polling
- 해결 시도: Redis PubSub 완전 비활성화
- 결과: 애플리케이션 시작 성공, 기능 저하

**문제 3: Reservation Notification Worker Hang**
- Redis lock 획득 시 hang
- 또는 database 쿼리 시 hang
- 해결 시도: Worker 비활성화
- 결과: 시스템 부팅 성공, 예약 알림 기능 상실

**문제 4: Slack Notification Blocking**
- startup/shutdown 시 Slack API 호출이 block
- timeout 설정했지만 무시됨
- Exception handler 내부에서도 blocking
- 해결 시도:
  - exception block에서 제거
  - startup에서 비활성화
- 결과: startup은 성공, 모니터링 기능 상실

**문제 5: RedisTimerListener Infinite Hang**
- `await redis_timer_listener.connect()` 무한 대기
- timeout 래핑 시도했지만 효과 없음
- Redis 자체는 정상 (ping 성공)
- 해결 시도:
  - RedisTimerListener 완전 비활성화
  - APScheduler fallback 활성화
- 결과: 시스템 동작, 정확도 저하 (1분 간격)

**문제 6: uvloop Hang on NAS**
- uvloop 사용 시 특정 지점에서 멈춤
- asyncio loop로 전환 시 개선
- NAS 환경의 특수성 (낮은 CPU, 특수 커널)
- 해결 시도: `--loop asyncio` 강제 사용
- 결과: hang 빈도 감소, 완전 해결 안됨

**문제 7: PgBouncer/Transaction Mode Init_DB Hang**
- 데이터베이스 초기화 쿼리가 hang
- Metadata 조회 시 prepared statement 충돌 의심
- 해결 시도: PgBouncer 사용 시 init_db 건너뛰기
- 결과: startup 성공, 테이블 생성 수동 필요

**문제 8: Lazy Engine Initialization 시도**
- Fork 후 engine 초기화 문제 해결 시도
- Workers가 각자 engine 생성하도록
- 해결 시도: Lazy initialization 패턴
- 결과: 다른 import 문제 발생

**문제 9: Invalid prepared_statement_cache_size**
- SQLAlchemy + asyncpg가 이 파라미터 인식 못함
- 공식 문서와 실제 구현 불일치
- 해결 시도: 파라미터 제거
- 결과: 다른 에러 노출

**문제 10: Worker=1 강제 설정**
- .env에서 WORKERS=2 설정
- 하지만 start-nas.sh에서 강제로 1로 재정의
- 혼란 발생
- 해결 시도: .env 파일만 수정
- 결과: 여전히 오버라이드됨

**커밋 히스토리 분석:**
```
7310941 - DB port 5432 강제 (Session Mode)
479de8b - DEALLOCATE ALL 시도
9627377 - "yeah fuck yeah" (좌절감 표현)
5a02c43 - Redis PubSub 비활성화
448a74e - APScheduler fallback 추가
28e62bc - Reservation worker 비활성화
932dd71 - Slack notification 제거
9694d52 - RedisTimerListener 비활성화
900ee0a - Redis connect timeout 추가
...
bbdc8f0 - SyntaxError 수정 (orphaned except)
```

**교훈:**
- 기능을 하나씩 비활성화하며 원인 찾기 시도
- 하지만 근본 원인은 PgBouncer 호환성 문제
- 비활성화로는 근본 해결 불가

### 11.3 backup-safe-60ce57b 브랜치 (안정 버전)

**상태:**
- 비교적 안정적인 상태
- 주요 기능 작동 중

**적용된 해결책들:**

**해결 1: PgBouncer Handling 로직**
- `_using_pgbouncer()` 함수로 감지
- `_get_connect_args()` 함수로 설정
- statement_cache_size=0 설정
- 상태: 로직은 올바름, 실제 적용은 불완전

**해결 2: Log Alerter Debounce**
- 중복 알림 방지
- 임계값 설정
- 상태: 정상 작동

**해결 3: Timer Starting Bug 수정**
- Break session으로 시작하는 버그
- UI cleanup
- 상태: 정상 작동

**해결 4: 한국어 로컬라이징 복구**
- 배포 중 손실된 한글 복구
- Notification 메시지 한글화
- 상태: 정상 작동

**해결 5: Master-Control Architecture**
- Agent는 Mac에서만 실행
- NAS는 순수 서버 역할
- 상태: 정상 작동

**커밋 히스토리:**
```
60ce57b - PgBouncer 처리 로직 강화
96bad18 - Log alerter debounce
f86ed2d - Prepared statements 비활성화 (시도)
...
```

**교훈:**
- 이 브랜치는 "작동하는" 상태
- 하지만 임시방편 다수 포함
- 근본 해결은 아님

### 11.4 패턴 분석 및 공통 문제점

**반복되는 문제 패턴:**

1. **PgBouncer Transaction Mode 충돌**
   - 모든 브랜치에서 공통
   - 다양한 형태로 나타남 (400, 502, hang)
   - 근본 원인은 동일

2. **Redis 관련 Hang/Blocking**
   - Redis Timer Listener
   - Redis Pub/Sub
   - Redis Lock 획득
   - 실제 원인: 비동기 처리 + NAS 환경

3. **Slack Notification Blocking**
   - 모든 브랜치에서 발생
   - Timeout이 작동하지 않음
   - Exception handler에서도 blocking

4. **Worker Fork 문제**
   - DB connection sharing
   - Engine initialization timing
   - Prepared statement 충돌

5. **NAS 환경의 특수성**
   - uvloop 불안정
   - CPU 성능 제한
   - 네트워크 지연
   - 권한 문제

**누적된 기술 부채:**

1. **비활성화된 기능들**
   - Redis Pub/Sub
   - Redis Timer Listener
   - Reservation Notification Worker
   - Slack Notification (부분)

2. **임시방편들**
   - Worker=1 강제
   - Port 5432 사용 (Session Mode)
   - APScheduler fallback
   - config_set 건너뛰기

3. **미해결 근본 원인**
   - SQLAlchemy + asyncpg + PgBouncer
   - Redis async operations on NAS
   - Slack API blocking behavior

**브랜치 간 진화 과정:**

```
backup-safe (안정)
    ↓
    문제 발견 및 수정 시도
    ↓
backup-gemini-disaster (최악)
    ↓
    대규모 수정 및 기능 비활성화
    ↓
backup-before-reset (많은 시도)
    ↓
    모든 임시방편 적용
    ↓
main (현재) - 근본 원인 분석 중
```

**각 브랜치의 접근법:**

| 브랜치 | 접근법 | 결과 |
|--------|--------|------|
| backup-safe | 점진적 개선 | 부분 성공 |
| gemini-disaster | 공격적 수정 | 실패 |
| before-reset | 방어적 비활성화 | 임시 성공 |
| main (현재) | 근본 원인 규명 | 진행 중 |

### 11.5 이전 경험에서 얻은 교훈

**DO (해야 할 것):**

1. **단계적 디버깅**
   - 한 번에 하나씩 변경
   - 각 변경 후 철저한 테스트
   - 롤백 지점 명확히

2. **근본 원인 추적**
   - 증상 치료가 아닌 원인 제거
   - 로그 분석 철저히
   - 스택 트레이스 완전 이해

3. **환경별 테스트**
   - 개발 환경과 프로덕션 환경 차이 인지
   - NAS 특수성 고려
   - 로컬에서 재현 시도

4. **문서화**
   - 시도한 모든 것 기록
   - 실패도 가치 있음
   - 패턴 발견에 도움

**DON'T (하지 말아야 할 것):**

1. **무분별한 기능 비활성화**
   - 증상만 숨김
   - 근본 해결 아님
   - 기술 부채 누적

2. **여러 변경 동시 적용**
   - 어떤 것이 효과 있는지 모름
   - 롤백 어려움
   - 디버깅 복잡도 증가

3. **임시방편에 의존**
   - Worker=1은 해결책 아님
   - Port 5432는 스케일링 불가
   - 언젠가 문제 재발

4. **좌절 후 포기**
   - "yeah fuck yeah" 같은 커밋 메시지
   - 체계적 접근 중단
   - 문제 더 악화

**최종 결론:**

이전 브랜치들의 경험을 통해 명확해진 것:

1. **PgBouncer Transaction Mode + SQLAlchemy + asyncpg는 근본적으로 호환되지 않음**
2. **임시방편으로 버틸 수는 있지만 언젠가 한계에 도달**
3. **NAS 환경의 특수성 (낮은 성능, uvloop 불안정)도 고려 필요**
4. **Redis async operations도 NAS에서 불안정**
5. **기술 스택 선택이 얼마나 중요한지 절실히 깨달음**

이 모든 경험이 현재의 근본 원인 분석으로 이어졌고, 이제는 **임시방편이 아닌 진짜 해결책**을 찾아야 할 시점입니다.

---

**작성일**: 2026년 1월 18일
**작성자**: Claude Code (AI Assistant)
**검토 필요**: Backend Team Lead
**다음 리뷰**: 해결책 적용 후 2주 내
