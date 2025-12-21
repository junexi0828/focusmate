---
id: ARC-008
title: Matching System API Specification
version: 1.0
status: Approved
date: 2025-12-12
author: Focus Mate Team
category: Architecture
---

# Matching System API Specification

## [Home](../README.md) > [Architecture](./README.md) > ARC-008

---

## 🌐 API 개요

### Base URL
```
Production: https://api.focusmate.com/api/v1
Development: http://localhost:8000/api/v1
```

### 인증
모든 API는 JWT Bearer Token 인증 필요 (일부 공개 API 제외)
```
Authorization: Bearer <access_token>
```

### 응답 형식
```json
{
  "success": true,
  "data": {},
  "message": "Success",
  "timestamp": "2025-12-12T13:34:54Z"
}
```

### 에러 응답
```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Error description",
    "details": {}
  },
  "timestamp": "2025-12-12T13:34:54Z"
}
```

## 📑 목차

1. [사용자 인증 API](#1-사용자-인증-api)
2. [매칭 풀 API](#2-매칭-풀-api)
3. [매칭 제안 API](#3-매칭-제안-api)
4. [메시지 API](#4-메시지-api)
5. [관리자 API](#5-관리자-api)

---

## 1. 사용자 인증 API

### 1.1 인증 신청 제출

사용자가 학과/학년 인증을 신청합니다.

**Endpoint**: `POST /verification/submit`

**Request Body**:
```json
{
  "school_name": "서울대학교",
  "department": "컴퓨터공학과",
  "major_category": "공과대학",
  "grade": "3학년",
  "student_id": "2021-12345",
  "gender": "male",
  "documents": [
    "https://storage.example.com/docs/student_card.jpg",
    "https://storage.example.com/docs/certificate.pdf"
  ]
}
```

**Response** (201 Created):
```json
{
  "verification_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "pending",
  "submitted_at": "2025-12-12T13:34:54Z",
  "message": "인증 신청이 제출되었습니다. 관리자 검토 후 결과를 알려드립니다."
}
```

**Error Codes**:
- `400 ALREADY_SUBMITTED`: 이미 인증 신청 중
- `400 INVALID_DOCUMENT`: 잘못된 서류 형식
- `401 UNAUTHORIZED`: 인증 필요

---

### 1.2 인증 상태 조회

현재 사용자의 인증 상태를 조회합니다.

**Endpoint**: `GET /verification/status`

**Response** (200 OK):
```json
{
  "verification_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "approved",
  "school_name": "서울대학교",
  "department": "컴퓨터공학과",
  "major_category": "공과대학",
  "grade": "3학년",
  "gender": "male",
  "badge_visible": true,
  "department_visible": true,
  "verified_at": "2025-12-10T10:00:00Z"
}
```

**Status Values**:
- `pending`: 검토 대기 중
- `approved`: 승인됨
- `rejected`: 반려됨
- `null`: 신청 내역 없음

---

### 1.3 인증 배지 설정 변경

인증 배지 및 학과 표시 설정을 변경합니다.

**Endpoint**: `PATCH /verification/settings`

**Request Body**:
```json
{
  "badge_visible": true,
  "department_visible": false
}
```

**Response** (200 OK):
```json
{
  "badge_visible": true,
  "department_visible": false,
  "message": "설정이 변경되었습니다."
}
```

---

### 1.4 서류 업로드

인증 서류를 업로드합니다.

**Endpoint**: `POST /verification/upload`

**Request** (multipart/form-data):
```
files: [File, File, ...]
```

**Response** (201 Created):
```json
{
  "uploaded_files": [
    "https://storage.example.com/docs/abc123.jpg",
    "https://storage.example.com/docs/def456.pdf"
  ],
  "count": 2
}
```

**Constraints**:
- 최대 파일 크기: 10MB
- 허용 형식: JPG, PNG, PDF
- 최대 파일 수: 5개

---

## 2. 매칭 풀 API

### 2.1 매칭 풀 등록

새로운 매칭 풀을 등록합니다.

**Endpoint**: `POST /matching/pools`

**Request Body**:
```json
{
  "member_ids": [
    "user-id-1",
    "user-id-2",
    "user-id-3",
    "user-id-4"
  ],
  "preferred_match_type": "major_category",
  "preferred_categories": ["공과대학", "자연과학대학"],
  "matching_type": "blind",
  "message": "즐겁게 만나요! 공대생 환영합니다 😊"
}
```

**Field Descriptions**:
- `member_ids`: 그룹 멤버 user_id 배열 (2~8명)
- `preferred_match_type`: `any` | `same_department` | `major_category`
- `preferred_categories`: 선호 전공 계열 (복수 선택 가능)
- `matching_type`: `blind` | `open`
- `message`: 소개 메시지 (1~200자)

**Response** (201 Created):
```json
{
  "pool_id": "660e8400-e29b-41d4-a716-446655440000",
  "member_count": 4,
  "department": "컴퓨터공학과",
  "grade": "3학년",
  "gender": "male",
  "status": "waiting",
  "created_at": "2025-12-12T13:34:54Z",
  "expires_at": "2025-12-19T13:34:54Z"
}
```

**Error Codes**:
- `400 INVALID_MEMBER_COUNT`: 멤버 수 2~8명 제한
- `400 UNVERIFIED_MEMBER`: 인증되지 않은 멤버 포함
- `400 ALREADY_IN_POOL`: 이미 다른 풀에 등록 중
- `400 INVALID_MESSAGE_LENGTH`: 메시지 길이 초과

---

### 2.2 내 매칭 풀 조회

현재 사용자가 등록한 매칭 풀을 조회합니다.

**Endpoint**: `GET /matching/pools/my`

**Response** (200 OK):
```json
{
  "pool": {
    "pool_id": "660e8400-e29b-41d4-a716-446655440000",
    "member_count": 4,
    "members": [
      {
        "user_id": "user-id-1",
        "name": "김철수",
        "department": "컴퓨터공학과",
        "grade": "3학년"
      }
    ],
    "preferred_match_type": "major_category",
    "preferred_categories": ["공과대학"],
    "matching_type": "blind",
    "message": "즐겁게 만나요!",
    "status": "waiting",
    "created_at": "2025-12-12T13:34:54Z",
    "expires_at": "2025-12-19T13:34:54Z"
  }
}
```

**Response** (404 Not Found):
```json
{
  "pool": null,
  "message": "등록된 매칭 풀이 없습니다."
}
```

---

### 2.3 매칭 풀 취소

등록한 매칭 풀을 취소합니다.

**Endpoint**: `DELETE /matching/pools/{pool_id}`

**Response** (200 OK):
```json
{
  "message": "매칭 풀이 취소되었습니다."
}
```

**Error Codes**:
- `403 FORBIDDEN`: 풀 생성자만 취소 가능
- `404 NOT_FOUND`: 풀을 찾을 수 없음
- `400 ALREADY_MATCHED`: 이미 매칭된 풀은 취소 불가

---

### 2.4 대기 중인 풀 통계

현재 대기 중인 매칭 풀 통계를 조회합니다.

**Endpoint**: `GET /matching/pools/stats`

**Response** (200 OK):
```json
{
  "total_waiting": 25,
  "by_member_count": {
    "2": 5,
    "3": 8,
    "4": 10,
    "5": 2
  },
  "by_gender": {
    "male": 15,
    "female": 10
  },
  "average_wait_time_hours": 12.5
}
```

---

## 3. 매칭 제안 API

### 3.1 내 매칭 제안 조회

현재 사용자에게 온 매칭 제안을 조회합니다.

**Endpoint**: `GET /matching/proposals`

**Query Parameters**:
- `status`: `pending` | `accepted` | `rejected` | `all` (default: `pending`)

**Response** (200 OK):
```json
{
  "proposals": [
    {
      "proposal_id": "770e8400-e29b-41d4-a716-446655440000",
      "my_pool": {
        "pool_id": "660e8400-e29b-41d4-a716-446655440000",
        "member_count": 4,
        "department": "컴퓨터공학과"
      },
      "matched_pool": {
        "pool_id": "880e8400-e29b-41d4-a716-446655440000",
        "member_count": 4,
        "department": "경영학과",
        "message": "재미있게 놀아요!",
        "matching_type": "blind"
      },
      "my_status": "pending",
      "other_status": "pending",
      "created_at": "2025-12-12T13:34:54Z",
      "expires_at": "2025-12-13T13:34:54Z"
    }
  ],
  "total": 1
}
```

---

### 3.2 매칭 제안 수락

매칭 제안을 수락합니다.

**Endpoint**: `POST /matching/proposals/{proposal_id}/accept`

**Response** (200 OK):
```json
{
  "proposal_id": "770e8400-e29b-41d4-a716-446655440000",
  "my_status": "accepted",
  "other_status": "pending",
  "message": "수락했습니다. 상대방의 응답을 기다리고 있습니다."
}
```

**Response** (200 OK - 양측 수락):
```json
{
  "proposal_id": "770e8400-e29b-41d4-a716-446655440000",
  "my_status": "accepted",
  "other_status": "accepted",
  "final_status": "matched",
  "chat_room": {
    "room_id": "990e8400-e29b-41d4-a716-446655440000",
    "room_name": "과팅 매칭 - 2025.12.12",
    "display_mode": "blind",
    "members_count": 8
  },
  "message": "매칭이 성사되었습니다! 단체 메시지방이 개설되었습니다."
}
```

**Error Codes**:
- `404 NOT_FOUND`: 제안을 찾을 수 없음
- `400 ALREADY_RESPONDED`: 이미 응답한 제안
- `400 EXPIRED`: 만료된 제안

---

### 3.3 매칭 제안 거절

매칭 제안을 거절합니다.

**Endpoint**: `POST /matching/proposals/{proposal_id}/reject`

**Request Body** (optional):
```json
{
  "reason": "시간이 맞지 않아요"
}
```

**Response** (200 OK):
```json
{
  "proposal_id": "770e8400-e29b-41d4-a716-446655440000",
  "my_status": "rejected",
  "final_status": "rejected",
  "message": "매칭 제안을 거절했습니다."
}
```

---

## 4. 메시지 API

### 4.1 내 메시지방 목록 조회

사용자가 참여 중인 매칭 메시지방 목록을 조회합니다.

**Endpoint**: `GET /matching/chats`

**Query Parameters**:
- `is_active`: `true` | `false` | `all` (default: `true`)

**Response** (200 OK):
```json
{
  "chat_rooms": [
    {
      "room_id": "990e8400-e29b-41d4-a716-446655440000",
      "room_name": "과팅 매칭 - 2025.12.12",
      "display_mode": "blind",
      "members_count": 8,
      "unread_count": 5,
      "last_message": {
        "content": "안녕하세요!",
        "sender_name": "A1",
        "created_at": "2025-12-12T14:00:00Z"
      },
      "created_at": "2025-12-12T13:34:54Z"
    }
  ],
  "total": 1
}
```

---

### 4.2 메시지방 상세 조회

특정 메시지방의 상세 정보를 조회합니다.

**Endpoint**: `GET /matching/chats/{room_id}`

**Response** (200 OK):
```json
{
  "room_id": "990e8400-e29b-41d4-a716-446655440000",
  "room_name": "과팅 매칭 - 2025.12.12",
  "display_mode": "blind",
  "group_a": {
    "department": "컴퓨터공학과",
    "grade": "3학년",
    "members": [
      {
        "user_id": "user-id-1",
        "display_name": "A1",
        "is_me": true
      },
      {
        "user_id": "user-id-2",
        "display_name": "A2",
        "is_me": false
      }
    ]
  },
  "group_b": {
    "department": "경영학과",
    "grade": "2학년",
    "members": [
      {
        "user_id": "user-id-5",
        "display_name": "B1",
        "is_me": false
      }
    ]
  },
  "created_at": "2025-12-12T13:34:54Z"
}
```

---

### 4.3 메시지 목록 조회

메시지방의 메시지 목록을 조회합니다.

**Endpoint**: `GET /matching/chats/{room_id}/messages`

**Query Parameters**:
- `limit`: 조회할 메시지 수 (default: 50, max: 100)
- `before`: 특정 메시지 이전 메시지 조회 (cursor)

**Response** (200 OK):
```json
{
  "messages": [
    {
      "message_id": "aa0e8400-e29b-41d4-a716-446655440000",
      "sender_id": "user-id-1",
      "sender_name": "A1",
      "message_type": "text",
      "content": "안녕하세요! 반갑습니다 😊",
      "created_at": "2025-12-12T14:00:00Z"
    },
    {
      "message_id": "bb0e8400-e29b-41d4-a716-446655440000",
      "sender_id": "user-id-5",
      "sender_name": "B1",
      "message_type": "text",
      "content": "네 반가워요!",
      "created_at": "2025-12-12T14:01:00Z"
    }
  ],
  "has_more": false,
  "next_cursor": null
}
```

---

### 4.4 메시지 전송

메시지방에 메시지를 전송합니다.

**Endpoint**: `POST /matching/chats/{room_id}/messages`

**Request Body**:
```json
{
  "message_type": "text",
  "content": "안녕하세요!",
  "attachments": []
}
```

**Response** (201 Created):
```json
{
  "message_id": "cc0e8400-e29b-41d4-a716-446655440000",
  "sender_id": "user-id-1",
  "sender_name": "A1",
  "message_type": "text",
  "content": "안녕하세요!",
  "created_at": "2025-12-12T14:05:00Z"
}
```

**Message Types**:
- `text`: 텍스트 메시지
- `image`: 이미지 메시지
- `system`: 시스템 메시지 (자동 생성)

---

### 4.5 메시지방 나가기

메시지방에서 나갑니다.

**Endpoint**: `POST /matching/chats/{room_id}/leave`

**Response** (200 OK):
```json
{
  "message": "메시지방에서 나갔습니다."
}
```

---

### 4.6 읽음 표시

메시지를 읽음 처리합니다.

**Endpoint**: `POST /matching/chats/{room_id}/read`

**Request Body**:
```json
{
  "last_read_message_id": "cc0e8400-e29b-41d4-a716-446655440000"
}
```

**Response** (200 OK):
```json
{
  "unread_count": 0,
  "last_read_at": "2025-12-12T14:10:00Z"
}
```

---

## 5. 관리자 API

### 5.1 대기 중인 인증 목록 조회

관리자가 검토 대기 중인 인증 신청을 조회합니다.

**Endpoint**: `GET /admin/verification/pending`

**Authorization**: Admin only

**Query Parameters**:
- `page`: 페이지 번호 (default: 1)
- `per_page`: 페이지당 항목 수 (default: 20)

**Response** (200 OK):
```json
{
  "verifications": [
    {
      "verification_id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "user-id-1",
      "user_name": "김철수",
      "school_name": "서울대학교",
      "department": "컴퓨터공학과",
      "grade": "3학년",
      "gender": "male",
      "documents": [
        "https://storage.example.com/docs/abc123.jpg"
      ],
      "submitted_at": "2025-12-12T10:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "per_page": 20,
  "total_pages": 1
}
```

---

### 5.2 인증 검토

관리자가 인증 신청을 승인/반려합니다.

**Endpoint**: `POST /admin/verification/{verification_id}/review`

**Authorization**: Admin only

**Request Body**:
```json
{
  "approved": true,
  "admin_note": "서류 확인 완료"
}
```

**Response** (200 OK):
```json
{
  "verification_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "approved",
  "verified_at": "2025-12-12T14:15:00Z",
  "message": "인증이 승인되었습니다."
}
```

---

### 5.3 매칭 통계 조회

관리자가 전체 매칭 통계를 조회합니다.

**Endpoint**: `GET /admin/matching/stats`

**Authorization**: Admin only

**Query Parameters**:
- `period`: `daily` | `weekly` | `monthly` (default: `weekly`)

**Response** (200 OK):
```json
{
  "period": "weekly",
  "total_pools_created": 150,
  "total_proposals_sent": 80,
  "total_matches_success": 45,
  "success_rate": 56.25,
  "average_match_time_hours": 18.5,
  "active_chat_rooms": 45,
  "by_match_type": {
    "any": 20,
    "same_department": 15,
    "major_category": 10
  }
}
```

---

### 5.4 신고 목록 조회

관리자가 신고 목록을 조회합니다.

**Endpoint**: `GET /admin/reports`

**Authorization**: Admin only

**Query Parameters**:
- `status`: `pending` | `resolved` | `all` (default: `pending`)
- `type`: `message` | `user` | `all` (default: `all`)

**Response** (200 OK):
```json
{
  "reports": [
    {
      "report_id": "dd0e8400-e29b-41d4-a716-446655440000",
      "reporter_id": "user-id-1",
      "reported_user_id": "user-id-5",
      "report_type": "message",
      "reason": "부적절한 메시지",
      "details": "욕설 사용",
      "evidence": {
        "message_id": "ee0e8400-e29b-41d4-a716-446655440000",
        "content": "..."
      },
      "status": "pending",
      "created_at": "2025-12-12T15:00:00Z"
    }
  ],
  "total": 5
}
```

---

### 5.5 신고 처리

관리자가 신고를 처리합니다.

**Endpoint**: `POST /admin/reports/{report_id}/resolve`

**Authorization**: Admin only

**Request Body**:
```json
{
  "action": "warn",
  "note": "경고 조치 완료"
}
```

**Action Types**:
- `dismiss`: 기각
- `warn`: 경고
- `suspend`: 정지 (7일)
- `ban`: 영구 차단

**Response** (200 OK):
```json
{
  "report_id": "dd0e8400-e29b-41d4-a716-446655440000",
  "status": "resolved",
  "action_taken": "warn",
  "resolved_at": "2025-12-12T15:30:00Z"
}
```

---

## 📊 WebSocket API

### 실시간 메시지

**Endpoint**: `ws://api.focusmate.com/ws/matching/chats/{room_id}`

**Connection**:
```javascript
const ws = new WebSocket('ws://api.focusmate.com/ws/matching/chats/{room_id}?token={jwt_token}');
```

**Client → Server (메시지 전송)**:
```json
{
  "type": "message",
  "content": "안녕하세요!",
  "message_type": "text"
}
```

**Server → Client (메시지 수신)**:
```json
{
  "type": "message",
  "message_id": "ff0e8400-e29b-41d4-a716-446655440000",
  "sender_id": "user-id-5",
  "sender_name": "B1",
  "content": "반가워요!",
  "created_at": "2025-12-12T16:00:00Z"
}
```

**Server → Client (타이핑 표시)**:
```json
{
  "type": "typing",
  "user_id": "user-id-5",
  "user_name": "B1",
  "is_typing": true
}
```

---

## 🔒 Rate Limiting

### 제한 정책

| Endpoint | Limit |
|----------|-------|
| POST /matching/pools | 3 / day |
| POST /matching/proposals/{id}/accept | 10 / hour |
| POST /matching/chats/{id}/messages | 60 / minute |
| GET /matching/* | 100 / minute |

### 응답 헤더
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1702389600
```

---

## 📝 에러 코드 목록

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `UNAUTHORIZED` | 401 | 인증 필요 |
| `FORBIDDEN` | 403 | 권한 없음 |
| `NOT_FOUND` | 404 | 리소스 없음 |
| `ALREADY_SUBMITTED` | 400 | 이미 제출됨 |
| `INVALID_MEMBER_COUNT` | 400 | 잘못된 멤버 수 |
| `UNVERIFIED_MEMBER` | 400 | 미인증 멤버 |
| `ALREADY_IN_POOL` | 400 | 이미 풀 등록 중 |
| `ALREADY_MATCHED` | 400 | 이미 매칭됨 |
| `EXPIRED` | 400 | 만료됨 |
| `RATE_LIMIT_EXCEEDED` | 429 | 요청 제한 초과 |
| `INTERNAL_ERROR` | 500 | 서버 오류 |

---

**문서 버전**: 1.0
**최종 수정일**: 2025-12-12
**다음 업데이트**: Phase 1 구현 후 실제 API 검증
