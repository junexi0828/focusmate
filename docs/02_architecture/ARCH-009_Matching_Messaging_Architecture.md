# ARCH-009: 매칭 시스템 메시징 아키텍처

## 📋 문서 정보

- **문서 번호**: ARCH-009
- **작성일**: 2025-12-12
- **버전**: 1.0
- **관련 문서**: REQ-002, ARCH-007, ARCH-008

## 🎯 개요

매칭 시스템 Phase 3의 메시징 시스템 구현을 위한 아키텍처 설계 문서입니다.
보편적인 IT 기업의 대규모 메시징 시스템 방법론을 기반으로, 현재 시스템 규모에 맞는 단계적 확장 전략을 제시합니다.

## 🏗️ 메시징 시스템 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React)                         │
│  - WebSocket Client (실시간 메시지 수신)                      │
│  - REST API Client (메시지 전송, 히스토리 조회)                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              Backend API (FastAPI)                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Message API Layer                                    │  │
│  │  - POST /matching/chats/{room_id}/messages          │  │
│  │  - GET  /matching/chats/{room_id}/messages          │  │
│  │  - POST /matching/chats/{room_id}/read              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  WebSocket Handler                                    │  │
│  │  - ws://api/matching/chats/{room_id}                 │  │
│  │  - 실시간 메시지 브로드캐스트                          │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
         ↓                    ↓                    ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  PostgreSQL  │    │    Redis      │    │  WebSocket   │
│  (영구 저장)  │    │  (Pub/Sub +  │    │  Manager     │
│              │    │   캐싱)        │    │              │
└──────────────┘    └──────────────┘    └──────────────┘
```

## 📊 메시징 방법론 비교

### 보편적인 IT 기업의 메시징 아키텍처 패턴

#### 1. 소규모~중규모 (현재 단계 추정)

**스택**: PostgreSQL + Redis Pub/Sub + WebSocket

**특징**:

- ✅ 간단한 아키텍처, 빠른 구현
- ✅ PostgreSQL로 메시지 영구 저장
- ✅ Redis Pub/Sub로 실시간 브로드캐스트
- ✅ WebSocket으로 클라이언트 전달
- ✅ 수평 확장 가능 (Stateless API)

**적용 사례**:

- Slack (초기 단계)
- Discord (초기 단계)
- 대부분의 스타트업

**처리 용량**:

- 동시 사용자: 1,000 ~ 10,000명
- 메시지 처리량: 1,000 ~ 10,000 msg/sec
- 메시지방: 100 ~ 1,000개

#### 2. 중규모~대규모

**스택**: PostgreSQL + Message Queue (RabbitMQ/Redis Streams) + WebSocket

**특징**:

- ✅ 메시지 큐로 비동기 처리
- ✅ 부하 분산 및 재시도 로직
- ✅ 메시지 순서 보장
- ✅ 배치 처리 가능

**적용 사례**:

- Slack (성장 단계)
- Microsoft Teams (일부 기능)
- 중견 기업 메신저

**처리 용량**:

- 동시 사용자: 10,000 ~ 100,000명
- 메시지 처리량: 10,000 ~ 100,000 msg/sec
- 메시지방: 1,000 ~ 10,000개

#### 3. 대규모

**스택**: Kafka + PostgreSQL + Redis + WebSocket

**특징**:

- ✅ 높은 처리량 (수백만 msg/sec)
- ✅ 분산 시스템
- ✅ 메시지 스트리밍 및 이벤트 소싱
- ✅ 복잡한 운영 및 인프라 비용

**적용 사례**:

- WhatsApp
- Telegram
- Facebook Messenger
- 카카오톡

**처리 용량**:

- 동시 사용자: 100,000명 이상
- 메시지 처리량: 100,000+ msg/sec
- 메시지방: 10,000개 이상

## 🎯 권장 아키텍처: PostgreSQL + Redis Pub/Sub + WebSocket

### 선택 이유

1. **현재 시스템 규모에 적합**

   - 매칭 시스템은 그룹 채팅 (2~16명)
   - 예상 동시 사용자: 수백 ~ 수천 명
   - PostgreSQL + Redis로 충분

2. **확장성**

   - Stateless API 서버 수평 확장 가능
   - Redis Pub/Sub로 서버 간 메시지 동기화
   - 필요 시 Kafka로 마이그레이션 가능

3. **운영 복잡도**

   - Kafka는 운영 복잡도가 높음
   - Redis는 이미 인프라에 포함됨
   - 빠른 개발 및 배포 가능

4. **비용 효율성**
   - 추가 인프라 비용 최소화
   - 개발 시간 단축

### 아키텍처 상세

```
┌─────────────────────────────────────────────────────────────┐
│                    메시지 전송 흐름                           │
└─────────────────────────────────────────────────────────────┘

1. 클라이언트 → REST API
   POST /matching/chats/{room_id}/messages
   {
     "content": "안녕하세요!",
     "message_type": "text"
   }

2. API 서버
   ├─ 메시지 검증 (권한, 길이 등)
   ├─ PostgreSQL에 메시지 저장
   │  └─ matching_messages 테이블
   └─ Redis Pub/Sub로 발행
      └─ 채널: matching:chat:{room_id}

3. Redis Pub/Sub
   └─ 모든 API 서버 인스턴스가 구독
      └─ 메시지 수신 시 WebSocket으로 브로드캐스트

4. WebSocket Manager
   └─ 해당 room_id의 모든 연결된 클라이언트에 전송

5. 클라이언트
   └─ 실시간 메시지 수신
```

## 🔄 메시지 처리 플로우

### 1. 메시지 전송

```python
# 1. API 엔드포인트에서 메시지 수신
@router.post("/matching/chats/{room_id}/messages")
async def send_message(
    room_id: str,
    data: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    redis: Redis = Depends(get_redis),
):
    # 2. 권한 검증 (방 멤버 확인)
    await verify_room_member(room_id, current_user.id, db)

    # 3. 메시지 저장 (PostgreSQL)
    message = await message_repo.create(
        Message(
            id=generate_uuid(),
            room_id=room_id,
            sender_id=current_user.id,
            content=data.content,
            message_type=data.message_type,
        )
    )

    # 4. Redis Pub/Sub로 발행
    await redis.publish(
        f"matching:chat:{room_id}",
        json.dumps({
            "type": "new_message",
            "message": message.dict(),
        })
    )

    # 5. 응답 반환
    return MessageResponse.from_orm(message)
```

### 2. 실시간 메시지 수신

```python
# Redis Pub/Sub 구독자 (백그라운드 태스크)
async def subscribe_to_room_messages(room_id: str, redis: Redis):
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"matching:chat:{room_id}")

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])

            # WebSocket으로 브로드캐스트
            await connection_manager.broadcast_to_room(
                data,
                room_id
            )
```

### 3. WebSocket 연결

```python
@router.websocket("/ws/matching/chats/{room_id}")
async def websocket_chat(
    websocket: WebSocket,
    room_id: str,
    token: str = Query(...),
):
    # 1. 인증
    user = await verify_websocket_token(token)

    # 2. 권한 확인
    await verify_room_member(room_id, user.id, db)

    # 3. WebSocket 연결
    await connection_manager.connect(websocket, room_id, user.id)

    # 4. Redis 구독 시작 (해당 서버 인스턴스)
    asyncio.create_task(
        subscribe_to_room_messages(room_id, redis)
    )

    try:
        while True:
            # 클라이언트 메시지 수신 (타이핑 표시 등)
            data = await websocket.receive_json()
            await handle_client_message(room_id, user.id, data)
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket, room_id, user.id)
```

## 💾 데이터 저장 전략

### PostgreSQL (영구 저장)

**테이블**: `matching_messages`

```sql
CREATE TABLE matching_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES matching_chat_rooms(room_id) ON DELETE CASCADE,
    sender_id VARCHAR(36) REFERENCES "user"(id) ON DELETE CASCADE,

    -- 메시지 내용
    message_type VARCHAR(20) DEFAULT 'text', -- text, image, system
    content TEXT NOT NULL,

    -- 첨부 파일
    attachments TEXT[],

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

-- 인덱스
CREATE INDEX idx_matching_messages_room ON matching_messages(room_id);
CREATE INDEX idx_matching_messages_created ON matching_messages(created_at DESC);
CREATE INDEX idx_matching_messages_sender ON matching_messages(sender_id);
```

**읽기 전략**:

- 최근 메시지 조회: 인덱스 활용 (created_at DESC)
- 페이지네이션: Cursor-based pagination (성능 최적화)
- 읽음 표시: 별도 테이블 또는 JSONB 필드

### Redis (캐싱)

**캐싱 전략**:

1. **최근 메시지 캐싱**

   ```
   Key: matching:chat:{room_id}:messages:recent
   Value: JSON array of last 50 messages
   TTL: 5분
   ```

2. **읽음 표시 캐싱**

   ```
   Key: matching:chat:{room_id}:read:{user_id}
   Value: last_read_message_id
   TTL: 1시간
   ```

3. **메시지방 메타데이터**
   ```
   Key: matching:chat:{room_id}:meta
   Value: JSON (member_count, last_message_at, etc.)
   TTL: 10분
   ```

## 🔔 읽음 표시 처리

### 방법 1: PostgreSQL 기반 (권장)

```sql
-- 읽음 표시 테이블
CREATE TABLE matching_message_reads (
    read_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    message_id UUID REFERENCES matching_messages(message_id) ON DELETE CASCADE,
    user_id VARCHAR(36) REFERENCES "user"(id) ON DELETE CASCADE,
    read_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(message_id, user_id)
);

CREATE INDEX idx_message_reads_user ON matching_message_reads(user_id);
CREATE INDEX idx_message_reads_message ON matching_message_reads(message_id);
```

**장점**:

- 정확한 읽음 상태 추적
- 히스토리 조회 가능
- 데이터 일관성 보장

**단점**:

- 대량 메시지 시 성능 이슈 가능
- 읽음 표시 업데이트 비용

### 방법 2: Redis 기반 (고성능)

```python
# 읽음 표시 저장
await redis.set(
    f"matching:chat:{room_id}:read:{user_id}",
    last_message_id,
    ex=86400  # 24시간
)

# 읽음 표시 조회
last_read = await redis.get(f"matching:chat:{room_id}:read:{user_id}")
```

**장점**:

- 빠른 읽기/쓰기
- 실시간 업데이트

**단점**:

- 영구 저장 필요 시 PostgreSQL 동기화 필요
- Redis 장애 시 데이터 손실 가능

### 하이브리드 접근 (권장)

```python
# 읽음 표시 업데이트
async def mark_as_read(room_id: str, user_id: str, message_id: str):
    # 1. Redis에 즉시 업데이트 (실시간)
    await redis.set(
        f"matching:chat:{room_id}:read:{user_id}",
        message_id,
        ex=86400
    )

    # 2. PostgreSQL에 비동기 저장 (영구 저장)
    asyncio.create_task(
        save_read_status_to_db(room_id, user_id, message_id)
    )
```

## 📡 실시간 알림 시스템

### 알림 채널

1. **In-App 알림** (WebSocket)

   - 실시간 메시지 수신
   - 매칭 제안 알림
   - 읽음 표시 업데이트

2. **Push 알림** (FCM/APNS)

   - 앱이 백그라운드일 때
   - 중요 알림만 (매칭 성사, 새 메시지)

3. **이메일 알림** (선택적)
   - 매칭 성사
   - 중요 이벤트만

### 알림 우선순위

```python
class NotificationPriority:
    HIGH = "high"      # 매칭 성사, 즉시 전송
    MEDIUM = "medium"  # 새 메시지, 배치 전송
    LOW = "low"        # 읽음 표시, 실시간만
```

## 🔐 보안 고려사항

### 메시지 암호화

1. **전송 중 암호화**

   - HTTPS/WSS 사용
   - TLS 1.3 이상

2. **저장 시 암호화** (선택적)
   - 민감 정보만 암호화
   - PostgreSQL 암호화 컬럼 또는 애플리케이션 레벨

### 접근 제어

```python
# 메시지 전송 권한 검증
async def verify_room_member(room_id: str, user_id: str):
    member = await db.query(MatchingChatMember).filter(
        MatchingChatMember.room_id == room_id,
        MatchingChatMember.user_id == user_id,
        MatchingChatMember.is_active == True
    ).first()

    if not member:
        raise ForbiddenException("방 멤버가 아닙니다")
```

## 📈 성능 최적화

### 1. 메시지 조회 최적화

```python
# Cursor-based Pagination
async def get_messages(
    room_id: str,
    limit: int = 50,
    before_message_id: str = None
):
    query = select(MatchingMessage).where(
        MatchingMessage.room_id == room_id
    ).order_by(MatchingMessage.created_at.desc())

    if before_message_id:
        before_message = await get_message(before_message_id)
        query = query.where(
            MatchingMessage.created_at < before_message.created_at
        )

    return await db.execute(query.limit(limit))
```

### 2. 배치 처리

```python
# 읽음 표시 배치 업데이트
async def batch_mark_as_read(
    room_id: str,
    user_id: str,
    message_ids: list[str]
):
    # 1. Redis에 즉시 업데이트
    last_message_id = max(message_ids)
    await redis.set(f"matching:chat:{room_id}:read:{user_id}", last_message_id)

    # 2. PostgreSQL에 배치 저장
    await db.execute(
        insert(MatchingMessageRead).values([
            {"message_id": mid, "user_id": user_id}
            for mid in message_ids
        ]).on_conflict_do_nothing()
    )
```

### 3. 연결 풀링

```python
# PostgreSQL 연결 풀
engine = create_async_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True
)

# Redis 연결 풀
redis = await aioredis.from_url(
    REDIS_URL,
    max_connections=50,
    decode_responses=True
)
```

## 🚀 확장 전략

### Phase 1: 현재 (PostgreSQL + Redis Pub/Sub)

**처리 용량**:

- 동시 사용자: 1,000명
- 메시지 처리량: 1,000 msg/sec
- 메시지방: 100개

**구현**:

- ✅ PostgreSQL 메시지 저장
- ✅ Redis Pub/Sub 실시간 브로드캐스트
- ✅ WebSocket 클라이언트 전달

### Phase 2: 성장 (Redis Streams 추가)

**처리 용량**:

- 동시 사용자: 10,000명
- 메시지 처리량: 10,000 msg/sec
- 메시지방: 1,000개

**추가 구현**:

- Redis Streams로 메시지 큐잉
- Consumer 그룹으로 부하 분산
- 메시지 재시도 로직

```python
# Redis Streams 사용
await redis.xadd(
    f"matching:chat:{room_id}:stream",
    {
        "message_id": message.id,
        "sender_id": message.sender_id,
        "content": message.content,
    }
)
```

### Phase 3: 대규모 (Kafka 도입)

**처리 용량**:

- 동시 사용자: 100,000명 이상
- 메시지 처리량: 100,000+ msg/sec
- 메시지방: 10,000개 이상

**마이그레이션**:

- Kafka로 메시지 스트리밍
- PostgreSQL은 최종 저장소
- Redis는 캐싱만 담당

```python
# Kafka Producer
from kafka import KafkaProducer

producer = KafkaProducer(
    bootstrap_servers=['kafka:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# 메시지 발행
producer.send(
    'matching-messages',
    {
        'room_id': room_id,
        'message': message.dict()
    }
)
```

## 📊 모니터링 및 관찰성

### 메트릭

1. **메시지 처리량**

   - 초당 메시지 수신/전송
   - 평균 응답 시간
   - 에러율

2. **WebSocket 연결**

   - 활성 연결 수
   - 연결/해제율
   - 평균 연결 지속 시간

3. **데이터베이스**
   - 쿼리 응답 시간
   - 연결 풀 사용률
   - 느린 쿼리

### 로깅

```python
# 구조화된 로깅
logger.info(
    "message_sent",
    extra={
        "room_id": room_id,
        "sender_id": sender_id,
        "message_id": message_id,
        "message_type": message_type,
    }
)
```

## 🧪 테스트 전략

### 단위 테스트

- 메시지 검증 로직
- 읽음 표시 업데이트
- 권한 검증

### 통합 테스트

- Redis Pub/Sub 메시지 전달
- WebSocket 브로드캐스트
- PostgreSQL 저장/조회

### 부하 테스트

- 동시 메시지 전송
- WebSocket 연결 수
- 메시지 조회 성능

## 📝 구현 체크리스트

### Phase 3 구현 항목

- [ ] **데이터베이스**

  - [ ] `matching_messages` 테이블 마이그레이션
  - [ ] `matching_message_reads` 테이블 (선택적)
  - [ ] 인덱스 최적화

- [ ] **Redis 설정**

  - [ ] Pub/Sub 채널 구조 설계
  - [ ] 캐싱 전략 구현
  - [ ] 연결 풀 설정

- [ ] **WebSocket**

  - [ ] 메시지방별 WebSocket 엔드포인트
  - [ ] 연결 관리 개선
  - [ ] 재연결 로직

- [ ] **API 엔드포인트**

  - [ ] POST /matching/chats/{room_id}/messages
  - [ ] GET /matching/chats/{room_id}/messages
  - [ ] POST /matching/chats/{room_id}/read

- [ ] **서비스 레이어**

  - [ ] 메시지 전송 서비스
  - [ ] 메시지 조회 서비스
  - [ ] 읽음 표시 서비스

- [ ] **실시간 처리**

  - [ ] Redis Pub/Sub 구독자
  - [ ] WebSocket 브로드캐스트
  - [ ] 타이핑 표시 (선택적)

- [ ] **알림**
  - [ ] In-App 알림
  - [ ] Push 알림 (FCM/APNS)
  - [ ] 알림 우선순위 처리

## 🎯 결론

**권장 아키텍처**: PostgreSQL + Redis Pub/Sub + WebSocket

이 아키텍처는:

1. ✅ 현재 시스템 규모에 적합
2. ✅ 빠른 구현 가능
3. ✅ 수평 확장 가능
4. ✅ 필요 시 Kafka로 마이그레이션 가능

**다음 단계**:

1. Phase 3 구현 시작 (PostgreSQL + Redis Pub/Sub)
2. 성능 모니터링 및 최적화
3. 사용자 증가 시 Redis Streams 또는 Kafka 검토

---

**문서 승인**: 대기 중
**다음 단계**: Phase 3 구현 시작
