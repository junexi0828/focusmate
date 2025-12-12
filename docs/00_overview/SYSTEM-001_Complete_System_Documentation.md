# FocusMate 전체 시스템 구현 문서

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [아키텍처](#아키텍처)
3. [데이터베이스 스키마](#데이터베이스-스키마)
4. [API 명세](#api-명세)
5. [RBAC 시스템](#rbac-시스템)
6. [Production 서비스](#production-서비스)
7. [배포 가이드](#배포-가이드)

---

## 시스템 개요

### 구현 완료 기능

#### 1. 통합 메시징 시스템
- **3가지 채팅 타입**: Direct (1:1), Team (팀 채널), Matching (매칭 그룹)
- **실시간 통신**: WebSocket + Redis Pub/Sub
- **메시지 기능**: CRUD, 검색, 리액션, 스레드
- **파일 업로드**: 이미지/파일 (10-50MB)
- **블라인드 모드**: 매칭 채팅용 익명 시스템

#### 2. 매칭 시스템
- **학생 인증**: 학생증 업로드 및 관리자 승인
- **매칭 풀**: 그룹 생성 및 관리
- **매칭 제안**: 자동 매칭 및 수락/거절
- **자동 채팅방 생성**: 제안 수락 시 자동 생성

#### 3. Admin & RBAC
- **3가지 역할**: USER, ADMIN, SUPER_ADMIN
- **8가지 권한**: 인증 관리, 시즌 관리, 사용자 관리 등
- **엔드포인트 보호**: 관리자 전용 API

#### 4. Production 서비스
- **SMTP Email**: 인증 결과, 초대 등 알림
- **S3 Storage**: AWS S3 파일 업로드
- **알림 시스템**: 5가지 알림 타입

### 통계

| 항목 | 수량 |
|------|------|
| **Backend Files** | 15+ |
| **Frontend Files** | 7 |
| **API Endpoints** | 18 |
| **Database Tables** | 3 (chat) |
| **TypeScript Types** | 14 interfaces |
| **Total LOC** | 3,000+ |

---

## 아키텍처

### 시스템 아키텍처

```mermaid
graph TB
    subgraph Frontend
        A[React App]
        B[WebSocket Hook]
        C[API Client]
    end

    subgraph Backend
        D[FastAPI]
        E[WebSocket Manager]
        F[Redis Pub/Sub]
        G[Service Layer]
        H[Repository Layer]
    end

    subgraph Database
        I[(PostgreSQL)]
    end

    subgraph External
        J[Redis]
        K[AWS S3]
        L[SMTP Server]
    end

    A --> B
    A --> C
    B --> E
    C --> D
    D --> G
    G --> H
    H --> I
    E --> F
    F --> J
    D --> K
    D --> L
```

### 통합 메시징 플로우

```mermaid
sequenceDiagram
    participant U1 as User 1
    participant WS1 as WebSocket 1
    participant API as FastAPI
    participant Redis as Redis Pub/Sub
    participant WS2 as WebSocket 2
    participant U2 as User 2

    U1->>WS1: Send Message
    WS1->>API: POST /messages
    API->>Redis: Publish Message
    Redis->>WS1: Broadcast
    Redis->>WS2: Broadcast
    WS1->>U1: Display Message
    WS2->>U2: Display Message
```

### 매칭 시스템 플로우

```mermaid
sequenceDiagram
    participant U as User
    participant API as API
    participant Service as ProposalService
    participant Chat as ChatService

    U->>API: Submit Verification
    API->>Service: Create Verification
    Note over Service: Admin Approval
    U->>API: Create Matching Pool
    API->>Service: Create Pool
    Note over Service: Auto Matching
    Service->>U: Send Proposal
    U->>API: Accept Proposal
    API->>Service: Update Proposal
    Service->>Chat: Create Chat Room
    Chat->>U: Chat Room Created
```

---

## 데이터베이스 스키마

### Chat Tables

#### chat_rooms
```sql
CREATE TABLE chat_rooms (
    room_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_type VARCHAR(20) NOT NULL,  -- 'direct', 'team', 'matching'
    room_name VARCHAR(255),
    description TEXT,
    metadata JSON,  -- Type-specific data
    display_mode VARCHAR(10),  -- 'open', 'blind'
    is_active BOOLEAN DEFAULT true,
    is_archived BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_message_at TIMESTAMP WITH TIME ZONE
);
```

#### chat_members
```sql
CREATE TABLE chat_members (
    member_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES chat_rooms(room_id),
    user_id VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'member',
    anonymous_name VARCHAR(50),
    group_label VARCHAR(10),
    is_active BOOLEAN DEFAULT true,
    is_muted BOOLEAN DEFAULT false,
    last_read_at TIMESTAMP WITH TIME ZONE,
    unread_count INTEGER DEFAULT 0,
    joined_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    left_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(room_id, user_id)
);
```

#### chat_messages
```sql
CREATE TABLE chat_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES chat_rooms(room_id),
    sender_id VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    message_type VARCHAR(20) DEFAULT 'text',
    attachments JSON,
    reactions JSON,
    thread_id UUID,
    reply_to_id UUID,
    is_edited BOOLEAN DEFAULT false,
    is_deleted BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deleted_at TIMESTAMP WITH TIME ZONE
);
```

---

## API 명세

### Chat API (15 endpoints)

#### Rooms

**GET /api/v1/chats/rooms**
- 사용자의 모든 채팅방 조회
- Query: `room_type` (optional)
- Response: `ChatRoomListResponse`

**POST /api/v1/chats/rooms/direct**
- 1:1 채팅방 생성
- Body: `DirectChatCreate`
- Response: `ChatRoomResponse`

**POST /api/v1/chats/rooms/team**
- 팀 채널 생성
- Body: `TeamChatCreate`
- Response: `ChatRoomResponse`

**GET /api/v1/chats/rooms/{room_id}**
- 채팅방 상세 조회
- Response: `ChatRoomResponse`

#### Messages

**GET /api/v1/chats/rooms/{room_id}/messages**
- 메시지 목록 조회
- Query: `limit`, `before_message_id`
- Response: `MessageListResponse`

**POST /api/v1/chats/rooms/{room_id}/messages**
- 메시지 전송
- Body: `MessageCreate`
- Response: `MessageResponse`

**PATCH /api/v1/chats/rooms/{room_id}/messages/{message_id}**
- 메시지 수정
- Body: `MessageUpdate`
- Response: `MessageResponse`

**DELETE /api/v1/chats/rooms/{room_id}/messages/{message_id}**
- 메시지 삭제 (소프트 삭제)
- Response: `MessageResponse`

**GET /api/v1/chats/rooms/{room_id}/search**
- 메시지 검색
- Query: `q`, `limit`
- Response: `MessageListResponse`

**POST /api/v1/chats/rooms/{room_id}/read**
- 읽음 표시
- Response: `{"message": "Marked as read"}`

#### File Upload

**POST /api/v1/chats/rooms/{room_id}/upload**
- 파일 업로드
- Body: `multipart/form-data`
- Response: `{"uploaded": int, "files": [...]}`

#### Reactions

**POST /api/v1/chats/rooms/{room_id}/messages/{message_id}/react**
- 리액션 추가
- Query: `emoji`
- Response: `{"message": "...", "reactions": [...]}`

**DELETE /api/v1/chats/rooms/{room_id}/messages/{message_id}/react**
- 리액션 제거
- Query: `emoji`
- Response: `{"message": "...", "reactions": [...]}`

#### WebSocket

**WS /api/v1/chats/ws**
- 실시간 채팅 연결
- Query: `token` (JWT)
- Events: `message`, `message_updated`, `message_deleted`, `typing`

### Proposals API (3 endpoints)

**GET /api/v1/matching/proposals/my**
- 내 제안 목록
- Response: `MatchingProposal[]`

**GET /api/v1/matching/proposals/{proposal_id}**
- 제안 상세
- Response: `MatchingProposal`

**POST /api/v1/matching/proposals/{proposal_id}/respond**
- 제안 응답
- Body: `{"action": "accept" | "reject"}`
- Response: `MatchingProposal`

---

## RBAC 시스템

### 역할 (Roles)

| Role | Description | Permissions |
|------|-------------|-------------|
| **USER** | 일반 사용자 | 기본 기능만 사용 |
| **ADMIN** | 관리자 | 인증 승인, 시즌 관리, 분석 조회 |
| **SUPER_ADMIN** | 최고 관리자 | 모든 권한 |

### 권한 (Permissions)

| Permission | Description | Roles |
|------------|-------------|-------|
| `VERIFY_USERS` | 사용자 인증 승인 | ADMIN, SUPER_ADMIN |
| `VIEW_VERIFICATIONS` | 인증 요청 조회 | ADMIN, SUPER_ADMIN |
| `MANAGE_SEASONS` | 랭킹 시즌 관리 | ADMIN, SUPER_ADMIN |
| `VIEW_ALL_RANKINGS` | 전체 랭킹 조회 | ADMIN, SUPER_ADMIN |
| `MANAGE_USERS` | 사용자 관리 | SUPER_ADMIN |
| `BAN_USERS` | 사용자 차단 | SUPER_ADMIN |
| `VIEW_ANALYTICS` | 분석 데이터 조회 | ADMIN, SUPER_ADMIN |
| `MANAGE_SETTINGS` | 시스템 설정 관리 | SUPER_ADMIN |

### 사용 예시

```python
from app.core.rbac import require_admin, require_super_admin

@router.get("/admin/pending")
async def get_pending_verifications(
    current_user: Annotated[dict, Depends(require_admin)],
    ...
):
    # Only ADMIN or SUPER_ADMIN can access
    pass

@router.post("/admin/users/{user_id}/ban")
async def ban_user(
    current_user: Annotated[dict, Depends(require_super_admin)],
    ...
):
    # Only SUPER_ADMIN can access
    pass
```

---

## Production 서비스

### SMTP Email Service

**기능**:
- 인증 제출 확인 이메일
- 인증 승인/거부 이메일
- 팀 초대 이메일

**설정**:
```python
from app.infrastructure.email.email_service import EmailService

email_service = EmailService()
await email_service.send_verification_approved_email(
    team_name="FocusMate Team",
    leader_email="user@example.com",
    admin_note="Great submission!"
)
```

### S3 Storage Service

**기능**:
- 파일 업로드 (단일/다중)
- 파일 삭제
- S3 URL 생성

**설정**:
```python
from app.infrastructure.storage.file_upload import S3UploadService

s3_service = S3UploadService(bucket_name="focusmate-uploads")
s3_key, file_url = await s3_service.save_file(file, user_id)
```

### 알림 시스템

**알림 타입**:
- `MESSAGE`: 새 메시지
- `MENTION`: 멘션
- `REACTION`: 리액션
- `PROPOSAL`: 매칭 제안
- `SYSTEM`: 시스템 알림

---

## 배포 가이드

### 환경 변수

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/focusmate

# Redis
REDIS_URL=redis://localhost:6379

# JWT
JWT_SECRET=your-secret-key
JWT_ALGORITHM=HS256

# SMTP Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
FROM_EMAIL=noreply@focusmate.com
FROM_NAME=FocusMate

# AWS S3
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_REGION=us-east-1
S3_BUCKET_NAME=focusmate-uploads

# Frontend
VITE_API_URL=http://localhost:8000
VITE_WS_URL=ws://localhost:8000/api/v1/chats/ws
```

### 데이터베이스 마이그레이션

```bash
cd backend
alembic upgrade head
```

### Backend 실행

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend 실행

```bash
cd frontend
npm install
npm run dev
```

### Redis 실행

```bash
# macOS
brew install redis
redis-server

# Ubuntu
sudo apt install redis
sudo systemctl start redis
```

### Production 배포

1. **Backend**: Docker + Kubernetes
2. **Frontend**: Vercel / Netlify
3. **Database**: AWS RDS (PostgreSQL)
4. **Redis**: AWS ElastiCache
5. **Storage**: AWS S3
6. **Email**: AWS SES / SendGrid

---

## 테스트

### Unit Tests
```bash
cd backend
pytest tests/unit/
```

### Integration Tests
```bash
cd backend
pytest tests/integration/
```

### E2E Tests
```bash
cd frontend
npm run test:e2e
```

---

**작성일**: 2025-12-12
**버전**: 1.0.0
**상태**: Production Ready ✅
