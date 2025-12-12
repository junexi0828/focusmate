---
id: REQ-002
title: API Specification
version: 1.0
status: Approved
date: 2025-12-04
author: Focus Mate Team
iso_standard: ISO/IEC/IEEE 29148
---

# API Specification

# Team Pomodoro Timer (Focus Mate)

**문서 버전**: 1.0
**작성일**: 2025-12-04
**Base URL**: `http://localhost:8000/api/v1`

---

## 목차

1. [인증](#1-인증)
2. [공통 응답 포맷](#2-공통-응답-포맷)
3. [REST API 엔드포인트](#3-rest-api-엔드포인트)
4. [WebSocket 프로토콜](#4-websocket-프로토콜)
5. [에러 코드](#5-에러-코드)

---

## 1. 인증

**v1.0**: 인증 없음 (공개 방 시스템)
**v1.1**: JWT 기반 인증 예정

```http
Authorization: Bearer <jwt_token>
```

---

## 2. 공통 응답 포맷

### 2.1 성공 응답

```json
{
  "status": "success",
  "data": { ... },
  "message": "Operation completed successfully"
}
```

### 2.2 에러 응답

```json
{
  "status": "error",
  "error": {
    "code": "ROOM_NOT_FOUND",
    "message": "Room with id 'xxx' not found",
    "details": { ... }
  }
}
```

---

## 3. REST API 엔드포인트

### 3.1 Health Check

#### GET /health

서버 상태 확인

**Response 200**:

```json
{
  "status": "healthy",
  "timestamp": "2025-12-04T10:00:00Z",
  "version": "1.0.0"
}
```

---

### 3.2 방 관리 (Rooms)

#### POST /api/v1/rooms

새로운 방 생성

**Request Body**:

```json
{
  "room_name": "team-alpha",
  "work_duration_minutes": 25,
  "break_duration_minutes": 5,
  "auto_start_break": true
}
```

**Validation**:

- `room_name`: 3-50자, 영문/숫자/하이픈/언더스코어만
- `work_duration_minutes`: 1-60
- `break_duration_minutes`: 1-30

**Response 201**:

```json
{
  "status": "success",
  "data": {
    "room_id": "550e8400-e29b-41d4-a716-446655440000",
    "room_name": "team-alpha",
    "work_duration": 1500,
    "break_duration": 300,
    "auto_start_break": true,
    "share_url": "http://localhost:3000/room/550e8400-e29b-41d4-a716-446655440000",
    "created_at": "2025-12-04T10:00:00Z"
  },
  "message": "Room created successfully"
}
```

**Response 422** (Validation Error):

```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": [
      {
        "loc": ["body", "room_name"],
        "msg": "String should match pattern '^[a-zA-Z0-9_-]+$'",
        "type": "string_pattern_mismatch"
      }
    ]
  }
}
```

---

#### GET /api/v1/rooms/{room_id}

방 정보 조회

**Path Parameters**:

- `room_id`: UUID 형식

**Response 200**:

```json
{
  "status": "success",
  "data": {
    "room_id": "550e8400-e29b-41d4-a716-446655440000",
    "room_name": "team-alpha",
    "work_duration": 1500,
    "break_duration": 300,
    "current_participants": 3,
    "max_participants": 50,
    "timer_state": {
      "status": "running",
      "session_type": "work",
      "remaining_seconds": 1234,
      "target_timestamp": "2025-12-04T10:25:00Z",
      "started_at": "2025-12-04T10:00:00Z"
    },
    "created_at": "2025-12-04T09:00:00Z"
  }
}
```

**Response 404**:

```json
{
  "status": "error",
  "error": {
    "code": "ROOM_NOT_FOUND",
    "message": "Room with id '550e8400-e29b-41d4-a716-446655440000' not found"
  }
}
```

---

#### DELETE /api/v1/rooms/{room_id}

방 삭제 (방장만 가능)

**Response 204**: No Content

**Response 403**:

```json
{
  "status": "error",
  "error": {
    "code": "FORBIDDEN",
    "message": "Only room host can delete the room"
  }
}
```

---

### 3.3 타이머 제어 (Timer)

#### POST /api/v1/rooms/{room_id}/timer/start

타이머 시작

**Request Body**:

```json
{
  "session_type": "work"
}
```

**Response 200**:

```json
{
  "status": "success",
  "data": {
    "status": "running",
    "session_type": "work",
    "target_timestamp": "2025-12-04T10:25:00Z",
    "started_at": "2025-12-04T10:00:00Z",
    "duration_seconds": 1500
  },
  "message": "Timer started successfully"
}
```

**Response 409** (Already Running):

```json
{
  "status": "error",
  "error": {
    "code": "TIMER_ALREADY_RUNNING",
    "message": "Timer is already running in this room"
  }
}
```

---

#### POST /api/v1/rooms/{room_id}/timer/pause

타이머 일시정지

**Response 200**:

```json
{
  "status": "success",
  "data": {
    "status": "paused",
    "remaining_seconds": 1234
  },
  "message": "Timer paused"
}
```

---

#### POST /api/v1/rooms/{room_id}/timer/resume

타이머 재개

**Response 200**:

```json
{
  "status": "success",
  "data": {
    "status": "running",
    "target_timestamp": "2025-12-04T10:20:34Z"
  },
  "message": "Timer resumed"
}
```

---

#### POST /api/v1/rooms/{room_id}/timer/reset

타이머 재설정

**Response 200**:

```json
{
  "status": "success",
  "data": {
    "status": "idle",
    "remaining_seconds": 1500
  },
  "message": "Timer reset"
}
```

---

### 3.4 통계 (Statistics) - v1.1

#### GET /api/v1/rooms/{room_id}/statistics

방 통계 조회

**Query Parameters**:

- `period`: `today` | `week` | `month` (기본: `today`)

**Response 200**:

```json
{
  "status": "success",
  "data": {
    "period": "today",
    "completed_sessions": 8,
    "total_focus_time_seconds": 12000,
    "average_session_duration": 1500,
    "completion_rate": 0.95
  }
}
```

---

## 4. WebSocket 프로토콜

### 4.1 연결

**Endpoint**: `ws://localhost:8000/ws/room/{room_id}`

**Connection Example**:

```javascript
const ws = new WebSocket(
  "ws://localhost:8000/ws/room/550e8400-e29b-41d4-a716-446655440000"
);

ws.onopen = () => {
  console.log("Connected to room");
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  handleMessage(message);
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};

ws.onclose = () => {
  console.log("Disconnected from room");
  // 재연결 로직
};
```

---

### 4.2 클라이언트 → 서버 메시지

#### 타이머 시작

```json
{
  "action": "start_timer",
  "data": {
    "session_type": "work"
  }
}
```

#### 타이머 일시정지

```json
{
  "action": "pause_timer"
}
```

#### 타이머 재개

```json
{
  "action": "resume_timer"
}
```

#### 타이머 재설정

```json
{
  "action": "reset_timer"
}
```

#### Heartbeat (연결 유지)

```json
{
  "action": "ping"
}
```

---

### 4.3 서버 → 클라이언트 메시지

#### 타이머 상태 업데이트

```json
{
  "event": "timer_update",
  "data": {
    "status": "running",
    "session_type": "work",
    "target_timestamp": "2025-12-04T10:25:00Z",
    "started_at": "2025-12-04T10:00:00Z",
    "remaining_seconds": 1234
  },
  "timestamp": "2025-12-04T10:04:26Z"
}
```

#### 참여자 변경

```json
{
  "event": "participant_update",
  "data": {
    "action": "joined",
    "participant": {
      "id": "user-123",
      "name": "Alice"
    },
    "current_count": 4
  },
  "timestamp": "2025-12-04T10:05:00Z"
}
```

#### 타이머 완료

```json
{
  "event": "timer_complete",
  "data": {
    "completed_session_type": "work",
    "next_session_type": "break",
    "auto_start": true
  },
  "timestamp": "2025-12-04T10:25:00Z"
}
```

#### Heartbeat 응답

```json
{
  "event": "pong",
  "timestamp": "2025-12-04T10:00:00Z"
}
```

#### 에러

```json
{
  "event": "error",
  "error": {
    "code": "INVALID_ACTION",
    "message": "Unknown action: 'invalid_action'"
  },
  "timestamp": "2025-12-04T10:00:00Z"
}
```

---

### 4.4 재연결 전략

**클라이언트 구현 예시**:

```typescript
class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  connect(roomId: string): void {
    this.ws = new WebSocket(`ws://localhost:8000/ws/room/${roomId}`);

    this.ws.onopen = () => {
      console.log("Connected");
      this.reconnectAttempts = 0;
    };

    this.ws.onclose = () => {
      console.log("Disconnected");
      this.reconnect(roomId);
    };

    this.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };
  }

  private reconnect(roomId: string): void {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error("Max reconnect attempts reached");
      return;
    }

    this.reconnectAttempts++;
    const delay = Math.min(1000 * 2 ** this.reconnectAttempts, 30000);

    console.log(
      `Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`
    );
    setTimeout(() => this.connect(roomId), delay);
  }
}
```

---

## 5. 에러 코드

### 5.1 HTTP 상태 코드

| 코드 | 설명                  | 사용 사례                         |
| ---- | --------------------- | --------------------------------- |
| 200  | OK                    | 성공적인 GET, PUT, PATCH          |
| 201  | Created               | 성공적인 POST (리소스 생성)       |
| 204  | No Content            | 성공적인 DELETE                   |
| 400  | Bad Request           | 잘못된 요청 형식                  |
| 404  | Not Found             | 리소스를 찾을 수 없음             |
| 409  | Conflict              | 리소스 충돌 (타이머 이미 실행 중) |
| 422  | Unprocessable Entity  | 유효성 검증 실패                  |
| 500  | Internal Server Error | 서버 내부 오류                    |

---

### 5.2 애플리케이션 에러 코드

| 코드                       | HTTP 상태 | 설명                    |
| -------------------------- | --------- | ----------------------- |
| `ROOM_NOT_FOUND`           | 404       | 방을 찾을 수 없음       |
| `ROOM_NAME_INVALID`        | 422       | 유효하지 않은 방 이름   |
| `TIMER_ALREADY_RUNNING`    | 409       | 타이머가 이미 실행 중   |
| `TIMER_NOT_RUNNING`        | 409       | 타이머가 실행 중이 아님 |
| `INVALID_DURATION`         | 422       | 유효하지 않은 시간 값   |
| `MAX_PARTICIPANTS_REACHED` | 409       | 최대 참여 인원 초과     |
| `FORBIDDEN`                | 403       | 권한 없음               |
| `VALIDATION_ERROR`         | 422       | 입력 검증 실패          |
| `INTERNAL_ERROR`           | 500       | 서버 내부 오류          |

---

## 6. Rate Limiting

**v1.1 예정**

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1638360000
```

---

## 7. 예시 시나리오

### 7.1 방 생성 및 타이머 시작

```bash
# 1. 방 생성
curl -X POST http://localhost:8000/api/v1/rooms \
  -H "Content-Type: application/json" \
  -d '{
    "room_name": "team-alpha",
    "work_duration_minutes": 25,
    "break_duration_minutes": 5
  }'

# Response:
# {
#   "status": "success",
#   "data": {
#     "room_id": "550e8400-e29b-41d4-a716-446655440000",
#     ...
#   }
# }

# 2. 타이머 시작
curl -X POST http://localhost:8000/api/v1/rooms/550e8400-e29b-41d4-a716-446655440000/timer/start \
  -H "Content-Type: application/json" \
  -d '{"session_type": "work"}'

# 3. WebSocket 연결 (JavaScript)
const ws = new WebSocket('ws://localhost:8000/ws/room/550e8400-e29b-41d4-a716-446655440000');
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Timer update:', message);
};
```

---

## 8. OpenAPI (Swagger) 문서

FastAPI는 자동으로 OpenAPI 문서를 생성합니다:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

**문서 끝**
