# FocusMate 미들웨어 가이드

이 문서는 FocusMate 백엔드에서 사용되는 보안 및 성능 미들웨어에 대한 상세 가이드를 제공합니다.

## 목차

1. [Rate Limiting 미들웨어](#1-rate-limiting-미들웨어)
2. [Trusted Host 미들웨어](#2-trusted-host-미들웨어)
3. [GZip 미들웨어](#3-gzip-미들웨어)
4. [Request ID/Logging 미들웨어](#4-request-idlogging-미들웨어)
5. [미들웨어 실행 순서](#미들웨어-실행-순서)
6. [설정 및 환경 변수](#설정-및-환경-변수)

---

## 1. Rate Limiting 미들웨어

### 개요

`RateLimitMiddleware`는 Redis를 사용한 분산 Rate Limiting을 제공하여 brute force 공격 및 API 남용을 방지합니다.

### 주요 기능

- **Redis 기반 분산 Rate Limiting**: 여러 서버 인스턴스 간 공유 가능
- **엔드포인트별 차등 제한**: 인증 엔드포인트에 더 엄격한 제한 적용
- **IP 및 사용자 기반 추적**: 인증된 사용자는 사용자 ID로, 비인증 사용자는 IP 주소로 추적
- **Sliding Window 알고리즘**: 정확한 시간 윈도우 기반 제한

### 구현 위치

- **파일**: `backend/app/api/middleware/rate_limit.py`
- **클래스**: `RateLimitMiddleware`

### 설정된 제한

#### 기본 제한
- **일반 엔드포인트**: 60 requests/minute
- **Burst Limit**: 120 requests/minute (기본 제한의 2배)

#### 엄격한 제한 (인증 관련)
- `/api/v1/auth/login`: **5 requests/minute**
- `/api/v1/auth/register`: **3 requests/minute**
- `/api/v1/auth/password-reset/request`: **3 requests/minute**
- `/api/v1/auth/password-reset/complete`: **3 requests/minute**

### 제외된 경로

다음 경로는 Rate Limiting에서 제외됩니다:
- `/health`
- `/docs`
- `/redoc`
- `/openapi.json`

### 사용 예시

```python
# main.py에서 자동으로 적용됨
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=60,
    exempt_paths=["/health", "/docs", "/redoc", "/openapi.json"],
)
```

### 응답 헤더

Rate Limiting 정보는 다음 헤더로 제공됩니다:

- `X-RateLimit-Limit`: 허용된 최대 요청 수
- `X-RateLimit-Remaining`: 남은 요청 수
- `X-RateLimit-Reset`: 제한이 리셋되는 Unix 타임스탬프
- `Retry-After`: 재시도 가능 시간 (초)

### Rate Limit 초과 시 응답

```json
{
  "error": "Rate limit exceeded",
  "message": "Too many requests. Please try again in 45 seconds.",
  "limit": 5,
  "remaining": 0,
  "reset": 1734876543
}
```

**HTTP 상태 코드**: `429 Too Many Requests`

### Redis 연결 실패 시 동작

Redis가 사용 불가능한 경우, 미들웨어는 요청을 허용합니다 (fail-open). 이는 Redis 장애 시에도 서비스가 계속 작동하도록 보장합니다.

### 보안 고려사항

1. **X-Forwarded-For 헤더 처리**: 프록시 뒤에서 실행 시 클라이언트 IP를 올바르게 식별
2. **사용자 인증 기반 추적**: 인증된 사용자는 IP 대신 사용자 ID로 추적되어 더 정확한 제한 가능
3. **엄격한 인증 엔드포인트 제한**: 로그인, 회원가입, 비밀번호 리셋에 더 엄격한 제한 적용

---

## 2. Trusted Host 미들웨어

### 개요

`TrustedHostMiddleware`는 Host 헤더 공격을 방지하기 위해 허용된 호스트만 허용합니다.

### 주요 기능

- **Host 헤더 검증**: 허용되지 않은 Host 헤더를 가진 요청 차단
- **프로덕션 환경에서만 활성화**: 개발 환경에서는 비활성화
- **설정 가능한 허용 호스트 목록**: 환경 변수로 관리

### 구현 위치

- **FastAPI 내장**: `fastapi.middleware.trustedhost.TrustedHostMiddleware`
- **설정**: `backend/app/core/config.py`의 `TRUSTED_HOSTS`

### 설정

```python
# main.py
if not settings.is_development:
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.TRUSTED_HOSTS,
    )
```

### 환경 변수

```env
# .env 파일
TRUSTED_HOSTS=localhost,127.0.0.1,api.focusmate.com,www.focusmate.com
```

### 기본값

- **개발 환경**: `localhost,127.0.0.1,0.0.0.0`
- **프로덕션 환경**: 환경 변수에서 지정된 호스트만 허용

### 허용되지 않은 Host 헤더 시 응답

**HTTP 상태 코드**: `400 Bad Request`

```json
{
  "detail": "Invalid host header"
}
```

### 보안 고려사항

1. **프로덕션 필수**: 프로덕션 환경에서는 반드시 활성화되어야 함
2. **모든 도메인 명시**: 프론트엔드, API, CDN 등 모든 허용된 도메인을 명시
3. **와일드카드 사용 금지**: 프로덕션에서는 `*` 사용 금지

---

## 3. GZip 미들웨어

### 개요

`GZipMiddleware`는 API 응답을 압축하여 대역폭을 절감하고 성능을 개선합니다.

### 주요 기능

- **자동 응답 압축**: 클라이언트가 `Accept-Encoding: gzip` 헤더를 보낼 때 자동 압축
- **최소 크기 제한**: 작은 응답은 압축하지 않음 (성능 최적화)
- **압축 레벨 조정 가능**: 1-9 레벨 (기본값: 6)

### 구현 위치

- **FastAPI 내장**: `fastapi.middleware.gzip.GZipMiddleware`
- **설정**: `backend/app/main.py`

### 설정

```python
# main.py
app.add_middleware(
    GZipMiddleware,
    minimum_size=1000,  # 1KB 이상만 압축
    compresslevel=6,    # 압축 레벨 (1-9)
)
```

### 압축 조건

1. **최소 크기**: 응답이 1KB 이상일 때만 압축
2. **클라이언트 지원**: 클라이언트가 `Accept-Encoding: gzip` 헤더를 보낼 때
3. **콘텐츠 타입**: 텍스트 기반 응답에 적합 (JSON, HTML, CSS, JS 등)

### 성능 영향

- **대역폭 절감**: 일반적으로 60-80% 대역폭 절감
- **CPU 사용량 증가**: 압축/해제에 CPU 사용
- **응답 시간**: 작은 응답은 압축 오버헤드가 더 클 수 있음

### 압축 레벨 가이드

- **1-3**: 빠른 압축, 낮은 압축률
- **4-6**: 균형잡힌 설정 (권장)
- **7-9**: 높은 압축률, 느린 압축

---

## 4. Request ID/Logging 미들웨어

### 개요

`RequestLoggingMiddleware`는 각 요청에 고유 ID를 부여하고 요청/응답을 로깅하여 디버깅과 모니터링을 용이하게 합니다.

### 주요 기능

- **고유 Request ID 생성**: 각 요청에 UUID 기반 고유 ID 부여
- **요청/응답 로깅**: 요청 시작, 완료, 에러 로깅
- **처리 시간 측정**: 각 요청의 처리 시간 추적
- **클라이언트 Request ID 지원**: 클라이언트가 제공한 Request ID 사용 가능

### 구현 위치

- **파일**: `backend/app/api/middleware/request_logging.py`
- **클래스**: `RequestLoggingMiddleware`

### 설정

```python
# main.py
app.add_middleware(
    RequestLoggingMiddleware,
    log_request_body=False,   # 보안을 위해 기본값 False
    log_response_body=False,  # 성능을 위해 기본값 False
    exclude_paths=["/health", "/docs", "/redoc", "/openapi.json"],
)
```

### Request ID 사용

#### 엔드포인트에서 Request ID 가져오기

```python
from fastapi import Request
from app.api.middleware.request_logging import get_request_id

@router.get("/example")
async def example(request: Request):
    request_id = get_request_id(request)
    logger.info(f"Processing request {request_id}")
    return {"request_id": request_id}
```

#### 클라이언트가 Request ID 제공

클라이언트는 `X-Request-ID` 헤더로 Request ID를 제공할 수 있습니다:

```bash
curl -H "X-Request-ID: my-custom-request-id" http://localhost:8000/api/v1/example
```

### 응답 헤더

- `X-Request-ID`: 요청의 고유 ID
- `X-Process-Time`: 요청 처리 시간 (초)

### 로그 형식

#### 요청 시작 로그

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "url": "http://localhost:8000/api/v1/auth/login",
  "path": "/api/v1/auth/login",
  "client_host": "127.0.0.1",
  "user_agent": "Mozilla/5.0..."
}
```

#### 요청 완료 로그

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/api/v1/auth/login",
  "status_code": 200,
  "duration": "0.123s"
}
```

#### 에러 로그

```json
{
  "request_id": "550e8400-e29b-41d4-a716-446655440000",
  "method": "POST",
  "path": "/api/v1/auth/login",
  "status_code": 500,
  "duration": "0.456s",
  "error": "Internal server error"
}
```

### 로그 레벨

- **INFO**: 정상 요청 (200-299)
- **WARNING**: 클라이언트 에러 (400-499)
- **ERROR**: 서버 에러 (500-599)

### 보안 고려사항

1. **Request Body 로깅**: 기본적으로 비활성화 (민감한 정보 포함 가능)
2. **Response Body 로깅**: 기본적으로 비활성화 (성능 및 보안)
3. **제외 경로**: Health check, 문서 경로는 로깅 제외

### 디버깅 모드

디버깅 시 Request/Response Body를 로깅하려면:

```python
app.add_middleware(
    RequestLoggingMiddleware,
    log_request_body=True,   # ⚠️ 보안 위험: 프로덕션에서 사용 금지
    log_response_body=True,  # ⚠️ 성능 영향: 프로덕션에서 사용 금지
)
```

---

## 미들웨어 실행 순서

미들웨어는 추가된 순서의 **역순**으로 실행됩니다. FocusMate의 미들웨어 실행 순서:

1. **RequestLoggingMiddleware** (가장 먼저 실행)
   - Request ID 생성
   - 요청 로깅 시작

2. **GZipMiddleware**
   - 응답 압축 (응답 시)

3. **TrustedHostMiddleware** (프로덕션만)
   - Host 헤더 검증

4. **RateLimitMiddleware**
   - Rate limit 확인
   - 제한 초과 시 요청 차단

5. **CORSMiddleware**
   - CORS 헤더 추가

6. **라우터/엔드포인트** 실행

7. **미들웨어 역순 실행** (응답 처리)

### 실행 순서 다이어그램

```
요청 → RequestLogging (시작)
     → GZip (압축 준비)
     → TrustedHost (검증)
     → RateLimit (제한 확인)
     → CORS (헤더 준비)
     → 엔드포인트 실행
     → CORS (헤더 추가)
     → RateLimit (헤더 추가)
     → TrustedHost (완료)
     → GZip (압축 적용)
     → RequestLogging (완료 로깅) → 응답
```

---

## 설정 및 환경 변수

### Rate Limiting 설정

```env
# .env 파일
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_BURST=10
REDIS_URL=redis://localhost:6379/0
```

### Trusted Hosts 설정

```env
# .env 파일
TRUSTED_HOSTS=localhost,127.0.0.1,api.focusmate.com
```

### 로깅 설정

```env
# .env 파일
APP_LOG_LEVEL=info  # debug, info, warning, error, critical
```

---

## 모니터링 및 디버깅

### Rate Limit 모니터링

Rate Limit 상태는 응답 헤더로 확인 가능:

```bash
curl -I http://localhost:8000/api/v1/auth/login
```

응답 헤더:
```
X-RateLimit-Limit: 5
X-RateLimit-Remaining: 4
X-RateLimit-Reset: 1734876543
```

### Request ID로 로그 추적

Request ID를 사용하여 특정 요청의 모든 로그를 추적:

```bash
# 로그에서 Request ID 검색
grep "550e8400-e29b-41d4-a716-446655440000" /tmp/focusmate-backend.log
```

### Redis Rate Limit 키 확인

```bash
# Redis CLI에서 Rate Limit 키 확인
redis-cli
> KEYS rate_limit:*
> ZRANGE rate_limit:ip:127.0.0.1:/api/v1/auth/login 0 -1
```

---

## 성능 고려사항

### Rate Limiting

- **Redis 연결 풀링**: Redis 연결 재사용으로 성능 최적화
- **파이프라인 사용**: 여러 Redis 명령을 한 번에 실행
- **Fail-Open 정책**: Redis 장애 시 서비스 중단 방지

### GZip 압축

- **최소 크기 제한**: 작은 응답은 압축하지 않음 (오버헤드 방지)
- **압축 레벨 조정**: 성능과 압축률의 균형

### Request Logging

- **비동기 로깅**: 요청 처리에 영향 최소화
- **선택적 Body 로깅**: 기본적으로 비활성화 (성능 및 보안)

---

## 보안 모범 사례

1. **프로덕션 환경 설정**
   - Trusted Host 미들웨어 활성화
   - Rate Limiting 엄격한 제한 적용
   - Request Body 로깅 비활성화

2. **Rate Limiting**
   - 인증 엔드포인트에 더 엄격한 제한
   - Redis를 통한 분산 Rate Limiting 사용

3. **로깅**
   - 민감한 정보 로깅 금지
   - Request ID를 통한 추적 가능하도록 유지

4. **모니터링**
   - Rate Limit 초과 모니터링
   - 의심스러운 요청 패턴 감지

---

## 문제 해결

### Rate Limit이 작동하지 않음

1. Redis 연결 확인:
   ```bash
   redis-cli ping
   ```

2. 환경 변수 확인:
   ```bash
   echo $REDIS_URL
   ```

3. 로그 확인:
   ```bash
   tail -f /tmp/focusmate-backend.log | grep rate
   ```

### Trusted Host 에러 발생

1. 허용된 호스트 확인:
   ```env
   TRUSTED_HOSTS=your-domain.com,api.your-domain.com
   ```

2. 개발 환경에서는 비활성화:
   ```python
   # main.py에서 자동으로 개발 환경에서는 비활성화됨
   if not settings.is_development:
       app.add_middleware(TrustedHostMiddleware, ...)
   ```

### Request ID가 없음

Request ID는 자동으로 생성되며, `X-Request-ID` 헤더로 확인 가능합니다. 엔드포인트에서 사용하려면:

```python
from app.api.middleware.request_logging import get_request_id

request_id = get_request_id(request)
```

---

## 참고 자료

- [FastAPI Middleware 문서](https://fastapi.tiangolo.com/advanced/middleware/)
- [Redis Rate Limiting 패턴](https://redis.io/docs/manual/patterns/rate-limiting/)
- [OWASP API Security Top 10](https://owasp.org/www-project-api-security/)

---

**문서 버전**: 1.0.0  
**최종 업데이트**: 2025-01-22

