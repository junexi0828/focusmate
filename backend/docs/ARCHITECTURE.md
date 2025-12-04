# Focus Mate Backend - Architecture

## Overview

Complete backend implementation for Focus Mate - a Pomodoro focus application with social features. Built with FastAPI, SQLAlchemy 2.0, and async/await patterns following Domain-Driven Design principles.

---

## Architecture Principles

This project is designed based on the following principles:

1. **Feature-Based Modularity**: Functionality organized into independent modules
2. **Domain-Driven Design (DDD)**: Business domain-centric design
3. **Hexagonal Architecture**: Port and adapter pattern to isolate external dependencies
4. **SOLID Principles**: Object-oriented design principles
5. **Clean Architecture**: Dependency direction control (external → internal)

---

## Design Patterns

- **Domain-Driven Design (DDD)**: Business logic isolated in domain layer
- **Hexagonal Architecture**: Clear separation between domain, infrastructure, and API layers
- **Repository Pattern**: Data access abstraction
- **Dependency Injection**: FastAPI's built-in DI system
- **Server-Authoritative State**: Timer calculations on backend to prevent client tampering

---

## Technology Stack

- **Framework**: FastAPI 0.115+ with async/await
- **ORM**: SQLAlchemy 2.0 async
- **Database**: SQLite (development), PostgreSQL-ready
- **Authentication**: JWT with python-jose, bcrypt password hashing
- **Real-time**: WebSocket for timer sync and notifications
- **Validation**: Pydantic V2 with strict mode

---

## Project Structure

```
backend/
├── app/                                    # Application root
│   ├── main.py                            # FastAPI application entry point
│   │
│   ├── api/                               # API Layer (external interface)
│   │   ├── deps.py                        # Common dependencies (DB session, auth)
│   │   └── v1/                            # API version 1
│   │       ├── router.py                  # v1 main router aggregation
│   │       └── endpoints/                 # Feature-specific endpoints
│   │           ├── auth.py                 # Authentication & Profile
│   │           ├── rooms.py               # Room management
│   │           ├── timer.py               # Timer control
│   │           ├── participants.py       # Participant management
│   │           ├── stats.py               # Statistics
│   │           ├── achievements.py        # Achievements
│   │           ├── community.py           # Posts & Comments
│   │           ├── messaging.py           # 1:1 Messages
│   │           └── websocket.py          # WebSocket
│   │
│   ├── core/                              # Core Layer (basic infrastructure)
│   │   ├── config.py                    # Environment settings (Pydantic Settings)
│   │   ├── security.py                   # Security (JWT, password hashing)
│   │   └── exceptions.py                 # Custom exceptions
│   │
│   ├── domain/                            # Domain Layer (business logic)
│   │   ├── user/                          # User domain
│   │   ├── room/                          # Room domain
│   │   ├── timer/                         # Timer domain
│   │   ├── participant/                  # Participant domain
│   │   ├── stats/                         # Statistics domain
│   │   ├── achievement/                  # Achievement domain
│   │   ├── community/                     # Community domain
│   │   └── messaging/                     # Messaging domain
│   │
│   ├── infrastructure/                    # Infrastructure Layer (external systems)
│   │   ├── database/                      # Database
│   │   │   ├── session.py                 # SQLAlchemy session management
│   │   │   ├── base.py                   # Base ORM class
│   │   │   ├── migrations/               # Alembic migrations
│   │   │   └── models/                   # SQLAlchemy ORM models
│   │   ├── repositories/                 # Repository implementations
│   │   ├── websocket/                     # WebSocket management
│   │   │   └── manager.py                 # Connection Manager
│   │   └── external/                      # External services
│   │       ├── email/                     # Email service
│   │       ├── storage/                   # File storage
│   │       └── push/                      # Push notifications
│   │
│   └── shared/                            # Shared utilities
│       ├── utils/                         # Utility functions
│       ├── constants/                     # Constants
│       └── types/                         # Type definitions
│
├── tests/                                 # Tests
│   ├── unit/                              # Unit tests
│   ├── integration/                       # Integration tests
│   └── e2e/                               # E2E tests
│
├── scripts/                               # Utility scripts
├── docs/                                  # Documentation
└── alembic/                               # DB migrations
```

---

## Module Design Patterns

### Domain Module Structure

Each domain follows this structure:

```
domain/{domain_name}/
├── __init__.py
├── schemas.py         # API schemas (Request/Response DTO)
├── service.py         # Business logic (service layer)
└── (submodules)       # Domain-specific submodules
```

**Example: Room Domain**

- `schemas.py`: `RoomCreate`, `RoomUpdate`, `RoomResponse`
- `service.py`: Room business logic (create, get, update, delete)
- Repository interface defined in infrastructure layer

### API Endpoint Structure

```python
# api/v1/endpoints/rooms.py
from fastapi import APIRouter, Depends
from app.domain.room.schemas import RoomCreate, RoomResponse
from app.domain.room.service import RoomService

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("/", response_model=RoomResponse)
async def create_room(
    data: RoomCreate,
    service: RoomService = Depends(get_room_service),
):
    """Create room endpoint"""
    return await service.create_room(data)
```

---

## Database Schema

### Core Models

| Model           | Primary Key | Key Fields                                                         | Purpose                    |
| --------------- | ----------- | ------------------------------------------------------------------ | -------------------------- |
| User            | id (str)    | email, username, hashed_password, total_focus_time, total_sessions | User accounts and stats    |
| Room            | id (str)    | name, work_duration, break_duration, is_active                     | Focus rooms                |
| Timer           | id (str)    | room_id, status, phase, remaining_seconds, started_at              | Server-authoritative timer |
| Participant     | id (str)    | room_id, user_id, status                                           | Room participants          |
| SessionHistory  | id (str)    | user_id, room_id, session_type, duration_minutes, completed_at     | Completed pomodoros        |
| Achievement     | id (str)    | name, category, requirement_type, requirement_value                | Achievement definitions    |
| UserAchievement | id (str)    | user_id, achievement_id, unlocked_at, progress                     | User unlocks               |
| Post            | id (str)    | user_id, title, content, category, likes, comment_count            | Forum posts                |
| Comment         | id (str)    | post_id, user_id, content, parent_comment_id, likes                | Post comments              |
| Conversation    | id (str)    | user1_id, user2_id, last_message_at, unread_counts                 | 1:1 chat threads           |
| Message         | id (str)    | conversation_id, sender_id, receiver_id, content, is_read          | Chat messages              |

### Database Features

- **Timestamps**: All models use `TimestampMixin` (created_at, updated_at)
- **Soft Deletes**: `is_deleted` flag for posts/comments
- **Indexes**: Strategic indexes on foreign keys and frequently queried fields
- **Timezone Aware**: All timestamps use `DateTime(timezone=True)`

---

## Implemented Features

### 1. User Authentication & Profile

- User registration with email/username/password
- Login with JWT token generation
- Password hashing with bcrypt
- Profile management (username, bio)
- User statistics tracking

### 2. Room Management

- Create focus rooms with custom durations
- Configurable work/break durations (default: 25min/5min)
- Auto-start break option
- Room listing and search

### 3. Timer System (Server-Authoritative)

- Server-side timer state management
- Real-time remaining seconds calculation
- State machine: IDLE → RUNNING → PAUSED → COMPLETED
- Phase management: WORK → BREAK
- Automatic phase transitions

### 4. Participant Management

- Join/leave rooms
- Track participant status (active/idle)
- List room participants

### 5. Session History & Statistics

- Record completed pomodoro sessions
- Track work vs break sessions
- Calculate total focus time and session count
- Time-range filtering (last 7/30/90 days)

### 6. Achievement System (Gamification)

- Define achievements with requirements
- Categories: sessions, time, streak, social
- Automatic unlock detection
- Progress tracking
- Points system

### 7. Community Forum

- Create, read, update, delete posts
- Nested comments with replies
- Like/unlike posts and comments
- Category filtering
- Full-text search in titles and content
- Pagination support

### 8. Messaging System (1:1 Chat)

- 1:1 conversations between users
- Send/receive messages
- Unread message tracking per conversation
- Mark messages as read
- Message pagination
- Automatic conversation creation

### 9. WebSocket Real-time Sync

- Real-time timer updates
- Participant join/leave notifications
- Room state synchronization
- Per-room connection management

---

## API Endpoint Summary

### Total Endpoints: 43

- **Authentication (4)**: Register, Login, Profile Get/Update
- **Rooms (5)**: List, Create, Get, Update, Delete
- **Timer (5)**: State, Start, Pause, Reset, Complete
- **Participants (3)**: Join, Leave, List
- **Stats (2)**: Record Session, Get User Stats
- **Achievements (6)**: Create, List All, List by Category, User Achievements, Progress, Check/Unlock
- **Community Posts (6)**: Create, List, Get, Update, Delete, Like
- **Community Comments (5)**: Create, List, Update, Delete, Like
- **Messaging (5)**: Send, List Conversations, Get Conversation, Mark Read, Unread Count
- **WebSocket (1)**: Room connection
- **Health (1)**: GET /health

---

## Security Features

### Authentication

- JWT tokens with configurable expiration
- Bcrypt password hashing (12 rounds)
- Email uniqueness validation
- Secret key from environment variables

### Authorization

- User-only operations (update/delete own posts/comments)
- Token-based API access (ready for middleware)

### Input Validation

- Pydantic strict mode
- Field length limits
- Pattern validation (email, session_type)
- SQL injection protection (parameterized queries)

---

## Performance Optimizations

### Database

- Strategic indexes on foreign keys
- Batch loading prevention with eager loading options
- Connection pooling with async sessions
- Query result pagination

### Caching Ready

- Repository pattern enables easy caching layer
- Redis configuration included in docker-compose

### WebSocket

- Per-room connection pools
- Efficient broadcast to room participants only

---

## Scalability Strategy

### Horizontal Scaling

- **Stateless API**: Server instances can scale infinitely
- **Redis Pub/Sub**: WebSocket message broadcasting
- **Load Balancer**: Nginx/HAProxy

### Database Scaling

- **Read Replicas**: Distribute read load
- **Connection Pooling**: SQLAlchemy pool management
- **Sharding**: User ID-based (future)

### Caching Strategy

- **Room State**: Redis (TTL 1 hour)
- **User Sessions**: Redis (TTL 24 hours)
- **API Response**: HTTP Cache-Control headers

---

## Architecture Decisions

### Why Async/Await?

- Modern Python best practice
- Better performance for I/O operations
- Native FastAPI support
- Scales well with WebSocket connections

### Why Server-Authoritative Timer?

- Prevents client-side tampering
- Ensures fair session tracking
- Centralized state management
- Easier to debug and maintain

### Why Repository Pattern?

- Testability (easy to mock)
- Flexibility (swap data sources)
- Clean separation of concerns
- Caching layer integration point

### Why Feature-Based Structure?

- Scalability (add features without modifying existing)
- Team collaboration (work on different features in parallel)
- Clarity (everything related in one place)
- Modularity (features can be extracted to microservices)

---

## Monitoring & Observability

- **Metrics**: Prometheus (API response time, error rate)
- **Tracing**: OpenTelemetry (distributed tracing)
- **Logging**: Structured JSON logs
- **Health Check**: `/health` endpoint
- **Database Monitoring**: SQLAlchemy query logging

---

## Key Dependencies

### Production

- `fastapi>=0.115.0` - Web framework
- `pydantic>=2.10.0` - Data validation (strict mode)
- `sqlalchemy>=2.0.0` - ORM (async)
- `alembic>=1.13.0` - Migrations
- `python-jose[cryptography]` - JWT
- `passlib[bcrypt]` - Password hashing
- `websockets>=12.0` - WebSocket

### Development

- `pytest>=8.0.0` - Test framework
- `pytest-asyncio` - Async tests
- `mypy>=1.11.0` - Type checking (strict)
- `ruff>=0.6.0` - Linter + Formatter

---

## Common Issues & Solutions

### Issue: Database locked (SQLite)

**Solution**: Use PostgreSQL for production, or enable WAL mode for SQLite

### Issue: JWT token expired

**Solution**: Check JWT_EXPIRE_MINUTES in .env, implement refresh tokens

### Issue: WebSocket disconnects

**Solution**: Implement ping/pong heartbeat, reconnection logic on frontend

### Issue: CORS errors

**Solution**: Add frontend URL to CORS_ORIGINS in .env

---

## Performance Benchmarks (Target)

- API Response Time: < 100ms (average)
- WebSocket Latency: < 50ms
- Database Query Time: < 50ms
- Concurrent Users: 1000+ with proper scaling
- WebSocket Connections: 100+ per room

---

## Production Readiness Checklist

- [ ] Environment variables properly configured
- [ ] Database migrations generated and tested
- [ ] PostgreSQL configured (replace SQLite)
- [ ] JWT middleware added to protected endpoints
- [ ] Rate limiting implemented
- [ ] Logging configured (structured logging)
- [ ] Error tracking (Sentry integration)
- [ ] Health checks implemented
- [ ] Monitoring (Prometheus + Grafana)
- [ ] HTTPS/TLS configured
- [ ] Database backups scheduled
- [ ] CI/CD pipeline configured
- [ ] Load testing completed
- [ ] Security audit performed
- [ ] Documentation finalized

---

**End of Architecture Documentation**
