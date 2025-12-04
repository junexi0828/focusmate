# System Architecture Document

# Team Pomodoro Timer (Focus Mate)

**문서 버전**: 1.0
**작성일**: 2025-12-04
**표준 준수**: ISO/IEC/IEEE 42010:2011

---

## 목차

1. [아키텍처 개요](#1-아키텍처-개요)
2. [아키텍처 뷰포인트](#2-아키텍처-뷰포인트)
3. [기술 스택 및 선택 근거](#3-기술-스택-및-선택-근거)
4. [데이터 모델](#4-데이터-모델)
5. [보안 아키텍처](#5-보안-아키텍처)
6. [확장성 및 성능](#6-확장성-및-성능)

---

## 1. 아키텍처 개요

### 1.1 아키텍처 목표

Focus Mate의 아키텍처는 다음 품질 속성을 최우선으로 설계되었습니다:

| 품질 속성      | 목표                    | 전략                                    |
| -------------- | ----------------------- | --------------------------------------- |
| **신뢰성**     | 99.9% 가용성            | 엄격한 타입 시스템, 90% 테스트 커버리지 |
| **유지보수성** | CC < 10, MI > 20        | 레이어드 아키텍처, 의존성 주입          |
| **성능**       | API < 200ms, WS < 100ms | 비동기 I/O, 경량 메시지 프로토콜        |
| **이식성**     | 단일 명령 배포          | Docker Compose, 환경 불가지론           |

### 1.2 아키텍처 스타일

- **주 패턴**: 클라이언트-서버 (Client-Server)
- **보조 패턴**: 이벤트 기반 (Event-Driven) - WebSocket을 통한 실시간 동기화
- **백엔드 패턴**: 레이어드 아키텍처 (Layered Architecture)
- **프론트엔드 패턴**: 컴포넌트 기반 (Component-Based) + Atomic Design

### 1.3 시스템 컨텍스트 다이어그램

```
┌─────────────────┐
│   Web Browser   │
│  (React SPA)    │
└────────┬────────┘
         │ HTTPS
         │ WebSocket
         ▼
┌─────────────────────────────────┐
│     FastAPI Backend Server      │
│  ┌───────────────────────────┐  │
│  │   API Layer (Routes)      │  │
│  └───────────┬───────────────┘  │
│              ▼                   │
│  ┌───────────────────────────┐  │
│  │   Service Layer (Logic)   │  │
│  └───────────┬───────────────┘  │
│              ▼                   │
│  ┌───────────────────────────┐  │
│  │  Repository Layer (Data)  │  │
│  └───────────┬───────────────┘  │
└──────────────┼──────────────────┘
               ▼
      ┌────────────────┐
      │  SQLite / PG   │
      │   Database     │
      └────────────────┘
```

---

## 2. 아키텍처 뷰포인트

### 2.1 논리적 뷰 (Logical View)

#### 2.1.1 백엔드 레이어 구조 (기능 단위 모듈화)

```
src/backend/app/
├── main.py                 # FastAPI 애플리케이션 진입점
│                           # - 라우터 등록 및 미들웨어 설정
│
├── routers/                # ⭐ 기능별 라우터 분리 (확장성)
│   ├── __init__.py
│   ├── rooms.py           # 방 관리 API (POST /rooms, GET /rooms/{id})
│   ├── timer.py           # 타이머 제어 API (POST /timer/start, pause, reset)
│   ├── participants.py    # 참여자 관리 API (GET /rooms/{id}/participants)
│   ├── websocket.py       # WebSocket 연결 관리 (WS /ws/{room_id})
│   └── chat.py            # 🔮 향후 확장: 채팅 기능 (POST /chat/message)
│
├── core/                   # Core Layer (설정, 보안)
│   ├── config.py          # 환경 설정
│   ├── security.py        # 인증/인가 (JWT)
│   ├── exceptions.py      # 커스텀 예외
│   └── dependencies.py    # 의존성 주입 (DB 세션 등)
│
├── schemas/                # API Schemas (Request/Response) - 기능별 분리
│   ├── __init__.py
│   ├── room.py            # RoomCreate, RoomResponse, RoomList
│   ├── timer.py           # TimerStart, TimerState, TimerUpdate
│   ├── participant.py     # ParticipantJoin, ParticipantList
│   └── common.py          # 공통 응답 포맷 (SuccessResponse, ErrorResponse)
│
├── services/               # Service Layer (비즈니스 로직) - 기능별 분리
│   ├── __init__.py
│   ├── room_service.py    # 방 생성, 조회, 수정, 삭제
│   ├── timer_service.py   # 타이머 시작, 일시정지, 재설정, 동기화
│   ├── participant_service.py  # 참여자 추가, 제거, 목록 조회
│   └── notification_service.py # 알림 발송 (브라우저, 이메일 등)
│
├── repositories/           # Repository Layer (데이터 액세스) - 인터페이스 기반
│   ├── __init__.py
│   ├── interfaces/        # 추상 인터페이스 (의존성 역전)
│   │   ├── room_repository_interface.py
│   │   ├── timer_repository_interface.py
│   │   └── participant_repository_interface.py
│   ├── implementations/   # SQLAlchemy 구현체
│   │   ├── room_repository.py
│   │   ├── timer_repository.py
│   │   └── participant_repository.py
│   └── base.py            # 공통 Repository 베이스 클래스
│
└── db/                     # Database
    ├── database.py        # DB 연결 관리 (SQLAlchemy 세션)
    ├── models.py          # SQLAlchemy ORM 모델 (독립적 설계)
    │                      # - 모델 간 직접 참조 최소화
    │                      # - Foreign Key는 DB 레벨에서만 관리
    └── migrations/        # Alembic 마이그레이션
```

**레이어 간 의존성 규칙**:

- **Router → Service → Repository Interface → Repository Implementation → DB**
- 상위 레이어는 하위 레이어에만 의존
- 하위 레이어는 상위 레이어를 알지 못함 (Dependency Inversion)
- **Repository는 Interface 기반**: 구현체 교체 용이 (예: SQLite → PostgreSQL, 향후 Redis 캐싱 추가)

**확장성 설계 원칙**:

1. **기능 추가 시**: `routers/chat.py`만 추가하면 됨 (기존 코드 수정 불필요)
2. **모듈 독립성**: 각 기능(room, timer, participant)은 독립적으로 테스트 가능
3. **의존성 역전**: Repository Interface로 DB 구현체 교체 용이

#### 2.1.2 프론트엔드 컴포넌트 구조 (Feature-based + Atomic Design 하이브리드)

```
src/frontend/src/
├── features/               # ⭐ 기능 단위 모듈화 (확장성)
│   ├── room/              # 방 관리 기능
│   │   ├── components/    # 기능별 컴포넌트
│   │   │   ├── CreateRoomCard.tsx
│   │   │   ├── JoinRoomCard.tsx
│   │   │   └── RoomSettingsDialog.tsx
│   │   ├── hooks/         # 기능별 훅
│   │   │   ├── useRoom.ts
│   │   │   └── useRoomSettings.ts
│   │   ├── stores/        # 기능별 상태 관리
│   │   │   └── roomStore.ts
│   │   ├── services/     # 기능별 API 클라이언트
│   │   │   └── roomService.ts
│   │   ├── types/         # 기능별 타입 정의
│   │   │   └── room.types.ts
│   │   └── index.ts       # Public API (외부 노출)
│   │
│   ├── timer/             # 타이머 기능
│   │   ├── components/
│   │   │   ├── TimerDisplay.tsx
│   │   │   └── TimerControls.tsx
│   │   ├── hooks/
│   │   │   ├── useTimer.ts
│   │   │   └── useWebSocket.ts
│   │   ├── stores/
│   │   │   └── timerStore.ts
│   │   ├── services/
│   │   │   └── timerService.ts
│   │   ├── types/
│   │   │   └── timer.types.ts
│   │   └── index.ts
│   │
│   ├── participants/      # 참여자 관리 기능
│   │   ├── components/
│   │   │   └── ParticipantList.tsx
│   │   ├── hooks/
│   │   │   └── useParticipants.ts
│   │   ├── services/
│   │   │   └── participantService.ts
│   │   ├── types/
│   │   │   └── participant.types.ts
│   │   └── index.ts
│   │
│   └── chat/              # 🔮 향후 확장: 채팅 기능
│       ├── components/
│       ├── hooks/
│       ├── stores/
│       └── index.ts
│
├── components/            # 공통 UI 컴포넌트 (Atomic Design)
│   ├── ui/               # 기본 UI 라이브러리 (Radix UI 래퍼)
│   │   ├── button.tsx
│   │   ├── input.tsx
│   │   ├── card.tsx
│   │   └── dialog.tsx
│   └── layout/           # 레이아웃 컴포넌트
│       ├── Header.tsx
│       └── Container.tsx
│
├── pages/                # 라우트 페이지 (Feature 조합)
│   ├── HomePage.tsx      # features/room 조합
│   ├── RoomPage.tsx      # features/timer + features/participants 조합
│   └── NotFoundPage.tsx
│
├── services/             # 공통 API 인프라
│   ├── api.ts           # Axios 인스턴스 (인터셉터, 에러 처리)
│   └── websocket.ts     # WebSocket 클라이언트
│
├── stores/               # 전역 상태 (선택적)
│   └── appStore.ts      # 앱 전역 설정 (테마, 언어 등)
│
└── utils/                # 유틸리티 함수
    ├── timeFormatter.ts
    ├── validators.ts
    └── constants.ts
```

**확장성 설계 원칙**:

1. **기능 추가 시**: `features/chat/` 폴더만 추가하면 됨 (기존 코드 수정 불필요)
2. **모듈 독립성**: 각 feature는 자체 컴포넌트, 훅, 스토어, 서비스를 포함
3. **Public API**: 각 feature의 `index.ts`로 외부 노출 인터페이스 제어
4. **재사용성**: 공통 UI는 `components/ui/`에서 관리 (Atomic Design 유지)

---

### 2.2 프로세스 뷰 (Process View)

#### 2.2.1 타이머 동기화 시퀀스

```
Client A          WebSocket Server       Timer Service       Database
   │                     │                     │                 │
   │──── Connect ───────>│                     │                 │
   │<─── Connected ──────│                     │                 │
   │                     │                     │                 │
   │─ Start Timer ──────>│                     │                 │
   │                     │── start_timer() ───>│                 │
   │                     │                     │── save_state ──>│
   │                     │<─── timer_state ────│                 │
   │<─ timer_update ─────│                     │                 │
   │                     │                     │                 │
   │                     │ [broadcast to all]  │                 │
   │                     │────────────────────>│                 │
Client B                 │                     │                 │
   │<─ timer_update ─────│                     │                 │
   │                     │                     │                 │
   │                     │  [every 1s tick]    │                 │
   │<─ timer_tick ───────│<─── broadcast ──────│                 │
```

**핵심 설계 원칙**:

1. **서버가 진실의 원천**: 클라이언트는 `target_timestamp`만 받아 로컬 계산
2. **이벤트 기반 업데이트**: 상태 변경 시에만 브로드캐스트 (대역폭 절약)
3. **재연결 복원력**: 연결 끊김 후 재접속 시 현재 상태 즉시 동기화

#### 2.2.2 WebSocket 메시지 프로토콜

**클라이언트 → 서버**:

```json
{
  "action": "start_timer",
  "room_id": "uuid-v4",
  "timestamp": "2025-12-04T10:00:00Z"
}
```

**서버 → 클라이언트**:

```json
{
  "event": "timer_update",
  "room_id": "uuid-v4",
  "data": {
    "status": "running",
    "session_type": "work",
    "target_timestamp": "2025-12-04T10:25:00Z",
    "started_at": "2025-12-04T10:00:00Z"
  }
}
```

---

### 2.3 배포 뷰 (Deployment View)

#### 2.3.1 Docker Compose 아키텍처

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Host                          │
│                                                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Frontend   │  │   Backend    │  │   Database   │  │
│  │   (Nginx)    │  │  (FastAPI)   │  │   (SQLite)   │  │
│  │   Port 3000  │  │   Port 8000  │  │   Volume     │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘  │
│         │                 │                  │          │
│         └─────────────────┴──────────────────┘          │
│                    bridge network                       │
└─────────────────────────────────────────────────────────┘
```

**docker-compose.yml 구조**:

```yaml
services:
  frontend:
    build: ./src/frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
    environment:
      - VITE_API_URL=http://backend:8000

  backend:
    build: ./src/backend
    ports:
      - "8000:8000"
    depends_on:
      - db
    environment:
      - DATABASE_URL=sqlite:///./data/focusmate.db
    volumes:
      - db-data:/app/data
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  db:
    # SQLite는 파일 기반이므로 별도 컨테이너 불필요
    # 프로덕션 시 PostgreSQL 추가
```

#### 2.3.2 헬스체크 및 의존성 관리

**백엔드 헬스체크 엔드포인트**:

```python
@app.get("/health")
async def health_check():
    """
    ISO 25010 가용성(Availability) 검증을 위한 헬스체크.
    """
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

---

### 2.4 데이터 뷰 (Data View)

#### 2.4.1 데이터베이스 스키마 (ERD) - 낮은 결합도 설계

```
┌─────────────────┐
│      rooms      │
├─────────────────┤
│ id (PK)         │ UUID (Primary Key)
│ name            │ VARCHAR(50) UNIQUE
│ work_duration   │ INTEGER (seconds)
│ break_duration  │ INTEGER (seconds)
│ created_at      │ TIMESTAMP
│ updated_at      │ TIMESTAMP
└─────────────────┘
         │
         │ (약한 결합: FK는 DB 레벨에서만)
         │ (애플리케이션 레벨에서는 UUID로 조인)
         │
         ▼
┌─────────────────┐
│  timer_sessions  │
├─────────────────┤
│ id (PK)         │ UUID
│ room_id (FK)    │ UUID (외래키, 인덱스)
│ session_type    │ ENUM('work', 'break')
│ started_at      │ TIMESTAMP
│ ended_at        │ TIMESTAMP (nullable)
│ target_time     │ TIMESTAMP
│ status          │ ENUM('running', 'paused', 'completed')
│ created_at      │ TIMESTAMP
└─────────────────┘
         │
         │ (독립적 설계: room 삭제 시 CASCADE 옵션)
         │
         ▼
┌─────────────────┐
│  participants   │
├─────────────────┤
│ id (PK)         │ UUID
│ room_id (FK)    │ UUID (외래키, 인덱스)
│ user_name       │ VARCHAR(50)
│ joined_at       │ TIMESTAMP
│ is_host         │ BOOLEAN DEFAULT FALSE
│ created_at      │ TIMESTAMP
└─────────────────┘
```

**낮은 결합도 설계 원칙**:

1. **UUID 기반 관계**: Foreign Key는 DB 레벨에서만 관리, 애플리케이션에서는 UUID로 조인
2. **독립적 모델**: 각 테이블은 자체 `created_at`, `updated_at` 보유
3. **CASCADE 옵션**: `ON DELETE CASCADE`는 선택적 (기본: `ON DELETE RESTRICT`)
4. **인덱스 전략**: `room_id`에 인덱스 추가로 조인 성능 최적화
5. **확장성**: 향후 `chat_messages` 테이블 추가 시 `room_id`만 참조하면 됨 (기존 모델 수정 불필요)

**Repository 인터페이스 예시**:

```python
# repositories/interfaces/room_repository_interface.py
from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

class IRoomRepository(ABC):
    """방 저장소 인터페이스 - 의존성 역전"""

    @abstractmethod
    async def create(self, room_data: dict) -> dict:
        """방 생성"""
        pass

    @abstractmethod
    async def get_by_id(self, room_id: UUID) -> Optional[dict]:
        """ID로 방 조회"""
        pass

    @abstractmethod
    async def delete(self, room_id: UUID) -> bool:
        """방 삭제"""
        pass

# repositories/implementations/room_repository.py
class RoomRepository(IRoomRepository):
    """SQLAlchemy 구현체"""
    def __init__(self, db: Session):
        self.db = db

    async def create(self, room_data: dict) -> dict:
        # SQLAlchemy ORM 사용
        pass
```

#### 2.4.2 Pydantic 모델 (Strict Mode)

```python
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr
from datetime import datetime
from enum import Enum

class SessionType(str, Enum):
    WORK = "work"
    BREAK = "break"

class TimerStatus(str, Enum):
    IDLE = "idle"
    RUNNING = "running"
    PAUSED = "paused"

class RoomCreate(BaseModel):
    """
    방 생성 요청 모델.
    ISO 25010 신뢰성 확보를 위해 Strict 모드 사용.
    """
    model_config = ConfigDict(strict=True)

    room_name: StrictStr = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern=r"^[a-zA-Z0-9_-]+$",
        description="방 이름 (영문, 숫자, 하이픈, 언더스코어만 허용)"
    )
    work_duration_minutes: StrictInt = Field(
        default=25,
        gt=0,
        le=60,
        description="집중 시간 (분)"
    )
    break_duration_minutes: StrictInt = Field(
        default=5,
        gt=0,
        le=30,
        description="휴식 시간 (분)"
    )

class TimerState(BaseModel):
    """타이머 상태 모델"""
    model_config = ConfigDict(strict=True)

    status: TimerStatus
    session_type: SessionType
    target_timestamp: datetime | None = None
    remaining_seconds: StrictInt = Field(ge=0)
```

---

## 3. 기술 스택 및 선택 근거

### 3.1 Architecture Decision Records (ADR)

#### ADR-001: FastAPI 선정

**날짜**: 2025-12-04
**상태**: 승인됨

**컨텍스트**:
백엔드 프레임워크로 Django, Flask, FastAPI를 검토했습니다.

**결정**:
FastAPI를 선택합니다.

**근거**:

1. **성능**: 비동기 I/O 네이티브 지원 (Starlette 기반)
2. **타입 안정성**: Pydantic 통합으로 런타임 검증 자동화
3. **문서화**: OpenAPI(Swagger) 자동 생성
4. **WebSocket**: 일급 시민(First-class) 지원
5. **ISO 25010 신뢰성**: 엄격한 데이터 검증으로 결함 최소화

**트레이드오프**:

- Django 대비 ORM 기능 부족 → SQLAlchemy로 보완
- 성숙도 낮음 → 활발한 커뮤니티로 상쇄

---

#### ADR-002: TypeScript Strict Mode

**날짜**: 2025-12-04
**상태**: 승인됨

**컨텍스트**:
프론트엔드에서 JavaScript vs TypeScript를 검토했습니다.

**결정**:
TypeScript strict 모드를 사용합니다.

**근거**:

1. **신뢰성**: 컴파일 타임 에러 검출로 런타임 오류 90% 감소
2. **유지보수성**: IDE 자동완성 및 리팩토링 지원
3. **ISO 25010 준수**: 타입 안정성 요구사항 충족

**설정**:

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true
  }
}
```

---

#### ADR-003: SQLite (개발) / PostgreSQL (프로덕션)

**날짜**: 2025-12-04
**상태**: 승인됨

**컨텍스트**:
데이터베이스 선택 시 개발 편의성과 프로덕션 안정성을 고려했습니다.

**결정**:

- 개발 환경: SQLite (파일 기반)
- 프로덕션: PostgreSQL (선택적)

**근거**:

1. **이식성**: SQLite는 별도 서버 불필요, Docker 환경에서 즉시 실행
2. **테스트 용이성**: 인메모리 DB로 빠른 테스트
3. **확장성**: SQLAlchemy ORM 사용으로 PostgreSQL 전환 용이

---

#### ADR-004: Zustand (상태 관리)

**날짜**: 2025-12-04
**상태**: 승인됨

**컨텍스트**:
Redux, MobX, Zustand, Jotai를 검토했습니다.

**결정**:
Zustand를 사용합니다.

**근거**:

1. **단순성**: 보일러플레이트 최소화 (Redux 대비 70% 코드 감소)
2. **성능**: 선택적 리렌더링 최적화
3. **TypeScript 지원**: 타입 추론 우수
4. **학습 곡선**: 낮은 진입 장벽

**예시**:

```typescript
import create from "zustand";

interface TimerStore {
  remainingSeconds: number;
  status: "idle" | "running" | "paused";
  startTimer: () => void;
}

export const useTimerStore = create<TimerStore>((set) => ({
  remainingSeconds: 1500,
  status: "idle",
  startTimer: () => set({ status: "running" }),
}));
```

---

## 4. 데이터 모델

### 4.1 도메인 모델

```
┌─────────────┐
│    Room     │
├─────────────┤
│ + id        │
│ + name      │
│ + settings  │
├─────────────┤
│ + start()   │
│ + pause()   │
│ + reset()   │
└──────┬──────┘
       │ has
       │ 1:1
       ▼
┌─────────────┐
│   Timer     │
├─────────────┤
│ + status    │
│ + target    │
│ + type      │
├─────────────┤
│ + tick()    │
│ + sync()    │
└─────────────┘
```

### 4.2 상태 전이 다이어그램

```
        ┌─────┐
        │ Idle│
        └──┬──┘
           │ start()
           ▼
        ┌─────────┐
    ┌───│ Running │◄──┐
    │   └─────────┘   │
    │ pause()    resume()
    ▼                 │
┌────────┐            │
│ Paused │────────────┘
└────┬───┘
     │ reset()
     ▼
  ┌─────┐
  │ Idle│
  └─────┘
```

---

## 5. 보안 아키텍처

### 5.1 위협 모델 (STRIDE)

| 위협                       | 완화 전략                          |
| -------------------------- | ---------------------------------- |
| **Spoofing** (위장)        | JWT 인증 (v1.1), 방 ID UUID 사용   |
| **Tampering** (변조)       | Pydantic Strict 검증, HTTPS 강제   |
| **Repudiation** (부인)     | 감사 로그 (v1.1)                   |
| **Information Disclosure** | 환경 변수 암호화, CORS 제한        |
| **Denial of Service**      | Rate Limiting, WebSocket 연결 제한 |
| **Elevation of Privilege** | 역할 기반 권한 (방장/참여자)       |

### 5.2 입력 검증 전략

**백엔드 (다층 방어)**:

```python
# Layer 1: Pydantic 스키마 검증
class RoomCreate(BaseModel):
    model_config = ConfigDict(strict=True)
    room_name: StrictStr = Field(pattern=r"^[a-zA-Z0-9_-]+$")

# Layer 2: 서비스 레이어 비즈니스 규칙 검증
def create_room(data: RoomCreate) -> Room:
    if room_exists(data.room_name):
        raise RoomAlreadyExistsError()
    # ...

# Layer 3: 데이터베이스 제약 조건
# SQLAlchemy 모델에 UNIQUE, NOT NULL 등
```

---

## 6. 확장성 및 성능

### 6.1 모듈화 전략 (Modularity)

#### 6.1.1 기능 추가 시나리오

**시나리오: 채팅 기능 추가**

**Backend**:

```python
# 1. 새 라우터 추가 (기존 코드 수정 없음)
# routers/chat.py
from fastapi import APIRouter
router = APIRouter(prefix="/chat", tags=["chat"])

@router.post("/messages")
async def send_message(...):
    pass

# 2. main.py에 등록만 추가
from routers import chat
app.include_router(chat.router)

# 3. 필요한 경우 새 서비스/리포지토리 추가
# services/chat_service.py
# repositories/implementations/chat_repository.py
```

**Frontend**:

```typescript
// 1. 새 feature 폴더 추가 (기존 코드 수정 없음)
// features/chat/
//   ├── components/ChatMessage.tsx
//   ├── hooks/useChat.ts
//   ├── stores/chatStore.ts
//   └── services/chatService.ts

// 2. RoomPage에서 import만 추가
import { ChatPanel } from "@/features/chat";

// 3. 기존 room, timer 기능과 독립적으로 동작
```

**Database**:

```sql
-- 1. 새 테이블 추가 (기존 테이블 수정 없음)
CREATE TABLE chat_messages (
    id UUID PRIMARY KEY,
    room_id UUID REFERENCES rooms(id) ON DELETE CASCADE,
    user_name VARCHAR(50),
    message TEXT,
    created_at TIMESTAMP
);

-- 2. room_id 인덱스만 추가 (기존 모델 영향 없음)
CREATE INDEX idx_chat_room_id ON chat_messages(room_id);
```

#### 6.1.2 모듈 독립성 원칙

| 원칙            | 설명                                  | 예시                                      |
| :-------------- | :------------------------------------ | :---------------------------------------- |
| **단일 책임**   | 각 모듈은 하나의 기능만 담당          | `routers/timer.py`는 타이머 제어만        |
| **의존성 역전** | 인터페이스에 의존, 구현체는 교체 가능 | `IRoomRepository` → `RoomRepository`      |
| **약한 결합**   | 모듈 간 직접 참조 최소화              | UUID로 조인, Foreign Key는 DB 레벨만      |
| **높은 응집도** | 관련 코드는 같은 모듈에               | `features/timer/`에 모든 타이머 관련 코드 |

### 6.2 수평 확장 전략 (v2.0)

```
        ┌─────────────┐
        │ Load Balancer│
        └──────┬───────┘
               │
       ┌───────┴───────┐
       ▼               ▼
┌────────────┐  ┌────────────┐
│ Backend 1  │  │ Backend 2  │
└─────┬──────┘  └─────┬──────┘
      │               │
      └───────┬───────┘
              ▼
        ┌──────────┐
        │  Redis   │ ← WebSocket 세션 공유
        └──────────┘
```

**모듈화의 이점**:

- 각 서버 인스턴스가 독립적으로 기능 모듈 로드 가능
- 특정 기능만 스케일 아웃 가능 (예: 타이머 서버만 확장)

### 6.3 성능 최적화

**백엔드**:

- 비동기 I/O (AsyncIO)
- 데이터베이스 연결 풀링
- 쿼리 최적화 (N+1 문제 방지)
- **모듈별 지연 로딩**: 사용하지 않는 라우터는 메모리에 로드하지 않음

**프론트엔드**:

- 코드 스플리팅 (Lazy Loading) - Feature 단위
- 메모이제이션 (React.memo, useMemo)
- 가상 스크롤 (참여자 목록)
- **Feature 기반 번들링**: 각 feature를 별도 청크로 분리

---

## 7. 모니터링 및 관찰성 (v1.1)

### 7.1 메트릭 수집

- **애플리케이션**: Prometheus + Grafana
- **로그**: Structured Logging (JSON)
- **추적**: OpenTelemetry (선택적)

### 7.2 핵심 메트릭

- API 응답 시간 (p50, p95, p99)
- WebSocket 연결 수
- 활성 방 수
- 에러율

---

## 8. 부록

### 8.1 용어집

- **Session**: 하나의 포모도로 사이클 (집중 + 휴식)
- **Room**: 팀원들이 타이머를 공유하는 가상 공간
- **Sync**: 클라이언트와 서버 간 타이머 상태 동기화

### 8.2 참조

- [SRS.md](./SRS.md): 요구사항 명세서
- [API_SPECIFICATION.md](./API_SPECIFICATION.md): API 문서
- [ADR/](./ADR/): 아키텍처 결정 기록

---

**문서 끝**
