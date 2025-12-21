---
id: ARC-019
title: Architecture Modularity Guide
version: 1.0
status: Approved
date: 2025-12-04
author: Focus Mate Team
category: Architecture
---

# Architecture Modularity Guide

## [Home](../README.md) > [Architecture](./README.md) > ARC-019

---


**문서 버전**: 1.0
**작성일**: 2025-12-04
**목적**: 기능 추가 시 기존 코드 수정 최소화를 위한 모듈화 전략

---

## 1. 핵심 원칙

### 1.1 모듈 독립성 (Module Independence)

각 기능 모듈은 다음을 자체 포함:

- **Backend**: Router → Service → Repository → DB Model
- **Frontend**: Components → Hooks → Stores → Services → Types

### 1.2 의존성 방향 (Dependency Direction)

```
Router → Service → Repository Interface → Repository Implementation → DB
```

- 상위 레이어는 하위 레이어에만 의존
- 인터페이스를 통한 의존성 역전

### 1.3 확장 시나리오

**예시: 채팅 기능 추가**

1. **Backend**: `routers/chat.py` 추가 → `main.py`에 등록만
2. **Frontend**: `features/chat/` 폴더 추가 → `RoomPage`에서 import만
3. **Database**: `chat_messages` 테이블 추가 (기존 테이블 수정 없음)

---

## 2. Backend 모듈화

### 2.1 라우터 구조

```python
# routers/rooms.py
from fastapi import APIRouter, Depends
from services.room_service import RoomService
from schemas.room import RoomCreate, RoomResponse

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("", response_model=RoomResponse)
async def create_room(
    data: RoomCreate,
    service: RoomService = Depends()
):
    return await service.create_room(data)

# main.py
from routers import rooms, timer, participants, websocket

app.include_router(rooms.router)
app.include_router(timer.router)
app.include_router(participants.router)
app.include_router(websocket.router)
```

### 2.2 Repository 인터페이스 패턴

```python
# repositories/interfaces/room_repository_interface.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

class IRoomRepository(ABC):
    @abstractmethod
    async def create(self, room_data: dict) -> dict:
        pass

    @abstractmethod
    async def get_by_id(self, room_id: UUID) -> Optional[dict]:
        pass

# repositories/implementations/room_repository.py
from repositories.interfaces.room_repository_interface import IRoomRepository

class RoomRepository(IRoomRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create(self, room_data: dict) -> dict:
        # SQLAlchemy 구현
        pass
```

**장점**: SQLite → PostgreSQL 전환 시 구현체만 교체

---

## 3. Frontend 모듈화

### 3.1 Feature 구조

```
features/timer/
├── components/
│   ├── TimerDisplay.tsx
│   └── TimerControls.tsx
├── hooks/
│   ├── useTimer.ts
│   └── useWebSocket.ts
├── stores/
│   └── timerStore.ts
├── services/
│   └── timerService.ts
├── types/
│   └── timer.types.ts
└── index.ts  # Public API
```

### 3.2 Public API 패턴

```typescript
// features/timer/index.ts
export { TimerDisplay, TimerControls } from "./components";
export { useTimer, useWebSocket } from "./hooks";
export { useTimerStore } from "./stores";
export type { TimerStatus, SessionType } from "./types";

// pages/RoomPage.tsx
import { TimerDisplay, TimerControls, useTimer } from "@/features/timer";
```

**장점**: 외부에서 feature 내부 구조를 알 필요 없음

---

## 4. Database 낮은 결합도

### 4.1 UUID 기반 관계

```python
# ❌ Bad: ORM 관계 직접 참조
class TimerSession(Base):
    room = relationship("Room", back_populates="timers")  # 강한 결합

# ✅ Good: UUID로 조인
class TimerSession(Base):
    room_id: UUID  # Foreign Key는 DB 레벨에서만
    # 애플리케이션에서는 UUID로 조인
```

### 4.2 독립적 모델 설계

```sql
-- 각 테이블은 자체 created_at, updated_at 보유
CREATE TABLE rooms (
    id UUID PRIMARY KEY,
    name VARCHAR(50) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE timer_sessions (
    id UUID PRIMARY KEY,
    room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW(),  -- 독립적
    updated_at TIMESTAMP DEFAULT NOW()
);
```

**장점**: 새 테이블 추가 시 기존 모델 수정 불필요

---

## 5. 확장 체크리스트

새 기능 추가 시:

- [ ] Backend: `routers/{feature}.py` 추가
- [ ] Backend: `services/{feature}_service.py` 추가
- [ ] Backend: `repositories/implementations/{feature}_repository.py` 추가
- [ ] Backend: `schemas/{feature}.py` 추가
- [ ] Frontend: `features/{feature}/` 폴더 추가
- [ ] Frontend: `features/{feature}/index.ts`로 Public API 정의
- [ ] Database: 새 테이블 추가 (기존 테이블 수정 없음)
- [ ] `main.py`에 라우터 등록만 추가
- [ ] 기존 코드 수정 없음 확인

---

**문서 끝**
