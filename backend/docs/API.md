# Focus Mate Backend - API Reference

Base URL: `http://localhost:8000/api/v1`

---

## Authentication & Profile

### Register User

```http
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepass123"
}

Response 201:
{
  "access_token": "eyJ0eXAiOiJKV1...",
  "user": {
    "id": "uuid",
    "email": "user@example.com",
    "username": "johndoe",
    "total_focus_time": 0,
    "total_sessions": 0,
    "is_verified": false
  }
}
```

### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepass123"
}

Response 200: (same as register)
```

### Get Profile

```http
GET /auth/profile/{user_id}

Response 200:
{
  "id": "uuid",
  "email": "user@example.com",
  "username": "johndoe",
  "bio": "Focus enthusiast",
  "total_focus_time": 1250,
  "total_sessions": 50,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### Update Profile

```http
PUT /auth/profile/{user_id}
Content-Type: application/json

{
  "username": "newname",
  "bio": "Updated bio"
}

Response 200: (updated user object)
```

---

## Rooms

### Create Room

```http
POST /rooms/
Content-Type: application/json

{
  "name": "Morning Focus Session",
  "work_duration": 25,
  "break_duration": 5,
  "auto_start_break": true
}

Response 201:
{
  "id": "uuid",
  "name": "Morning Focus Session",
  "work_duration": 25,
  "break_duration": 5,
  "auto_start_break": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

### List Rooms

```http
GET /rooms/

Response 200:
[
  {
    "id": "uuid",
    "name": "Morning Focus",
    "work_duration": 25,
    "break_duration": 5,
    "is_active": true
  }
]
```

### Get Room

```http
GET /rooms/{room_id}

Response 200: (room object)
```

### Update Room

```http
PUT /rooms/{room_id}
Content-Type: application/json

{
  "work_duration": 50,
  "break_duration": 10
}

Response 200: (updated room object)
```

### Delete Room

```http
DELETE /rooms/{room_id}

Response 200:
{
  "status": "deactivated",
  "room_id": "uuid"
}
```

---

## Timer

### Get Timer State

```http
GET /timer/{room_id}

Response 200:
{
  "id": "uuid",
  "room_id": "uuid",
  "status": "RUNNING",
  "phase": "WORK",
  "duration": 1500,
  "remaining_seconds": 847,
  "started_at": "2024-01-01T10:00:00Z",
  "paused_at": null
}
```

### Start Timer

```http
POST /timer/{room_id}/start

Response 200: (timer state)
```

### Pause Timer

```http
POST /timer/{room_id}/pause

Response 200: (timer state)
```

### Reset Timer

```http
POST /timer/{room_id}/reset

Response 200: (timer state with status=IDLE)
```

### Complete Phase

```http
POST /timer/{room_id}/complete

Response 200: (timer transitions to next phase)
```

---

## Participants

### Join Room

```http
POST /participants/join
Content-Type: application/json

{
  "room_id": "uuid",
  "user_id": "uuid"
}

Response 201:
{
  "id": "uuid",
  "room_id": "uuid",
  "user_id": "uuid",
  "status": "active",
  "joined_at": "2024-01-01T10:00:00Z"
}
```

### Leave Room

```http
POST /participants/leave
Content-Type: application/json

{
  "participant_id": "uuid"
}

Response 200:
{
  "status": "left",
  "participant_id": "uuid"
}
```

### List Participants

```http
GET /participants/{room_id}

Response 200:
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "status": "active",
    "joined_at": "2024-01-01T10:00:00Z"
  }
]
```

### Update Participant Status

```http
PUT /participants/{participant_id}/status
Content-Type: application/json

{
  "status": "idle"
}

Response 200: (participant object)
```

---

## Statistics

### Record Completed Session

```http
POST /stats/session
Content-Type: application/json

{
  "user_id": "uuid",
  "room_id": "uuid",
  "session_type": "work",
  "duration_minutes": 25
}

Response 201:
{
  "status": "recorded",
  "session_id": "uuid"
}
```

### Get User Stats

```http
GET /stats/user/{user_id}?days=7

Response 200:
{
  "total_focus_time": 1250,
  "total_sessions": 50,
  "average_session": 25,
  "sessions": [
    {
      "id": "uuid",
      "type": "work",
      "duration": 25,
      "completed_at": "2024-01-01T10:25:00Z"
    }
  ]
}
```

---

## Achievements

### Create Achievement

```http
POST /achievements/
Content-Type: application/json

{
  "name": "First Steps",
  "description": "Complete your first pomodoro session",
  "icon": "trophy",
  "category": "sessions",
  "requirement_type": "total_sessions",
  "requirement_value": 1,
  "points": 10
}

Response 201: (achievement object)
```

### List All Achievements

```http
GET /achievements/

Response 200: (array of achievements)
```

### List by Category

```http
GET /achievements/category/sessions

Response 200: (array of achievements in category)
```

### Get User Achievements

```http
GET /achievements/user/{user_id}

Response 200:
[
  {
    "id": "uuid",
    "user_id": "uuid",
    "achievement_id": "uuid",
    "unlocked_at": "2024-01-01T10:25:00Z",
    "progress": 1,
    "achievement": {
      "name": "First Steps",
      "description": "Complete your first pomodoro",
      "icon": "trophy",
      "points": 10
    }
  }
]
```

### Get Achievement Progress

```http
GET /achievements/user/{user_id}/progress

Response 200:
[
  {
    "achievement": {...},
    "is_unlocked": true,
    "progress": 50,
    "progress_percentage": 100.0,
    "unlocked_at": "2024-01-01T10:00:00Z"
  },
  {
    "achievement": {...},
    "is_unlocked": false,
    "progress": 25,
    "progress_percentage": 25.0,
    "unlocked_at": null
  }
]
```

### Check and Unlock Achievements

```http
POST /achievements/user/{user_id}/check

Response 200: (array of newly unlocked achievements)
```

---

## Community

### Create Post

```http
POST /community/posts?user_id={user_id}
Content-Type: application/json

{
  "title": "My productivity tips",
  "content": "Here are some tips that helped me...",
  "category": "tips"
}

Response 201:
{
  "id": "uuid",
  "user_id": "uuid",
  "title": "My productivity tips",
  "content": "Here are some tips...",
  "category": "tips",
  "likes": 0,
  "comment_count": 0,
  "is_pinned": false,
  "created_at": "2024-01-01T10:00:00Z",
  "author_username": "johndoe"
}
```

### List Posts

```http
GET /community/posts?category=tips&search=productivity&limit=20&offset=0

Response 200:
{
  "posts": [
    {
      "id": "uuid",
      "title": "My productivity tips",
      "category": "tips",
      "likes": 5,
      "comment_count": 3,
      "created_at": "2024-01-01T10:00:00Z",
      "author_username": "johndoe"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

### Get Post

```http
GET /community/posts/{post_id}

Response 200: (full post object)
```

### Update Post

```http
PUT /community/posts/{post_id}?user_id={user_id}
Content-Type: application/json

{
  "title": "Updated title",
  "content": "Updated content"
}

Response 200: (updated post object)
```

### Delete Post

```http
DELETE /community/posts/{post_id}?user_id={user_id}

Response 200:
{
  "status": "deleted",
  "post_id": "uuid"
}
```

### Toggle Post Like

```http
POST /community/posts/{post_id}/like?user_id={user_id}

Response 200:
{
  "success": true,
  "liked": true,
  "new_count": 6
}
```

### Create Comment

```http
POST /community/posts/{post_id}/comments?user_id={user_id}
Content-Type: application/json

{
  "content": "Great post!",
  "parent_comment_id": null
}

Response 201:
{
  "id": "uuid",
  "post_id": "uuid",
  "user_id": "uuid",
  "content": "Great post!",
  "parent_comment_id": null,
  "likes": 0,
  "created_at": "2024-01-01T10:05:00Z",
  "author_username": "johndoe"
}
```

### Get Post Comments

```http
GET /community/posts/{post_id}/comments

Response 200:
[
  {
    "id": "uuid",
    "content": "Great post!",
    "likes": 2,
    "author_username": "user1",
    "replies": [
      {
        "id": "uuid",
        "content": "Thanks!",
        "author_username": "author"
      }
    ]
  }
]
```

### Update Comment

```http
PUT /community/comments/{comment_id}?user_id={user_id}
Content-Type: application/json

{
  "content": "Updated comment text"
}

Response 200: (updated comment)
```

### Delete Comment

```http
DELETE /community/comments/{comment_id}?user_id={user_id}

Response 200:
{
  "status": "deleted",
  "comment_id": "uuid"
}
```

### Toggle Comment Like

```http
POST /community/comments/{comment_id}/like?user_id={user_id}

Response 200:
{
  "success": true,
  "liked": true,
  "new_count": 3
}
```

---

## Messaging

### Send Message

```http
POST /messages/send?sender_id={user_id}
Content-Type: application/json

{
  "receiver_id": "uuid",
  "content": "Hey, want to focus together?"
}

Response 201:
{
  "id": "uuid",
  "conversation_id": "uuid",
  "sender_id": "uuid",
  "receiver_id": "uuid",
  "content": "Hey, want to focus together?",
  "is_read": false,
  "created_at": "2024-01-01T10:00:00Z",
  "sender_username": "johndoe",
  "receiver_username": "janedoe"
}
```

### List Conversations

```http
GET /messages/conversations?user_id={user_id}

Response 200:
[
  {
    "id": "uuid",
    "other_user_id": "uuid",
    "other_user_username": "janedoe",
    "last_message": "Hey, want to focus together?",
    "last_message_at": "2024-01-01T10:00:00Z",
    "unread_count": 2
  }
]
```

### Get Conversation Detail

```http
GET /messages/conversations/{conversation_id}?user_id={user_id}&limit=50&offset=0

Response 200:
{
  "conversation": {
    "id": "uuid",
    "user1_id": "uuid",
    "user2_id": "uuid",
    "other_user_id": "uuid",
    "other_user_username": "janedoe",
    "last_message_at": "2024-01-01T10:00:00Z",
    "unread_count": 0
  },
  "messages": [
    {
      "id": "uuid",
      "content": "Hey, want to focus together?",
      "sender_id": "uuid",
      "is_read": true,
      "created_at": "2024-01-01T10:00:00Z",
      "sender_username": "johndoe"
    }
  ]
}
```

### Mark Messages as Read

```http
POST /messages/conversations/{conversation_id}/read?user_id={user_id}
Content-Type: application/json

{
  "message_ids": ["uuid1", "uuid2"]
}

Response 200:
{
  "marked_count": 2,
  "conversation_id": "uuid",
  "new_unread_count": 0
}
```

### Get Unread Count

```http
GET /messages/unread-count?user_id={user_id}

Response 200:
{
  "user_id": "uuid",
  "unread_count": 5
}
```

---

## WebSocket

### Connect to Room

```javascript
const ws = new WebSocket("ws://localhost:8000/api/v1/ws/{room_id}");

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Received:", data);
  // data.type: "timer_update", "participant_joined", etc.
};

ws.send(
  JSON.stringify({
    type: "ping",
    data: {},
  })
);
```

**Message Types**:

- `timer_update`: Timer state changed
- `participant_joined`: New participant joined
- `participant_left`: Participant left
- `phase_completed`: Timer phase completed

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Validation error for 'email': Email already registered"
}
```

### 401 Unauthorized

```json
{
  "detail": "Invalid email or password"
}
```

### 403 Forbidden

```json
{
  "detail": "You can only edit your own posts"
}
```

### 404 Not Found

```json
{
  "detail": "Post uuid not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

---

## Common Query Parameters

- `user_id`: User identifier (required for many operations)
- `limit`: Pagination limit (default: 20, max: 100)
- `offset`: Pagination offset (default: 0)
- `days`: Time range in days (default: 7)
- `category`: Filter by category
- `search`: Search query string

---

## Health Check

```http
GET /health

Response 200:
{
  "status": "healthy"
}
```

---

## Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Both provide:

- All endpoints with descriptions
- Request/response schemas
- Try-it-out functionality
- Schema models

---

**End of API Reference**
