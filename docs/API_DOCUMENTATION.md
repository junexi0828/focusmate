# FocusMate API Documentation

## Overview

FocusMate API는 집중 학습 및 팀 협업을 위한 RESTful API입니다.

**Base URL**: `http://localhost:8000/api/v1`

**Version**: 1.0.0

---

## Authentication

모든 보호된 엔드포인트는 JWT 토큰 인증이 필요합니다.

### Headers
```
Authorization: Bearer <access_token>
```

### Admin Endpoints
일부 엔드포인트는 Admin 권한이 필요합니다 (RBAC).

---

## API Endpoints

### 1. Authentication (`/auth`)

#### POST /auth/register
사용자 등록

**Request**:
```json
{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

**Response** (201):
```json
{
  "user_id": "uuid",
  "email": "user@example.com",
  "username": "username"
}
```

#### POST /auth/login
로그인

**Request**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response** (200):
```json
{
  "access_token": "jwt_token",
  "token_type": "bearer",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "username"
  }
}
```

---

### 2. Stats (`/stats`)

#### POST /stats/goals
사용자 목표 저장

**Request**:
```json
{
  "daily_goal_minutes": 120,
  "weekly_goal_sessions": 10
}
```

**Response** (201):
```json
{
  "goal_id": "uuid",
  "user_id": "uuid",
  "daily_goal_minutes": 120,
  "weekly_goal_sessions": 10,
  "created_at": "2025-12-12T17:00:00Z"
}
```

#### GET /stats/goals
사용자 목표 조회

**Response** (200):
```json
{
  "goal_id": "uuid",
  "daily_goal_minutes": 120,
  "weekly_goal_sessions": 10
}
```

#### POST /stats/sessions
수동 세션 저장

**Request**:
```json
{
  "room_name": "Study Room",
  "duration_minutes": 60,
  "completed_at": "2025-12-12T16:00:00Z"
}
```

#### GET /stats/sessions
세션 기록 조회

**Query Parameters**:
- `limit` (optional): 최대 결과 수 (default: 100)

---

### 3. Chat (`/chats`)

#### GET /chats/unread-count
읽지 않은 메시지 수 조회

**Response** (200):
```json
{
  "unread_count": 5
}
```

#### GET /chats/rooms
채팅방 목록 조회

**Response** (200):
```json
{
  "rooms": [
    {
      "room_id": "uuid",
      "room_name": "General",
      "unread_count": 3,
      "last_message": "Hello!",
      "last_message_at": "2025-12-12T16:00:00Z"
    }
  ]
}
```

---

### 4. Community (`/community`)

#### GET /community/posts
게시글 목록 조회 (검색 지원)

**Query Parameters**:
- `limit` (optional): 최대 결과 수 (default: 20, max: 100)
- `offset` (optional): 페이지네이션 오프셋 (default: 0)
- `category` (optional): 카테고리 필터
- `search` (optional): 검색 쿼리 (제목/내용)

**Response** (200):
```json
{
  "posts": [
    {
      "id": "uuid",
      "user_id": "uuid",
      "title": "Study Tips",
      "content": "Here are some tips...",
      "category": "tips",
      "likes": 10,
      "comment_count": 5,
      "is_liked": false,
      "created_at": "2025-12-12T15:00:00Z"
    }
  ],
  "total": 100,
  "limit": 20,
  "offset": 0
}
```

#### POST /community/posts
게시글 작성

**Request**:
```json
{
  "title": "Study Tips",
  "content": "Here are some tips...",
  "category": "tips"
}
```

#### POST /community/posts/{post_id}/like
게시글 좋아요 토글

**Response** (200):
```json
{
  "success": true,
  "liked": true,
  "new_count": 11
}
```

---

### 5. Ranking (`/ranking`)

#### GET /ranking/teams
팀 목록 조회

**Response** (200):
```json
{
  "teams": [
    {
      "team_id": "uuid",
      "name": "Study Warriors",
      "leader_id": "uuid",
      "total_score": 1500,
      "member_count": 5
    }
  ]
}
```

#### POST /ranking/teams
팀 생성

**Request**:
```json
{
  "name": "Study Warriors",
  "description": "Focused study team"
}
```

#### GET /ranking/teams/{team_id}/members
팀 멤버 조회

**Response** (200):
```json
{
  "members": [
    {
      "user_id": "uuid",
      "role": "leader",
      "joined_at": "2025-12-01T00:00:00Z",
      "total_sessions": 50,
      "total_focus_time": 3000
    }
  ],
  "total": 5
}
```

#### GET /ranking/invitations
사용자 초대 목록 조회

**Query Parameters**:
- `status` (optional): pending, accepted, rejected

**Response** (200):
```json
{
  "invitations": [
    {
      "invitation_id": "uuid",
      "team_id": "uuid",
      "team_name": "Study Warriors",
      "status": "pending",
      "created_at": "2025-12-12T10:00:00Z",
      "expires_at": "2025-12-19T10:00:00Z"
    }
  ],
  "total": 3
}
```

#### POST /ranking/teams/{team_id}/invite
팀원 초대

**Request**:
```json
{
  "email": "newmember@example.com"
}
```

---

### 6. Verification (`/ranking/verifications`)

#### POST /ranking/verifications
인증 요청 제출

**Request** (multipart/form-data):
- `school_name`: string
- `student_id`: string (optional, encrypted)
- `file`: file (encrypted)

**Response** (201):
```json
{
  "verification_id": "uuid",
  "status": "pending",
  "school_name": "University",
  "submitted_at": "2025-12-12T17:00:00Z"
}
```

#### GET /ranking/verifications/pending
대기 중인 인증 조회 (Admin only)

**Response** (200):
```json
{
  "verifications": [
    {
      "verification_id": "uuid",
      "user_id": "uuid",
      "school_name": "University",
      "status": "pending",
      "submitted_at": "2025-12-12T17:00:00Z"
    }
  ]
}
```

#### POST /ranking/verifications/{verification_id}/review
인증 검토 (Admin only)

**Request**:
```json
{
  "approved": true,
  "admin_note": "Verified successfully"
}
```

---

### 7. Mini Games (`/ranking/mini-games`)

#### POST /ranking/mini-games/start
게임 점수 제출

**Request**:
```json
{
  "game_type": "dino_jump",
  "score": 1500,
  "completed_at": "2025-12-12T17:00:00Z"
}
```

**Response** (201):
```json
{
  "id": "uuid",
  "user_id": "uuid",
  "game_type": "dino_jump",
  "score": 1500,
  "completed_at": "2025-12-12T17:00:00Z",
  "created_at": "2025-12-12T17:00:00Z"
}
```

#### GET /ranking/mini-games/leaderboard/{game_type}
게임 리더보드 조회

**Query Parameters**:
- `limit` (optional): 최대 결과 수 (default: 10)

**Response** (200):
```json
{
  "leaderboard": [
    {
      "user_id": "uuid",
      "username": "player1",
      "score": 2000,
      "rank": 1,
      "completed_at": "2025-12-12T16:00:00Z"
    }
  ]
}
```

---

### 8. Achievements (`/achievements`)

#### GET /achievements
업적 목록 조회

**Response** (200):
```json
{
  "achievements": [
    {
      "achievement_id": "uuid",
      "name": "First Session",
      "description": "Complete your first session",
      "requirement_type": "total_sessions",
      "requirement_value": 1,
      "unlocked": true,
      "unlocked_at": "2025-12-01T10:00:00Z"
    }
  ]
}
```

---

## Error Responses

모든 에러는 다음 형식을 따릅니다:

```json
{
  "detail": "Error message",
  "code": "ERROR_CODE"
}
```

### Common Status Codes

- `200 OK`: 성공
- `201 Created`: 리소스 생성 성공
- `400 Bad Request`: 잘못된 요청
- `401 Unauthorized`: 인증 실패
- `403 Forbidden`: 권한 없음
- `404 Not Found`: 리소스 없음
- `500 Internal Server Error`: 서버 오류

---

## Security

### File Encryption
- Verification 파일은 Fernet 대칭 암호화 사용
- 환경 변수 `FILE_ENCRYPTION_KEY` 필요

### SMTP Email
- 환경 변수 설정 필요:
  - `SMTP_HOST`
  - `SMTP_PORT`
  - `SMTP_USER`
  - `SMTP_PASSWORD`
  - `SMTP_FROM_EMAIL`
  - `SMTP_ENABLED`

### Admin RBAC
- `require_admin` 의존성으로 관리자 권한 체크
- 민감한 엔드포인트 보호

---

## Frontend API Clients

### Available Modules

1. **auth.ts** - 인증 관련
2. **stats.ts** - 목표/세션 관리
3. **chat.ts** - 채팅/메시지
4. **miniGames.ts** - 미니게임
5. **community.ts** - 커뮤니티 (예정)
6. **ranking.ts** - 랭킹/팀 (예정)

### Usage Example

```typescript
import { saveUserGoal, getUserGoal } from './api/stats';

// Save goal
const goal = await saveUserGoal({
  daily_goal_minutes: 120,
  weekly_goal_sessions: 10,
});

// Get goal
const currentGoal = await getUserGoal();
```

---

**Last Updated**: 2025-12-12
**API Version**: 1.0.0
**Documentation Status**: Complete for P0+P1+P2 features
