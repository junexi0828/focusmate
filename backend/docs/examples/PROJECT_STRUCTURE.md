# Focus Mate Backend - Project Structure

## 📐 Architecture Principles

이 프로젝트는 다음 원칙을 기반으로 설계되었습니다:

1. **Feature-Based Modularity**: 기능별로 완전히 독립된 모듈 구조
2. **Domain-Driven Design (DDD)**: 비즈니스 도메인 중심 설계
3. **Hexagonal Architecture**: 포트와 어댑터 패턴으로 외부 의존성 격리
4. **SOLID Principles**: 객체지향 설계 원칙 준수
5. **Clean Architecture**: 의존성 방향 제어 (외부 → 내부)

---

## 🏗️ Directory Structure

```
backend/
├── app/                                    # 애플리케이션 루트
│   ├── main.py                            # FastAPI 애플리케이션 진입점
│   ├── __init__.py
│   │
│   ├── api/                               # API Layer (외부 인터페이스)
│   │   ├── __init__.py
│   │   ├── deps.py                        # 공통 의존성 (DB 세션, 인증 등)
│   │   │
│   │   └── v1/                            # API 버전 1
│   │       ├── __init__.py
│   │       ├── router.py                  # v1 메인 라우터 통합
│   │       │
│   │       └── endpoints/                 # 기능별 엔드포인트
│   │           ├── __init__.py
│   │           │
│   │           ├── rooms.py              # 방 관리 API
│   │           ├── timer.py              # 타이머 제어 API
│   │           ├── participants.py       # 참여자 관리 API
│   │           ├── websocket.py          # WebSocket 연결
│   │           │
│   │           ├── community.py          # 🔮 커뮤니티 (게시판) API
│   │           ├── posts.py              # 🔮 게시글 API
│   │           ├── comments.py           # 🔮 댓글 API
│   │           │
│   │           ├── messages.py           # 🔮 1:1 메시지 API
│   │           ├── conversations.py      # 🔮 대화 스레드 API
│   │           │
│   │           ├── stats.py              # 🔮 통계 API
│   │           ├── achievements.py       # 🔮 업적 시스템 API
│   │           │
│   │           ├── users.py              # 🔮 사용자 관리 API
│   │           ├── profiles.py           # 🔮 프로필 API
│   │           ├── auth.py               # 🔮 인증/인가 API
│   │           │
│   │           ├── notifications.py      # 🔮 알림 API
│   │           └── settings.py           # 🔮 사용자 설정 API
│   │
│   ├── core/                              # Core Layer (기본 인프라)
│   │   ├── __init__.py
│   │   ├── config.py                     # 환경 설정 (Pydantic Settings)
│   │   ├── security.py                   # 보안 (JWT, 비밀번호 해싱)
│   │   ├── exceptions.py                 # 커스텀 예외
│   │   ├── logging.py                    # 로깅 설정
│   │   ├── events.py                     # 이벤트 시스템 (Pub/Sub)
│   │   └── middleware.py                 # 미들웨어 (CORS, 로깅 등)
│   │
│   ├── domain/                            # Domain Layer (비즈니스 로직)
│   │   ├── __init__.py
│   │   │
│   │   ├── room/                         # 방 관리 도메인
│   │   │   ├── __init__.py
│   │   │   ├── models.py                 # 도메인 모델 (Pydantic)
│   │   │   ├── schemas.py                # Request/Response 스키마
│   │   │   ├── service.py                # 비즈니스 로직
│   │   │   ├── repository.py             # Repository 인터페이스
│   │   │   ├── events.py                 # 도메인 이벤트
│   │   │   └── exceptions.py             # 도메인 예외
│   │   │
│   │   ├── timer/                        # 타이머 도메인
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   ├── state_machine.py          # 타이머 상태 머신
│   │   │   ├── synchronizer.py           # 타이머 동기화 로직
│   │   │   └── events.py
│   │   │
│   │   ├── participant/                  # 참여자 도메인
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   └── repository.py
│   │   │
│   │   ├── community/                    # 🔮 커뮤니티 도메인
│   │   │   ├── __init__.py
│   │   │   ├── post/
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── service.py
│   │   │   │   └── repository.py
│   │   │   └── comment/
│   │   │       ├── models.py
│   │   │       ├── schemas.py
│   │   │       ├── service.py
│   │   │       └── repository.py
│   │   │
│   │   ├── messaging/                    # 🔮 메시징 도메인
│   │   │   ├── __init__.py
│   │   │   ├── conversation/
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── service.py
│   │   │   │   └── repository.py
│   │   │   └── message/
│   │   │       ├── models.py
│   │   │       ├── schemas.py
│   │   │       ├── service.py
│   │   │       └── repository.py
│   │   │
│   │   ├── stats/                        # 🔮 통계 도메인
│   │   │   ├── __init__.py
│   │   │   ├── session/
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── service.py
│   │   │   │   └── repository.py
│   │   │   ├── achievement/
│   │   │   │   ├── models.py
│   │   │   │   ├── schemas.py
│   │   │   │   ├── service.py
│   │   │   │   └── repository.py
│   │   │   └── analytics/
│   │   │       ├── models.py
│   │   │       ├── schemas.py
│   │   │       └── service.py
│   │   │
│   │   ├── user/                         # 🔮 사용자 도메인
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── profile/
│   │   │       ├── models.py
│   │   │       ├── schemas.py
│   │   │       ├── service.py
│   │   │       └── repository.py
│   │   │
│   │   ├── notification/                 # 🔮 알림 도메인
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── schemas.py
│   │   │   ├── service.py
│   │   │   ├── repository.py
│   │   │   └── channels/                 # 알림 채널 (이메일, 푸시, 브라우저)
│   │   │       ├── __init__.py
│   │   │       ├── email.py
│   │   │       ├── push.py
│   │   │       └── browser.py
│   │   │
│   │   └── shared/                       # 공유 도메인 (여러 도메인에서 사용)
│   │       ├── __init__.py
│   │       ├── models.py                 # 공통 도메인 모델
│   │       ├── schemas.py                # 공통 스키마
│   │       ├── value_objects.py          # Value Objects (Email, UUID 등)
│   │       └── enums.py                  # 공통 Enum
│   │
│   ├── infrastructure/                    # Infrastructure Layer (외부 시스템)
│   │   ├── __init__.py
│   │   │
│   │   ├── database/                     # 데이터베이스
│   │   │   ├── __init__.py
│   │   │   ├── session.py                # SQLAlchemy 세션 관리
│   │   │   ├── base.py                   # Base ORM 클래스
│   │   │   ├── migrations/               # Alembic 마이그레이션
│   │   │   │   ├── env.py
│   │   │   │   ├── script.py.mako
│   │   │   │   └── versions/
│   │   │   │
│   │   │   └── models/                   # SQLAlchemy ORM 모델
│   │   │       ├── __init__.py
│   │   │       ├── room.py
│   │   │       ├── timer.py
│   │   │       ├── participant.py
│   │   │       ├── user.py
│   │   │       ├── post.py
│   │   │       ├── comment.py
│   │   │       ├── message.py
│   │   │       ├── conversation.py
│   │   │       ├── session_history.py
│   │   │       ├── achievement.py
│   │   │       ├── notification.py
│   │   │       └── user_settings.py
│   │   │
│   │   ├── repositories/                 # Repository 구현체
│   │   │   ├── __init__.py
│   │   │   ├── base.py                   # Base Repository (CRUD)
│   │   │   ├── room_repository.py
│   │   │   ├── timer_repository.py
│   │   │   ├── participant_repository.py
│   │   │   ├── user_repository.py
│   │   │   ├── post_repository.py
│   │   │   ├── comment_repository.py
│   │   │   ├── message_repository.py
│   │   │   ├── conversation_repository.py
│   │   │   ├── session_history_repository.py
│   │   │   ├── achievement_repository.py
│   │   │   ├── notification_repository.py
│   │   │   └── user_settings_repository.py
│   │   │
│   │   ├── cache/                        # 캐시 (Redis)
│   │   │   ├── __init__.py
│   │   │   ├── client.py                 # Redis 클라이언트
│   │   │   ├── room_cache.py             # 방 상태 캐싱
│   │   │   └── session_cache.py          # 세션 캐싱
│   │   │
│   │   ├── websocket/                    # WebSocket 관리
│   │   │   ├── __init__.py
│   │   │   ├── manager.py                # Connection Manager
│   │   │   ├── room_manager.py           # 방별 연결 관리
│   │   │   └── message_broker.py         # 메시지 브로커 (Redis Pub/Sub)
│   │   │
│   │   ├── external/                     # 외부 서비스
│   │   │   ├── __init__.py
│   │   │   ├── email/                    # 이메일 서비스
│   │   │   │   ├── __init__.py
│   │   │   │   ├── smtp.py
│   │   │   │   └── templates/
│   │   │   ├── storage/                  # 파일 스토리지 (S3, 로컬)
│   │   │   │   ├── __init__.py
│   │   │   │   ├── local.py
│   │   │   │   └── s3.py
│   │   │   └── push/                     # 푸시 알림 (FCM, APNs)
│   │   │       ├── __init__.py
│   │   │       ├── fcm.py
│   │   │       └── apns.py
│   │   │
│   │   └── monitoring/                   # 모니터링 및 로깅
│   │       ├── __init__.py
│   │       ├── metrics.py                # Prometheus 메트릭
│   │       ├── tracing.py                # OpenTelemetry 추적
│   │       └── health.py                 # Health Check
│   │
│   ├── application/                       # Application Layer (Use Cases)
│   │   ├── __init__.py
│   │   │
│   │   ├── room/                         # 방 관리 유스케이스
│   │   │   ├── __init__.py
│   │   │   ├── create_room.py
│   │   │   ├── join_room.py
│   │   │   ├── leave_room.py
│   │   │   ├── update_room_settings.py
│   │   │   └── delete_room.py
│   │   │
│   │   ├── timer/                        # 타이머 유스케이스
│   │   │   ├── __init__.py
│   │   │   ├── start_timer.py
│   │   │   ├── pause_timer.py
│   │   │   ├── resume_timer.py
│   │   │   ├── reset_timer.py
│   │   │   └── sync_timer.py
│   │   │
│   │   ├── community/                    # 🔮 커뮤니티 유스케이스
│   │   │   ├── __init__.py
│   │   │   ├── create_post.py
│   │   │   ├── update_post.py
│   │   │   ├── delete_post.py
│   │   │   ├── create_comment.py
│   │   │   └── like_post.py
│   │   │
│   │   ├── messaging/                    # 🔮 메시징 유스케이스
│   │   │   ├── __init__.py
│   │   │   ├── send_message.py
│   │   │   ├── create_conversation.py
│   │   │   └── mark_as_read.py
│   │   │
│   │   ├── stats/                        # 🔮 통계 유스케이스
│   │   │   ├── __init__.py
│   │   │   ├── record_session.py
│   │   │   ├── calculate_stats.py
│   │   │   └── unlock_achievement.py
│   │   │
│   │   └── user/                         # 🔮 사용자 유스케이스
│   │       ├── __init__.py
│   │       ├── register_user.py
│   │       ├── login_user.py
│   │       ├── update_profile.py
│   │       └── change_password.py
│   │
│   ├── shared/                            # Shared (공통 유틸리티)
│   │   ├── __init__.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── datetime.py               # 날짜/시간 유틸리티
│   │   │   ├── validators.py             # 커스텀 검증
│   │   │   ├── pagination.py             # 페이지네이션
│   │   │   └── response.py               # 공통 응답 생성
│   │   │
│   │   ├── constants/
│   │   │   ├── __init__.py
│   │   │   ├── error_codes.py            # 에러 코드 상수
│   │   │   └── defaults.py               # 기본값 상수
│   │   │
│   │   └── types/
│   │       ├── __init__.py
│   │       ├── common.py                 # 공통 타입 정의
│   │       └── protocols.py              # Protocol 정의 (인터페이스)
│   │
│   └── cli/                               # CLI 도구 (관리 명령)
│       ├── __init__.py
│       ├── seed.py                        # 데이터 시딩
│       ├── migrate.py                     # 마이그레이션 실행
│       └── admin.py                       # 관리자 작업
│
├── tests/                                 # 테스트
│   ├── __init__.py
│   ├── conftest.py                        # Pytest 설정 및 Fixture
│   │
│   ├── unit/                              # 단위 테스트
│   │   ├── __init__.py
│   │   ├── domain/
│   │   │   ├── test_room_service.py
│   │   │   ├── test_timer_service.py
│   │   │   └── test_timer_state_machine.py
│   │   └── shared/
│   │       └── test_validators.py
│   │
│   ├── integration/                       # 통합 테스트
│   │   ├── __init__.py
│   │   ├── api/
│   │   │   ├── test_room_api.py
│   │   │   ├── test_timer_api.py
│   │   │   └── test_websocket.py
│   │   └── repositories/
│   │       ├── test_room_repository.py
│   │       └── test_timer_repository.py
│   │
│   ├── e2e/                               # E2E 테스트
│   │   ├── __init__.py
│   │   ├── test_room_lifecycle.py
│   │   └── test_timer_synchronization.py
│   │
│   └── fixtures/                          # 테스트 데이터
│       ├── __init__.py
│       ├── rooms.py
│       ├── users.py
│       └── sessions.py
│
├── scripts/                               # 유틸리티 스크립트
│   ├── seed_data.py                       # 개발 데이터 생성
│   ├── run_tests.sh                       # 테스트 실행
│   ├── check_quality.sh                   # 품질 검사
│   └── generate_openapi.py                # OpenAPI 스펙 생성
│
├── docs/                                  # API 문서 (로컬)
│   ├── api/
│   │   └── openapi.json
│   └── examples/
│       ├── room_creation.md
│       └── timer_control.md
│
├── alembic.ini                            # Alembic 설정
├── pyproject.toml                         # Poetry 설정 (의존성 관리)
├── requirements.txt                       # Pip 의존성 (Docker용)
├── requirements-dev.txt                   # 개발 의존성
├── Dockerfile                             # Docker 이미지
├── docker-compose.yml                     # 로컬 개발 환경
├── .env.example                           # 환경 변수 템플릿
├── .gitignore
├── pytest.ini                             # Pytest 설정
├── mypy.ini                               # Mypy 설정
├── ruff.toml                              # Ruff 설정
└── README.md                              # 백엔드 README
```

---

## 🎯 Module Design Patterns

### 1. Domain Module Structure (도메인 모듈 구조)

각 도메인은 다음 구조를 따릅니다:

```python
domain/{domain_name}/
├── __init__.py
├── models.py          # 도메인 모델 (Pydantic, 비즈니스 규칙 포함)
├── schemas.py         # API 스키마 (Request/Response DTO)
├── service.py         # 비즈니스 로직 (서비스 계층)
├── repository.py      # Repository 인터페이스 (Protocol)
├── events.py          # 도메인 이벤트
└── exceptions.py      # 도메인 특화 예외
```

**예시: Room Domain**

```python
# domain/room/models.py
from pydantic import BaseModel, Field, ConfigDict

class Room(BaseModel):
    """도메인 모델 - 비즈니스 규칙 포함"""
    model_config = ConfigDict(strict=True)

    id: str
    name: str = Field(min_length=3, max_length=50)
    work_duration: int = Field(ge=1, le=60)
    break_duration: int = Field(ge=1, le=30)

    def can_start_timer(self) -> bool:
        """타이머를 시작할 수 있는지 검증"""
        return self.work_duration > 0

# domain/room/repository.py
from typing import Protocol

class RoomRepositoryInterface(Protocol):
    """Repository 인터페이스 - 구현체와 분리"""
    async def create(self, room: Room) -> Room: ...
    async def get_by_id(self, room_id: str) -> Room | None: ...
```

### 2. API Endpoint Structure (엔드포인트 구조)

```python
# api/v1/endpoints/rooms.py
from fastapi import APIRouter, Depends
from app.domain.room.schemas import RoomCreate, RoomResponse
from app.application.room.create_room import CreateRoomUseCase

router = APIRouter(prefix="/rooms", tags=["rooms"])

@router.post("/", response_model=RoomResponse)
async def create_room(
    data: RoomCreate,
    use_case: CreateRoomUseCase = Depends()
):
    """방 생성 엔드포인트"""
    return await use_case.execute(data)
```

### 3. Use Case Structure (유스케이스 구조)

```python
# application/room/create_room.py
from app.domain.room.models import Room
from app.domain.room.repository import RoomRepositoryInterface

class CreateRoomUseCase:
    """방 생성 유스케이스 - 단일 책임"""

    def __init__(self, repository: RoomRepositoryInterface):
        self.repository = repository

    async def execute(self, data: RoomCreate) -> Room:
        """유스케이스 실행"""
        room = Room(**data.model_dump())
        return await self.repository.create(room)
```

---

## 🔌 Integration Points (통합 지점)

### 1. Web Client Integration (웹 클라이언트)
- **REST API**: `/api/v1/*`
- **WebSocket**: `/ws/{room_id}`
- **CORS**: 프론트엔드 도메인 허용

### 2. Desktop Client Integration (데스크톱 GUI)
- **REST API**: 동일한 엔드포인트 사용
- **WebSocket**: 실시간 동기화 지원
- **Authentication**: JWT 토큰 기반
- **Electron/Tauri 호환**: CORS 우회 설정

### 3. Mobile App Integration (향후)
- **REST API**: 동일한 엔드포인트
- **Push Notifications**: FCM/APNs 통합
- **Offline Mode**: 로컬 캐시 + 동기화

---

## 📦 Key Dependencies

### Production
- `fastapi>=0.115.0` - 웹 프레임워크
- `pydantic>=2.10.0` - 데이터 검증 (strict mode)
- `sqlalchemy>=2.0.0` - ORM (async)
- `alembic>=1.13.0` - 마이그레이션
- `redis>=5.0.0` - 캐시 및 Pub/Sub
- `python-jose[cryptography]` - JWT
- `passlib[bcrypt]` - 비밀번호 해싱
- `websockets>=12.0` - WebSocket
- `prometheus-client` - 메트릭

### Development
- `pytest>=8.0.0` - 테스트 프레임워크
- `pytest-asyncio` - 비동기 테스트
- `pytest-cov` - 커버리지
- `mypy>=1.11.0` - 타입 체킹 (strict)
- `ruff>=0.6.0` - Linter + Formatter
- `httpx` - HTTP 클라이언트 (테스트용)

---

## 🚀 Scalability Strategy

### Horizontal Scaling
- **Stateless API**: 서버 인스턴스 무제한 확장
- **Redis Pub/Sub**: WebSocket 메시지 브로드캐스트
- **Load Balancer**: Nginx/HAProxy

### Database Scaling
- **Read Replicas**: 읽기 부하 분산
- **Connection Pooling**: SQLAlchemy 풀 관리
- **Sharding**: 사용자 ID 기반 (향후)

### Caching Strategy
- **Room State**: Redis (TTL 1시간)
- **User Sessions**: Redis (TTL 24시간)
- **API Response**: HTTP Cache-Control 헤더

---

## 📝 Development Workflow

### 1. 새 기능 추가 (예: Community)
```bash
# 1. 도메인 모듈 생성
mkdir -p app/domain/community/{post,comment}

# 2. Repository 생성
touch app/infrastructure/repositories/post_repository.py

# 3. Use Case 생성
touch app/application/community/create_post.py

# 4. API 엔드포인트 생성
touch app/api/v1/endpoints/community.py

# 5. 테스트 작성
touch tests/unit/domain/test_post_service.py
```

### 2. 마이그레이션
```bash
# 마이그레이션 생성
alembic revision --autogenerate -m "Add community tables"

# 마이그레이션 적용
alembic upgrade head
```

### 3. 품질 검사
```bash
# 타입 체킹
mypy app/ --strict

# Linting
ruff check app/

# 테스트
pytest --cov=app --cov-report=html
```

---

## 🔐 Security Considerations

- **SQL Injection**: SQLAlchemy 파라미터화 쿼리
- **XSS**: Pydantic 자동 이스케이핑
- **CSRF**: SameSite 쿠키 (향후)
- **Rate Limiting**: Redis 기반 (향후)
- **Input Validation**: Pydantic strict mode

---

## 📊 Monitoring & Observability

- **Metrics**: Prometheus (API 응답 시간, 에러율)
- **Tracing**: OpenTelemetry (분산 추적)
- **Logging**: Structured JSON 로그
- **Health Check**: `/health` 엔드포인트
- **Database Monitoring**: SQLAlchemy 쿼리 로깅

---

## 🎓 Learning Resources

- [FastAPI Best Practices](https://fastapi.tiangolo.com/tutorial/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/)
- [SQLAlchemy 2.0 Tutorial](https://docs.sqlalchemy.org/)
- [Clean Architecture](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [DDD in Python](https://www.cosmicpython.com/)

🔮 **Legend**: 아이콘이 있는 모듈은 향후 구현 예정
