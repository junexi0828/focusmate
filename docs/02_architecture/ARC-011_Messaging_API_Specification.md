---
id: ARC-011
title: Messaging API Specification
version: 1.0
status: Approved
date: 2025-12-12
author: Focus Mate Team
category: Architecture
---

# Messaging API Specification

## [Home](../README.md) > [Architecture](./README.md) > ARC-011

---


## 개요

통합 메시징 시스템의 REST API 및 WebSocket API 명세입니다.

**Base URL**: `/api/v1/chats`

## 인증

모든 엔드포인트는 JWT 인증이 필요합니다.

```
Authorization: Bearer <token>
```

---

## REST API

### 채팅방 관리

#### GET /rooms

사용자의 모든 채팅방 목록을 조회합니다.

**Query Parameters**:
- `room_type` (optional): 'direct' | 'team' | 'matching'

**Response**:
```json
{
  "rooms": [
    {
      "room_id": "uuid",
      "room_type": "direct",
      "room_name": "John Doe",
      "description": null,
      "metadata": {...},
      "display_mode": "open",
      "is_active": true,
      "unread_count": 5,
      "last_message_at": "2025-12-12T10:00:00Z",
      "created_at": "2025-12-01T10:00:00Z"
    }
  ],
  "total": 10
}
```

#### POST /rooms/direct

1:1 채팅방을 생성합니다.

**Request Body**:
```json
{
  "recipient_id": "user_id"
}
```

**Response**: `201 Created`
```json
{
  "room_id": "uuid",
  "room_type": "direct",
  "room_name": "John Doe",
  "metadata": {
    "type": "direct",
    "user_ids": ["user1", "user2"]
  },
  "created_at": "2025-12-12T10:00:00Z"
}
```

#### POST /rooms/team

팀 채널을 생성합니다.

**Request Body**:
```json
{
  "team_id": "uuid",
  "room_name": "General",
  "description": "Team general channel",
  "is_private": false
}
```

**Response**: `201 Created`

#### GET /rooms/{room_id}

채팅방 상세 정보를 조회합니다.

**Response**:
```json
{
  "room_id": "uuid",
  "room_type": "team",
  "room_name": "General",
  "description": "Team general channel",
  "metadata": {...},
  "member_count": 15,
  "created_at": "2025-12-01T10:00:00Z"
}
```

---

### 메시지 관리

#### GET /rooms/{room_id}/messages

채팅방의 메시지 목록을 조회합니다.

**Query Parameters**:
- `limit` (default: 50): 조회할 메시지 수
- `before_message_id` (optional): 페이지네이션용 메시지 ID

**Response**:
```json
{
  "messages": [
    {
      "message_id": "uuid",
      "room_id": "uuid",
      "sender_id": "user_id",
      "content": "Hello!",
      "message_type": "text",
      "attachments": null,
      "reactions": [
        {
          "emoji": "👍",
          "users": ["user1", "user2"],
          "count": 2
        }
      ],
      "is_edited": false,
      "is_deleted": false,
      "created_at": "2025-12-12T10:00:00Z"
    }
  ],
  "total": 100,
  "has_more": true
}
```

#### POST /rooms/{room_id}/messages

메시지를 전송합니다.

**Request Body**:
```json
{
  "content": "Hello, world!",
  "message_type": "text",
  "reply_to_id": "uuid",  // optional
  "thread_id": "uuid"     // optional
}
```

**Response**: `201 Created`
```json
{
  "message_id": "uuid",
  "room_id": "uuid",
  "sender_id": "user_id",
  "content": "Hello, world!",
  "created_at": "2025-12-12T10:00:00Z"
}
```

#### PATCH /rooms/{room_id}/messages/{message_id}

메시지를 수정합니다.

**Request Body**:
```json
{
  "content": "Updated message"
}
```

**Response**:
```json
{
  "message_id": "uuid",
  "content": "Updated message",
  "is_edited": true,
  "updated_at": "2025-12-12T10:05:00Z"
}
```

#### DELETE /rooms/{room_id}/messages/{message_id}

메시지를 삭제합니다 (소프트 삭제).

**Response**:
```json
{
  "message_id": "uuid",
  "is_deleted": true,
  "deleted_at": "2025-12-12T10:10:00Z"
}
```

---

### 메시지 검색

#### GET /rooms/{room_id}/search

채팅방 내 메시지를 검색합니다.

**Query Parameters**:
- `q` (required): 검색어
- `limit` (default: 50): 결과 수

**Response**:
```json
{
  "messages": [...],
  "total": 5,
  "has_more": false
}
```

---

### 읽음 표시

#### POST /rooms/{room_id}/read

메시지를 읽음으로 표시합니다.

**Response**:
```json
{
  "message": "Marked as read"
}
```

---

### 파일 업로드

#### POST /rooms/{room_id}/upload

파일을 업로드합니다.

**Request**: `multipart/form-data`
- `files`: File[] (최대 10개)

**Response**:
```json
{
  "uploaded": 2,
  "files": [
    {
      "path": "uploads/user_id/2025/12/12/file1.jpg",
      "url": "/uploads/user_id/2025/12/12/file1.jpg"
    },
    {
      "path": "uploads/user_id/2025/12/12/file2.pdf",
      "url": "/uploads/user_id/2025/12/12/file2.pdf"
    }
  ]
}
```

**제한사항**:
- 이미지: 10MB
- 파일: 50MB
- 허용 타입: jpg, jpeg, png, gif, webp, pdf, doc, docx, xls, xlsx

---

### 리액션

#### POST /rooms/{room_id}/messages/{message_id}/react

메시지에 리액션을 추가합니다.

**Query Parameters**:
- `emoji` (required): 이모지 (예: 👍, ❤️, 😂)

**Response**:
```json
{
  "message": "Reaction added",
  "reactions": [
    {
      "emoji": "👍",
      "users": ["user1"],
      "count": 1
    }
  ]
}
```

#### DELETE /rooms/{room_id}/messages/{message_id}/react

메시지에서 리액션을 제거합니다.

**Query Parameters**:
- `emoji` (required): 이모지

**Response**:
```json
{
  "message": "Reaction removed",
  "reactions": []
}
```

---

## WebSocket API

### 연결

**Endpoint**: `ws://localhost:8000/api/v1/chats/ws`

**Query Parameters**:
- `token` (required): JWT 토큰

```typescript
const ws = new WebSocket(`${WS_URL}/api/v1/chats/ws?token=${token}`);
```

### 이벤트

#### 수신 이벤트

**message** - 새 메시지
```json
{
  "type": "message",
  "message": {
    "message_id": "uuid",
    "room_id": "uuid",
    "sender_id": "user_id",
    "content": "Hello!",
    "created_at": "2025-12-12T10:00:00Z"
  }
}
```

**message_updated** - 메시지 수정
```json
{
  "type": "message_updated",
  "message": {
    "message_id": "uuid",
    "content": "Updated",
    "is_edited": true
  }
}
```

**message_deleted** - 메시지 삭제
```json
{
  "type": "message_deleted",
  "message_id": "uuid",
  "room_id": "uuid"
}
```

**typing** - 타이핑 중
```json
{
  "type": "typing",
  "room_id": "uuid",
  "user_id": "user_id"
}
```

**joined** - 사용자 입장
```json
{
  "type": "joined",
  "room_id": "uuid",
  "user_id": "user_id"
}
```

**left** - 사용자 퇴장
```json
{
  "type": "left",
  "room_id": "uuid",
  "user_id": "user_id"
}
```

#### 송신 이벤트

**join_room** - 채팅방 입장
```json
{
  "type": "join_room",
  "room_id": "uuid"
}
```

**leave_room** - 채팅방 퇴장
```json
{
  "type": "leave_room",
  "room_id": "uuid"
}
```

**typing** - 타이핑 알림
```json
{
  "type": "typing",
  "room_id": "uuid"
}
```

---

## 에러 응답

### 400 Bad Request
```json
{
  "detail": "Invalid request data"
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication required"
}
```

### 403 Forbidden
```json
{
  "detail": "Not a member of this room"
}
```

### 404 Not Found
```json
{
  "detail": "Room not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error"
}
```

---

**작성일**: 2025-12-12
**버전**: 1.0.0
