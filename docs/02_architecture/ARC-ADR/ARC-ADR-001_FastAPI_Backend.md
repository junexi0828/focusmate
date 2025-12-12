# ADR-001: FastAPI 백엔드 프레임워크 선정

**날짜**: 2025-12-04
**상태**: 승인됨
**결정자**: Architecture Team

---

## 컨텍스트 (Context)

Team Pomodoro Timer 프로젝트의 백엔드 프레임워크를 선택해야 합니다. 주요 요구사항은 다음과 같습니다:

1. **실시간 통신**: WebSocket 지원 필수
2. **타입 안정성**: ISO 25010 신뢰성 확보를 위한 엄격한 데이터 검증
3. **성능**: 비동기 I/O 지원으로 다수의 동시 접속 처리
4. **개발 생산성**: 자동 문서화 및 빠른 개발 사이클
5. **유지보수성**: 명확한 코드 구조 및 낮은 학습 곡선

---

## 결정 (Decision)

**FastAPI**를 백엔드 프레임워크로 선택합니다.

---

## 근거 (Rationale)

### 1. Pydantic 통합 (타입 안정성)

FastAPI는 Pydantic을 기본으로 사용하여 런타임 데이터 검증을 자동화합니다.

```python
from pydantic import BaseModel, ConfigDict, Field, StrictInt

class TimerSettings(BaseModel):
    model_config = ConfigDict(strict=True)
    work_duration: StrictInt = Field(gt=0, le=3600)
```

**장점**:

- 잘못된 데이터 타입 자동 차단
- ISO 25010 신뢰성 요구사항 충족
- 런타임 에러 90% 감소 (예상)

### 2. 비동기 I/O (성능)

Starlette 기반으로 ASGI를 네이티브 지원합니다.

```python
@app.get("/rooms/{room_id}")
async def get_room(room_id: str, db: AsyncSession = Depends(get_db)):
    room = await db.get(Room, room_id)
    return room
```

**벤치마크** (예상):

- Django: ~1,000 req/s
- Flask: ~2,000 req/s
- **FastAPI: ~10,000 req/s** ✅

### 3. WebSocket 일급 지원

```python
@app.websocket("/ws/room/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    await websocket.accept()
    # 실시간 타이머 동기화
```

### 4. 자동 문서화 (OpenAPI)

- Swagger UI: `/docs`
- ReDoc: `/redoc`
- OpenAPI JSON: `/openapi.json`

**개발 생산성 향상**: API 문서 수동 작성 불필요

### 5. 타입 힌트 기반 (Mypy 호환)

```python
def start_timer(room_id: str, duration: int) -> TimerState:
    pass
```

Mypy strict 모드와 완벽 호환되어 정적 분석 가능.

---

## 대안 (Alternatives)

### 대안 1: Django + Django REST Framework

**장점**:

- 성숙한 생태계
- 강력한 ORM
- Admin 패널

**단점**:

- 동기 I/O (비동기 지원 제한적)
- 무거운 프레임워크 (오버헤드)
- WebSocket 지원 약함 (Channels 필요)

**결론**: 실시간 요구사항에 부적합

---

### 대안 2: Flask + Flask-SocketIO

**장점**:

- 경량 프레임워크
- 유연성
- 낮은 학습 곡선

**단점**:

- 데이터 검증 수동 구현 필요
- 비동기 지원 약함
- 타입 안정성 부족

**결론**: 신뢰성 요구사항 충족 어려움

---

### 대안 3: Node.js (Express + Socket.io)

**장점**:

- 뛰어난 WebSocket 지원
- 비동기 네이티브
- 큰 생태계

**단점**:

- Python 생태계 활용 불가
- 타입 안정성 낮음 (TypeScript 필요)
- 팀의 Python 전문성 활용 불가

**결론**: 기술 스택 일관성 부족

---

## 결과 (Consequences)

### 긍정적 영향 ✅

1. **신뢰성**: Pydantic Strict 모드로 데이터 무결성 보장
2. **성능**: 비동기 I/O로 높은 동시 접속 처리
3. **생산성**: 자동 문서화로 개발 속도 향상
4. **유지보수성**: 명확한 타입 힌트로 코드 가독성 증가

### 부정적 영향 ⚠️

1. **ORM 제한**: Django ORM 대비 SQLAlchemy 학습 필요
2. **성숙도**: Django 대비 상대적으로 젊은 프레임워크
3. **Admin 패널**: 기본 제공 없음 (필요 시 별도 구축)

### 완화 전략

- SQLAlchemy Async 사용으로 ORM 기능 보완
- 활발한 커뮤니티와 문서로 성숙도 문제 상쇄
- Admin 패널 불필요 (API 중심 설계)

---

## 참조 (References)

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic V2 Documentation](https://docs.pydantic.dev/)
- [FastAPI vs Flask vs Django Benchmark](https://www.techempower.com/benchmarks/)
- ISO/IEC 25010: Software Quality Model

---

**승인자**: Architecture Team
**구현 상태**: ✅ 완료
