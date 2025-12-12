# 랭킹전 시스템 API 명세서

## 📋 목차
1. [인증 API](#인증-api)
2. [팀 관리 API](#팀-관리-api)
3. [세션 API](#세션-api)
4. [미니게임 API](#미니게임-api)
5. [리더보드 API](#리더보드-api)
6. [관리자 API](#관리자-api)

---

## 인증 API

### 학교 인증 요청
```http
POST /api/ranking/verification/request
```

**Request Body**:
```json
{
  "team_id": "uuid",
  "documents": [
    {
      "type": "student_id",
      "url": "https://...",
      "user_id": "uuid"
    },
    {
      "type": "affiliation_proof",
      "url": "https://..."
    }
  ],
  "team_member_list": [
    {
      "user_id": "uuid",
      "name": "홍길동",
      "student_id": "2021123456"
    }
  ]
}
```

**Response**:
```json
{
  "request_id": "uuid",
  "status": "pending",
  "submitted_at": "2025-01-12T10:00:00Z",
  "message": "인증 요청이 제출되었습니다."
}
```

---

### 인증 상태 조회
```http
GET /api/ranking/verification/status/{team_id}
```

**Response**:
```json
{
  "team_id": "uuid",
  "verification_status": "verified",
  "request_id": "uuid",
  "submitted_at": "2025-01-12T10:00:00Z",
  "reviewed_at": "2025-01-13T15:30:00Z",
  "admin_note": "승인 완료"
}
```

---

## 팀 관리 API

### 팀 생성
```http
POST /api/ranking/teams
```

**Request Body**:
```json
{
  "team_name": "코딩마스터즈",
  "team_type": "department",
  "mini_game_enabled": true,
  "affiliation_info": {
    "university": "서울대학교",
    "department": "컴퓨터공학과"
  }
}
```

**Response**:
```json
{
  "team_id": "uuid",
  "team_name": "코딩마스터즈",
  "team_type": "department",
  "verification_status": "none",
  "leader_id": "uuid",
  "invite_code": "ABC123",
  "created_at": "2025-01-12T10:00:00Z"
}
```

---

### 팀원 초대
```http
POST /api/ranking/teams/{team_id}/invite
```

**Request Body**:
```json
{
  "email": "user@example.com"
}
```

**Response**:
```json
{
  "invitation_id": "uuid",
  "team_id": "uuid",
  "email": "user@example.com",
  "status": "pending",
  "expires_at": "2025-01-19T10:00:00Z"
}
```

---

### 초대 수락
```http
POST /api/ranking/teams/invitations/{invitation_id}/accept
```

**Response**:
```json
{
  "member_id": "uuid",
  "team_id": "uuid",
  "user_id": "uuid",
  "role": "member",
  "joined_at": "2025-01-12T11:00:00Z"
}
```

---

### 팀 정보 조회
```http
GET /api/ranking/teams/{team_id}
```

**Response**:
```json
{
  "team_id": "uuid",
  "team_name": "코딩마스터즈",
  "team_type": "department",
  "verification_status": "verified",
  "mini_game_enabled": true,
  "leader": {
    "user_id": "uuid",
    "name": "홍길동",
    "email": "leader@example.com"
  },
  "members": [
    {
      "user_id": "uuid",
      "name": "김철수",
      "role": "member",
      "joined_at": "2025-01-12T11:00:00Z"
    }
  ],
  "stats": {
    "total_study_time": 48.5,
    "current_streak": 7,
    "mini_game_score": 350
  },
  "created_at": "2025-01-12T10:00:00Z"
}
```

---

### 팀 목록 조회
```http
GET /api/ranking/teams?type={team_type}&status={verification_status}
```

**Query Parameters**:
- `type`: `general` | `department` | `lab` | `club`
- `status`: `none` | `pending` | `verified` | `rejected`
- `page`: 페이지 번호 (기본: 1)
- `limit`: 페이지 크기 (기본: 20)

**Response**:
```json
{
  "teams": [
    {
      "team_id": "uuid",
      "team_name": "코딩마스터즈",
      "team_type": "department",
      "member_count": 4,
      "verification_status": "verified"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 50,
    "total_pages": 3
  }
}
```

---

### 팀 설정 수정
```http
PATCH /api/ranking/teams/{team_id}
```

**Request Body**:
```json
{
  "team_name": "새로운 팀명",
  "mini_game_enabled": false
}
```

---

### 팀원 제명
```http
DELETE /api/ranking/teams/{team_id}/members/{user_id}
```

---

### 팀 탈퇴
```http
POST /api/ranking/teams/{team_id}/leave
```

---

## 세션 API

### 랭킹전 세션 시작
```http
POST /api/ranking/sessions/start
```

**Request Body**:
```json
{
  "team_id": "uuid",
  "duration_minutes": 25,
  "session_type": "work"
}
```

**Response**:
```json
{
  "session_id": "uuid",
  "team_id": "uuid",
  "user_id": "uuid",
  "duration_minutes": 25,
  "session_type": "work",
  "started_at": "2025-01-12T14:00:00Z"
}
```

---

### 세션 완료
```http
POST /api/ranking/sessions/{session_id}/complete
```

**Request Body**:
```json
{
  "actual_duration": 25,
  "success": true
}
```

**Response**:
```json
{
  "session_id": "uuid",
  "completed_at": "2025-01-12T14:25:00Z",
  "team_stats_updated": true,
  "mini_game_available": true
}
```

---

### 팀 세션 통계
```http
GET /api/ranking/teams/{team_id}/sessions/stats?period={period}
```

**Query Parameters**:
- `period`: `daily` | `weekly` | `monthly` | `all_time`

**Response**:
```json
{
  "team_id": "uuid",
  "period": "weekly",
  "total_study_time": 48.5,
  "total_sessions": 45,
  "average_per_member": 12.1,
  "daily_breakdown": [
    {
      "date": "2025-01-06",
      "total_hours": 6.5,
      "sessions": 8
    }
  ]
}
```

---

## 미니게임 API

### 게임 시작
```http
POST /api/ranking/mini-games/start
```

**Request Body**:
```json
{
  "team_id": "uuid",
  "game_type": "quiz"
}
```

**Response**:
```json
{
  "game_id": "uuid",
  "game_type": "quiz",
  "game_data": {
    "question": "포모도로 기법의 기본 집중 시간은?",
    "options": ["15분", "25분", "50분", "60분"],
    "time_limit": 30
  },
  "started_at": "2025-01-12T14:30:00Z"
}
```

---

### 게임 제출
```http
POST /api/ranking/mini-games/{game_id}/submit
```

**Request Body**:
```json
{
  "answer": "25분",
  "completion_time": 12.5
}
```

**Response**:
```json
{
  "game_id": "uuid",
  "success": true,
  "score": 15,
  "bonus": 5,
  "total_score": 20,
  "correct_answer": "25분",
  "team_total_score": 370
}
```

---

### 게임 기록 조회
```http
GET /api/ranking/teams/{team_id}/mini-games?period={period}
```

**Response**:
```json
{
  "team_id": "uuid",
  "period": "weekly",
  "total_score": 350,
  "games_played": 28,
  "success_rate": 0.85,
  "recent_games": [
    {
      "game_id": "uuid",
      "game_type": "quiz",
      "user_id": "uuid",
      "score": 20,
      "success": true,
      "played_at": "2025-01-12T14:30:00Z"
    }
  ]
}
```

---

## 리더보드 API

### 순공부시간 랭킹
```http
GET /api/ranking/leaderboard/study-time?period={period}&limit={limit}
```

**Query Parameters**:
- `period`: `weekly` | `monthly` | `all_time`
- `limit`: 순위 개수 (기본: 100)

**Response**:
```json
{
  "ranking_type": "study_time",
  "period": "weekly",
  "updated_at": "2025-01-12T15:00:00Z",
  "leaderboard": [
    {
      "rank": 1,
      "team_id": "uuid",
      "team_name": "코딩마스터즈",
      "team_type": "department",
      "total_hours": 52.3,
      "member_count": 4,
      "average_hours": 13.1,
      "rank_change": 0
    },
    {
      "rank": 2,
      "team_id": "uuid",
      "team_name": "알고리즘킹",
      "team_type": "department",
      "total_hours": 48.7,
      "member_count": 4,
      "average_hours": 12.2,
      "rank_change": 1
    }
  ]
}
```

---

### 연속 성공 랭킹
```http
GET /api/ranking/leaderboard/streak?limit={limit}
```

**Response**:
```json
{
  "ranking_type": "streak",
  "updated_at": "2025-01-12T15:00:00Z",
  "leaderboard": [
    {
      "rank": 1,
      "team_id": "uuid",
      "team_name": "코딩마스터즈",
      "team_type": "department",
      "current_streak": 14,
      "longest_streak": 21,
      "streak_status": "active",
      "rank_change": 0
    }
  ]
}
```

---

### 미니게임 랭킹
```http
GET /api/ranking/leaderboard/mini-game?period={period}&limit={limit}
```

**Response**:
```json
{
  "ranking_type": "mini_game",
  "period": "weekly",
  "updated_at": "2025-01-12T15:00:00Z",
  "leaderboard": [
    {
      "rank": 1,
      "team_id": "uuid",
      "team_name": "코딩마스터즈",
      "team_type": "department",
      "total_score": 450,
      "games_played": 32,
      "success_rate": 0.87,
      "average_score": 14.1,
      "rank_change": 2
    }
  ]
}
```

---

### 내 팀 순위 조회
```http
GET /api/ranking/teams/{team_id}/rank
```

**Response**:
```json
{
  "team_id": "uuid",
  "rankings": {
    "study_time": {
      "weekly": {
        "rank": 2,
        "total_teams": 50,
        "percentile": 96
      },
      "monthly": {
        "rank": 5,
        "total_teams": 120,
        "percentile": 95.8
      }
    },
    "streak": {
      "rank": 1,
      "total_teams": 50,
      "percentile": 100
    },
    "mini_game": {
      "weekly": {
        "rank": 3,
        "total_teams": 45,
        "percentile": 93.3
      }
    }
  }
}
```

---

## 관리자 API

### 인증 요청 목록
```http
GET /api/admin/ranking/verification/requests?status={status}
```

**Query Parameters**:
- `status`: `pending` | `approved` | `rejected` | `all`

**Response**:
```json
{
  "requests": [
    {
      "request_id": "uuid",
      "team_id": "uuid",
      "team_name": "코딩마스터즈",
      "team_type": "department",
      "submitted_at": "2025-01-12T10:00:00Z",
      "status": "pending",
      "documents_count": 5
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 15
  }
}
```

---

### 인증 승인/반려
```http
POST /api/admin/ranking/verification/{request_id}/review
```

**Request Body**:
```json
{
  "status": "approved",
  "admin_note": "서류 확인 완료"
}
```

**Response**:
```json
{
  "request_id": "uuid",
  "team_id": "uuid",
  "status": "approved",
  "reviewed_at": "2025-01-13T15:30:00Z",
  "admin_note": "서류 확인 완료"
}
```

---

### 팀 통계 조회 (관리자)
```http
GET /api/admin/ranking/teams/{team_id}/stats
```

**Response**:
```json
{
  "team_id": "uuid",
  "team_name": "코딩마스터즈",
  "detailed_stats": {
    "total_study_time": 248.5,
    "total_sessions": 245,
    "total_mini_game_score": 1850,
    "member_breakdown": [
      {
        "user_id": "uuid",
        "name": "홍길동",
        "study_time": 65.2,
        "sessions": 68,
        "mini_game_score": 480
      }
    ]
  }
}
```

---

## WebSocket 이벤트

### 실시간 순위 업데이트
```javascript
// 구독
socket.emit('subscribe_leaderboard', {
  ranking_type: 'study_time',
  period: 'weekly'
});

// 수신
socket.on('leaderboard_update', (data) => {
  console.log(data);
  // {
  //   ranking_type: 'study_time',
  //   period: 'weekly',
  //   updated_teams: [
  //     { team_id: 'uuid', rank: 2, total_hours: 48.7 }
  //   ]
  // }
});
```

---

### 팀 활동 알림
```javascript
// 구독
socket.emit('subscribe_team', {
  team_id: 'uuid'
});

// 수신
socket.on('team_activity', (data) => {
  console.log(data);
  // {
  //   type: 'session_completed',
  //   user_id: 'uuid',
  //   user_name: '홍길동',
  //   duration: 25,
  //   team_total_hours: 48.5
  // }
});
```

---

## 에러 코드

| 코드 | 메시지 | 설명 |
|------|--------|------|
| `TEAM_001` | Team not found | 팀을 찾을 수 없음 |
| `TEAM_002` | Insufficient members | 최소 인원 미달 (4명) |
| `TEAM_003` | Already in team | 이미 다른 팀에 소속 |
| `TEAM_004` | Not team leader | 팀장 권한 필요 |
| `VERIFY_001` | Verification pending | 인증 대기 중 |
| `VERIFY_002` | Verification required | 인증 필요 |
| `VERIFY_003` | Invalid documents | 서류 오류 |
| `GAME_001` | Game not available | 게임 불가 시간 |
| `GAME_002` | Already played | 이미 참여함 |
| `GAME_003` | Time expired | 시간 초과 |

---

**작성일**: 2025-01-12
**버전**: 1.0
