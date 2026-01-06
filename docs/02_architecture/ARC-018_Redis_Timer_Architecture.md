# ARC-018: Redis TTL Timer Architecture

**문서 ID**: ARC-018
**작성일**: 2026-01-07
**작성자**: System Architect
**상태**: Approved
**카테고리**: Architecture / Timer

---

## 1. 개요

### 1.1 목적
본 문서는 FocusMate의 타이머 시스템을 위한 **Redis TTL 기반 이벤트 구동(Event-Driven) 아키텍처**를 정의합니다. 기존의 데이터베이스 폴링(Polling) 방식(APScheduler)을 대체하여, 초 단위의 정확도와 서버 확장성을 확보하는 것을 목적으로 합니다.

### 1.2 핵심 원칙
1. **Event-Driven**: 타이머 만료는 Redis 키 만료 이벤트(`__keyevent@0__:expired`)에 의해 트리거됩니다.
2. **Precision**: Redis의 TTL 메커니즘을 사용하여 초 단위의 정확한 만료 시간을 보장합니다.
3. **Scalability**: 데이터베이스 폴링을 제거하여 DB 부하를 없애고, 다중 서버 환경에서도 중복 처리 없이 안전하게 확장 가능합니다.
4. **Reliability**: Redis 장애 시를 대비한 폴링 백업(선택적) 또는 안전 장치를 고려합니다.

---

## 2. 아키텍처 비교

### 2.1 기존 방식 (APScheduler Polling)
- **메커니즘**: 1분마다 DB에서 실행 중인 모든 타이머 조회 → 만료 여부 계산 → 종료 처리
- **단점**:
  - 오차 범위: 최대 1분 (지연 처리)
  - DB 부하: 매분 전체 테이블 조회 (N명 사용자 시 부하 증가)
  - 확장성 문제: 다중 서버 시 중복 처리 발생 (DB Lock 필요)

### 2.2 개선 방식 (Redis TTL Event-Driven)
- **메커니즘**: 타이머 시작 시 Redis에 TTL 설정 → 만료 시 Redis가 이벤트 발행 → 리스너가 즉시 종료 처리
- **장점**:
  - 정확도: 초 단위 정확성
  - DB 부하: Zero (이벤트 발생 시에만 해당 타이머 처리)
  - 확장성: Redis Pub/Sub은 다중 서버 환경에서도 이벤트 분배가 용이하며, Pub/Sub 특성상 중복 처리 방지가 더 수월함(단일 리스너 그룹 또는 멱등성 로직)

---

## 3. 시스템 아키텍처

### 3.1 아키텍처 다이어그램

```mermaid
graph TD
    User[사용자] -->|타이머 시작| API[FastAPI Server]

    subgraph "Timer Start Flow"
        API -->|1. 레코드 생성| DB[(PostgreSQL)]
        API -->|2. SETEX (Key+TTL)| Redis[(Redis)]
    end

    subgraph "Timer Expiry Flow"
        Redis -->|3. 만료 이벤트 (expired)| Listener[Redis Timer Listener]
        Listener -->|4. 타이머 종료 처리| DB
    end
```

### 3.2 핵심 컴포넌트

1. **Redis Timer Listener** (`redis_timer_listener.py`)
   - Redis Keyspace Notifications(`__keyevent@0__:expired`)를 구독
   - `timer:expire:{room_id}` 패턴의 키 만료 감지
   - 만료 시 `TimerService.complete_timer` 호출

2. **Timer Service** (`service.py`)
   - `start_timer`: DB 업데이트 후 `_set_redis_timer_ttl` 호출
   - `_set_redis_timer_ttl`: Redis에 만료 키 설정 (`SETEX`)

3. **Redis Configuration**
   - `notify-keyspace-events = Ex` (Expired events 활성화 필수)

---

## 4. 데이터 모델

### 4.1 Redis Key 구조

| Key | Value | TTL | 설명 |
|-----|-------|-----|------|
| `timer:expire:{room_id}` | JSON (`room_id`, `started_at`, `duration`) | `remaining_seconds` | 타이머 만료 트리거용 키 |

### 4.2 이벤트 페이로드

Redis 만료 이벤트(`expired`)는 메시지 본문으로 **만료된 키 이름**만 전달합니다.
- 채널: `__keyevent@0__:expired`
- 메시지: `timer:expire:123e4567-e89b-12d3...`

따라서 리스너는 키 이름에서 `room_id`를 파싱하여 DB 작업을 수행합니다.

---

## 5. 구현 상세

### 5.1 리스너 구현 (Python)

```python
class RedisTimerListener:
    async def listen(self):
        # 1. PubSub 연결 및 설정
        await self.redis.config_set('notify-keyspace-events', 'Ex')
        await self.pubsub.psubscribe('__keyevent@0__:expired')

        # 2. 이벤트 루프
        async for message in self.pubsub.listen():
            if message['type'] == 'pmessage':
                key = message['data']
                if key.startswith('timer:expire:'):
                    room_id = key.split(':')[-1]
                    await self._handle_timer_expiry(room_id)
```

### 5.2 타이머 시작 시 설정

```python
async def _set_redis_timer_ttl(self, room_id, duration):
    key = f"timer:expire:{room_id}"
    # 값은 디버깅용 메타데이터 (만료 시 사라짐)
    value = json.dumps({"room_id": room_id, "created_at": str(datetime.now())})
    await redis.setex(key, duration, value)
```

---

## 6. 운영 고려사항

### 6.1 신뢰성 및 장애 처리
- **Redis 재시작**: Redis는 인메모리이므로 재시작 시 TTL 키가 사라질 수 있습니다. (AOF/RDBPersistence 설정 권장)
- **리스너 재연결**: 네트워크 단절 시 자동 재연결 로직이 포함되어 있습니다.
- **백업 계획**: Redis 장애가 장기화될 경우, DB 기반 폴링(아카이브된 APScheduler)을 비상용으로 사용할 수 있습니다.

### 6.2 다중 서버 확장 (Horizontal Scaling)
서버가 여러 대로 늘어날 경우:
1. **단일 리스너 패턴**: 하나의 전용 워커 서버만 리스너를 실행
2. **경쟁 소비자 패턴**: 모든 서버가 리스닝하되, DB 트랜잭션 레벨에서 멱등성(Idempotency)을 보장하여 중복 종료 처리 방지 (`timer.status == RUNNING` 체크)

*현재 FocusMate는 2번 방식(DB 상태 체크를 통한 중복 방지)을 채택하고 있습니다.*

---

## 7. 관련 문서
- [ARC-013: 데이터베이스 아키텍처](./ARC-013_데이터베이스_아키텍처.md)
- [ARC-014: WebSocket 아키텍처](./ARC-014_WebSocket_아키텍처.md)
