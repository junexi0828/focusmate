# ARC-017: Enterprise Notification System Architecture

**문서 ID**: ARC-017
**작성일**: 2026-01-07
**작성자**: System Architect
**상태**: Design
**카테고리**: Architecture / Notification System

---

## 1. 개요

### 1.1 목적
본 문서는 FocusMate의 엔터프라이즈급 알림 시스템 아키텍처를 정의합니다. Slack, Discord, Instagram 등 IT 대기업의 알림 시스템 패턴을 따라 **이벤트 기반 + WebSocket 중심 + 오프라인 백필** 아키텍처를 구현합니다.

### 1.2 핵심 원칙
1. **Event-Driven**: 모든 알림은 서버 이벤트에서 발생
2. **WS-Centric**: 실시간 데이터는 WebSocket으로 전송
3. **Persistent**: 알림은 항상 DB에 저장
4. **Multi-Channel**: WS(온라인) + Email(오프라인)
5. **Backfill**: 재접속 시 놓친 알림 동기화

### 1.3 범위
- 메시지, 커뮤니티, 친구, 매칭, 예약, 랭킹 알림
- 실시간 전송 및 오프라인 처리
- 알림 그룹화 및 우선순위 관리

---

## 2. 시스템 아키텍처

### 2.1 전체 플로우

```
이벤트 발생 (예: 메시지 전송)
  ↓
1. 비즈니스 로직 실행 (메시지 저장)
  ↓
2. 알림 생성 (NotificationService.create_notification)
  ↓
3. DB 저장 (notification 레코드)
  ↓
4. 사용자 설정 확인 (notification_settings)
  ↓
5. 온라인 여부 확인
  ↓
6a. 온라인 → WS 전송 (즉시)
6b. 오프라인 → Email 전송 (비동기)
  ↓
7. 전송 상태 업데이트 (delivered_via_*)
```

### 2.2 컴포넌트 구조

```
┌─────────────────────────────────────────────────────┐
│                   Frontend Layer                     │
│  - NotificationBell (UI)                            │
│  - useNotificationBackfill (Hook)                   │
│  - WebSocket Connection                             │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│                  API Layer                           │
│  - /notifications/backfill (GET)                    │
│  - /notifications (GET, POST, PATCH)                │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│              Service Layer                           │
│  - NotificationService                              │
│    • create_notification()                          │
│    • deliver_notification()                         │
│    • get_notifications_since()                      │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│            Infrastructure Layer                      │
│  - NotificationRepository (DB)                      │
│  - NotificationWebSocketManager (WS)                │
│  - EmailService (SMTP)                              │
└─────────────────────────────────────────────────────┘
```

---

## 3. 알림 이벤트 맵핑

### 3.1 알림 타입 정의

| 기능 | 이벤트 | 알림 타입 | 수신자 | 우선순위 |
|------|--------|-----------|--------|----------|
| **메시지** | | | | |
| 새 메시지 | `message.sent` | `message` | 수신자 | HIGH |
| 새 대화 | `conversation.created` | `new_conversation` | 수신자 | HIGH |
| **커뮤니티** | | | | |
| 댓글 작성 | `post.commented` | `post_comment` | 게시글 작성자 | MEDIUM |
| 좋아요 | `post.liked` | `post_like` | 게시글 작성자 | LOW |
| 멘션 | `post.mentioned` | `mention` | 멘션된 사용자 | HIGH |
| **친구** | | | | |
| 친구 요청 | `friend.requested` | `friend_request` | 요청 받은 사용자 | MEDIUM |
| 요청 수락 | `friend.accepted` | `friend_accepted` | 요청한 사용자 | MEDIUM |
| **매칭** | | | | |
| 매칭 제안 | `matching.proposed` | `matching_proposal` | 그룹 멤버들 | HIGH |
| 매칭 성공 | `matching.matched` | `matching_success` | 그룹 멤버들 | HIGH |
| **예약** | | | | |
| 예약 리마인더 | `reservation.reminder` | `reservation_reminder` | 예약자 | HIGH |
| **랭킹** | | | | |
| 순위 변동 | `ranking.changed` | `ranking_change` | 해당 사용자 | LOW |

### 3.2 우선순위 시스템

```python
class NotificationPriority(str, Enum):
    HIGH = "high"      # 즉시 주의 필요 (메시지, 매칭)
    MEDIUM = "medium"  # 중요하지만 긴급하지 않음 (친구 요청)
    LOW = "low"        # 정보성 (좋아요, 랭킹)
```

---

## 4. 데이터 모델

### 4.1 Notification 테이블

```sql
CREATE TABLE notifications (
    notification_id VARCHAR(36) PRIMARY KEY,
    user_id VARCHAR(36) NOT NULL,

    -- Type and priority
    type VARCHAR(50) NOT NULL,
    priority VARCHAR(20) NOT NULL DEFAULT 'medium',

    -- Content
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    data JSONB,

    -- Routing
    routing JSONB,

    -- Grouping
    group_key VARCHAR(100),

    -- Status
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,

    -- Delivery tracking
    delivered_via_ws BOOLEAN DEFAULT FALSE,
    delivered_via_email BOOLEAN DEFAULT FALSE,

    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    -- Indexes
    INDEX idx_user_unread (user_id, is_read),
    INDEX idx_user_created (user_id, created_at),
    INDEX idx_group_key (group_key)
);
```

### 4.2 스키마 정의

```python
class NotificationCreate(BaseModel):
    """알림 생성 스키마"""
    user_id: str
    type: NotificationType
    priority: NotificationPriority = NotificationPriority.MEDIUM
    title: str
    message: str
    data: dict | None = None
    routing: dict | None = None  # {path: '/messages/123'}
    group_key: str | None = None  # 그룹화 키
```

---

## 5. 핵심 기능

### 5.1 알림 생성 및 전송

```python
async def create_notification(data: NotificationCreate):
    # 1. 사용자 설정 확인
    if not await check_notification_allowed(data.user_id, data.type):
        return None

    # 2. 알림 레코드 생성
    notification = await repository.create(notification)

    # 3. 전송
    if await is_user_online(data.user_id):
        await send_via_websocket(notification)  # 즉시
    else:
        await send_via_email(notification)      # 비동기

    return notification
```

### 5.2 오프라인 백필

```python
@router.get("/notifications/backfill")
async def get_missed_notifications(
    since: datetime,  # 마지막 동기화 시간
    limit: int = 50,
):
    """재접속 시 놓친 알림 조회"""
    notifications = await service.get_notifications_since(
        user_id=current_user.id,
        since=since,
        limit=limit,
    )
    return notifications
```

**프론트엔드 자동 동기화**:
```typescript
useEffect(() => {
    const lastSync = localStorage.getItem('last_notification_sync');
    if (lastSync) {
        notificationService.getBackfill(new Date(lastSync))
            .then(notifications => {
                // 놓친 알림 표시
                toast.info(`${notifications.length}개의 새 알림`);
            });
    }
    localStorage.setItem('last_notification_sync', new Date().toISOString());
}, []);
```

### 5.3 알림 그룹화 (선택적)

```python
# 같은 타입 알림 그룹화
await create_notification(
    group_key="post_123_likes",  # 그룹화 키
    title="새로운 좋아요 3개",
    message="홍길동님 외 2명이 좋아요를 눌렀습니다"
)
```

---

## 6. 이벤트 트리거 구현

### 6.1 메시지 알림

```python
@router.post("/messages/send")
async def send_message(data: MessageCreate):
    # 1. 메시지 저장
    message = await message_service.create(data)

    # 2. 실시간 WS 전송 (기존)
    await ws_manager.send_message(...)

    # 3. 알림 생성 (NEW)
    await notification_service.create_notification(
        NotificationCreate(
            user_id=data.receiver_id,
            type=NotificationType.MESSAGE,
            priority=NotificationPriority.HIGH,
            title=f"{sender.name}님의 새 메시지",
            message=message.content[:50],
            routing={"path": f"/messages/{conversation_id}"},
        )
    )
```

### 6.2 커뮤니티 알림

```python
@router.post("/posts/{post_id}/comments")
async def create_comment(post_id: str, data: CommentCreate):
    # 1. 댓글 생성
    comment = await comment_service.create(post_id, data)

    # 2. 알림 생성 (자신의 게시글이 아닌 경우만)
    if post.author_id != current_user.id:
        await notification_service.create_notification(
            NotificationCreate(
                user_id=post.author_id,
                type=NotificationType.POST_COMMENT,
                priority=NotificationPriority.MEDIUM,
                title=f"{current_user.name}님이 댓글을 남겼습니다",
                message=comment.content[:50],
                routing={"path": f"/community/posts/{post_id}"},
            )
        )
```

### 6.3 친구 알림

```python
@router.post("/friends/request")
async def send_friend_request(data: FriendRequestCreate):
    # 1. 친구 요청 생성
    request = await friend_service.create_request(data)

    # 2. 알림 생성
    await notification_service.create_notification(
        NotificationCreate(
            user_id=data.user_id,
            type=NotificationType.FRIEND_REQUEST,
            priority=NotificationPriority.MEDIUM,
            title=f"{current_user.name}님의 친구 요청",
            message="친구 요청을 수락하시겠습니까?",
            routing={"path": "/friends/requests"},
        )
    )
```

---

## 7. 구현 일정

### Week 1: 인프라 구축
- Notification 모델 업데이트 (priority, routing, group_key)
- NotificationService 강화 (grouping, delivery tracking)
- WebSocket Manager 강화 (connection tracking)
- 백필 API 구현
- 프론트엔드 백필 훅 구현

### Week 2: 메시지 알림
- 메시지 전송 시 알림 생성
- 새 대화 시 알림 생성
- 테스트 (온라인/오프라인)

### Week 3: 커뮤니티 알림
- 댓글 알림
- 좋아요 알림
- 멘션 알림 (선택적)

### Week 4: 친구 알림
- 친구 요청 알림
- 요청 수락 알림

### Week 5: 예약 알림 강화
- 복수 리마인더 지원
- 알림 토글 UI

---

## 8. 성능 고려사항

### 8.1 최적화 전략
- **인덱스**: user_id, is_read, created_at 복합 인덱스
- **배치 처리**: 알림 그룹화로 DB 부하 감소
- **캐싱**: 사용자 설정 캐싱 (Redis)
- **비동기 처리**: 이메일 전송은 백그라운드 작업

### 8.2 확장성
- **수평 확장**: WebSocket Manager 분산 가능
- **파티셔닝**: 사용자별 테이블 파티셔닝 고려
- **아카이빙**: 90일 이상 알림 아카이빙

---

## 9. 모니터링 및 메트릭

### 9.1 핵심 메트릭
- 알림 생성 속도 (notifications/sec)
- 알림 전송 성공률 (WS vs Email)
- 평균 전송 시간
- 백필 요청 빈도
- 사용자별 알림 설정 분포

### 9.2 알림 대시보드
```python
# 메트릭 수집
- 시간대별 알림 생성 추이
- 타입별 알림 분포
- 전송 채널별 성공률
- 평균 읽기 시간
```

---

## 10. 보안 고려사항

### 10.1 접근 제어
- 사용자는 자신의 알림만 조회 가능
- 알림 생성은 서버 이벤트에서만 발생
- WebSocket 연결 시 인증 필수

### 10.2 데이터 보호
- 민감한 정보는 data 필드에 암호화 저장
- 알림 내용은 최소한의 정보만 포함
- 이메일 전송 시 HTTPS 사용

---

## 11. 참고 문서

- [ARC-014: WebSocket 아키텍처](/docs/02_architecture/ARC-014_WebSocket_아키텍처.md)
- [REQ-004: Notification Status](/docs/01_requirements/REQ-004_Notification_Status.md)
- [ARC-001: System Architecture](/docs/02_architecture/ARC-001_System_Architecture.md)

---

## 12. 변경 이력

| 날짜 | 버전 | 변경 내용 | 작성자 |
|------|------|-----------|--------|
| 2026-01-07 | 1.0 | 초안 작성 | System Architect |
