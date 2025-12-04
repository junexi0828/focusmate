# Coding Standards and Style Guide

# Team Pomodoro Timer (Focus Mate)

**문서 버전**: 1.0
**작성일**: 2025-12-04
**목적**: ISO/IEC 25010 유지보수성 및 신뢰성 확보

---

## 목차

1. [일반 원칙](#1-일반-원칙)
2. [Python 코딩 표준](#2-python-코딩-표준)
3. [TypeScript 코딩 표준](#3-typescript-코딩-표준)
4. [코드 리뷰 가이드](#4-코드-리뷰-가이드)
5. [품질 게이트](#5-품질-게이트)

---

## 1. 일반 원칙

### 1.1 핵심 가치

| 원칙              | 설명                           | ISO 25010 연관           |
| ----------------- | ------------------------------ | ------------------------ |
| **명확성**        | 코드는 주석보다 자명해야 함    | 유지보수성 - 분석성      |
| **단순성**        | 복잡도 < 10 유지               | 유지보수성 - 변경 용이성 |
| **타입 안정성**   | Any 타입 금지                  | 신뢰성 - 성숙성          |
| **테스트 가능성** | 모든 로직은 테스트 가능해야 함 | 신뢰성 - 시험성          |

### 1.2 SOLID 원칙 준수

```python
# ✅ Good: Single Responsibility
class TimerService:
    """타이머 로직만 담당"""
    def start_timer(self, duration: int) -> Timer:
        pass

class NotificationService:
    """알림 로직만 담당"""
    def send_notification(self, message: str) -> None:
        pass

# ❌ Bad: 여러 책임
class TimerService:
    def start_timer(self, duration: int) -> Timer:
        pass

    def send_notification(self, message: str) -> None:  # 책임 위반
        pass
```

---

## 2. Python 코딩 표준

### 2.1 스타일 가이드

**기준**: PEP 8 + Black + Ruff

#### 2.1.1 Naming Conventions

```python
# 모듈/패키지: snake_case
# timer_service.py

# 클래스: PascalCase
class TimerService:
    pass

# 함수/변수: snake_case
def calculate_remaining_time(target_timestamp: datetime) -> int:
    remaining_seconds = ...
    return remaining_seconds

# 상수: UPPER_SNAKE_CASE
MAX_PARTICIPANTS = 50
DEFAULT_WORK_DURATION = 1500

# Private: 언더스코어 접두사
class Room:
    def __init__(self):
        self._internal_state = {}  # Private
```

---

### 2.2 타입 힌트 (Type Hints)

#### 2.2.1 엄격한 타입 정의

```python
from typing import Optional, List, Dict, Any
from datetime import datetime

# ✅ Good: 명확한 타입
def start_timer(
    room_id: str,
    duration_seconds: int,
    session_type: SessionType
) -> TimerState:
    """
    타이머를 시작합니다.

    Args:
        room_id: 방 고유 식별자 (UUID 문자열)
        duration_seconds: 타이머 시간 (초 단위, 1-3600)
        session_type: 세션 유형 (work 또는 break)

    Returns:
        TimerState: 시작된 타이머 상태

    Raises:
        ValueError: duration_seconds가 유효 범위를 벗어난 경우
        RoomNotFoundError: room_id에 해당하는 방이 없는 경우
    """
    pass

# ❌ Bad: Any 타입 사용
def start_timer(room_id: Any, duration: Any) -> Any:
    pass
```

#### 2.2.2 Mypy 설정

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_incomplete_defs = true
check_untyped_defs = true
no_implicit_optional = true

# Pydantic 플러그인
plugins = ["pydantic.mypy"]

[tool.pydantic-mypy]
init_forbid_extra = true
init_typed = true
warn_required_dynamic_aliases = true
```

---

### 2.3 Pydantic 모델 (Strict Mode)

#### 2.3.1 데이터 검증

```python
from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr, field_validator
from typing import Annotated

class RoomCreate(BaseModel):
    """
    방 생성 요청 모델.

    ISO 25010 신뢰성 확보를 위해 Strict 모드 사용.
    모든 필드는 자동 형변환 없이 정확한 타입만 허용.
    """
    model_config = ConfigDict(
        strict=True,
        frozen=False,
        validate_assignment=True,
        str_strip_whitespace=True
    )

    room_name: Annotated[
        StrictStr,
        Field(
            min_length=3,
            max_length=50,
            pattern=r"^[a-zA-Z0-9_-]+$",
            description="방 이름 (영문, 숫자, 하이픈, 언더스코어만 허용)",
            examples=["team-alpha", "study_group_1"]
        )
    ]

    work_duration_minutes: Annotated[
        StrictInt,
        Field(
            gt=0,
            le=60,
            description="집중 시간 (분)",
            examples=[25, 45]
        )
    ] = 25

    break_duration_minutes: Annotated[
        StrictInt,
        Field(
            gt=0,
            le=30,
            description="휴식 시간 (분)",
            examples=[5, 10]
        )
    ] = 5

    @field_validator('work_duration_minutes')
    @classmethod
    def validate_work_duration(cls, v: int) -> int:
        """비즈니스 규칙: 휴식 시간보다 길어야 함"""
        # 추가 검증 로직
        return v
```

---

### 2.4 복잡도 관리

#### 2.4.1 순환 복잡도 (Cyclomatic Complexity)

**목표**: CC < 10

```python
# ❌ Bad: CC = 12 (너무 복잡)
def process_timer_event(event: dict) -> None:
    if event["type"] == "start":
        if event["duration"] > 0:
            if event["session"] == "work":
                if event["auto_start"]:
                    # ...
                else:
                    # ...
            else:
                # ...
        else:
            # ...
    elif event["type"] == "pause":
        # ...
    elif event["type"] == "reset":
        # ...

# ✅ Good: CC = 3 (단순화)
def process_timer_event(event: TimerEvent) -> None:
    """
    타이머 이벤트를 처리합니다.

    복잡도 감소를 위해 Strategy 패턴 사용.
    """
    handler = get_event_handler(event.type)
    handler.handle(event)

def get_event_handler(event_type: EventType) -> EventHandler:
    """이벤트 타입에 맞는 핸들러 반환"""
    handlers = {
        EventType.START: StartEventHandler(),
        EventType.PAUSE: PauseEventHandler(),
        EventType.RESET: ResetEventHandler(),
    }
    return handlers[event_type]
```

#### 2.4.2 함수 길이 제한

**목표**: 함수당 50줄 이하

```python
# ✅ Good: 작고 집중된 함수
def calculate_target_timestamp(duration_seconds: int) -> datetime:
    """종료 시각 계산 (단일 책임)"""
    return datetime.utcnow() + timedelta(seconds=duration_seconds)

def validate_duration(duration_seconds: int) -> None:
    """시간 유효성 검증 (단일 책임)"""
    if not 1 <= duration_seconds <= 3600:
        raise ValueError(f"Duration must be between 1 and 3600, got {duration_seconds}")

def start_timer(room_id: str, duration_seconds: int) -> TimerState:
    """타이머 시작 (조합)"""
    validate_duration(duration_seconds)
    target = calculate_target_timestamp(duration_seconds)
    return TimerState(status=TimerStatus.RUNNING, target_timestamp=target)
```

---

### 2.5 에러 처리

#### 2.5.1 커스텀 예외

```python
# app/core/exceptions.py
class FocusMateException(Exception):
    """기본 예외 클래스"""
    def __init__(self, message: str, code: str):
        self.message = message
        self.code = code
        super().__init__(self.message)

class RoomNotFoundError(FocusMateException):
    """방을 찾을 수 없을 때"""
    def __init__(self, room_id: str):
        super().__init__(
            message=f"Room not found: {room_id}",
            code="ROOM_NOT_FOUND"
        )

class TimerAlreadyRunningError(FocusMateException):
    """타이머가 이미 실행 중일 때"""
    def __init__(self, room_id: str):
        super().__init__(
            message=f"Timer is already running in room: {room_id}",
            code="TIMER_ALREADY_RUNNING"
        )
```

#### 2.5.2 에러 핸들링

```python
from fastapi import HTTPException, status

# ✅ Good: 명확한 에러 처리
@router.post("/rooms/{room_id}/timer/start")
async def start_timer(
    room_id: str,
    service: TimerService = Depends(get_timer_service)
) -> TimerResponse:
    """타이머 시작 API"""
    try:
        timer_state = await service.start_timer(room_id)
        return TimerResponse(status="success", data=timer_state)

    except RoomNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": e.code, "message": e.message}
        )

    except TimerAlreadyRunningError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"code": e.code, "message": e.message}
        )

    except Exception as e:
        # 예상치 못한 에러는 로깅 후 500 반환
        logger.error(f"Unexpected error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"code": "INTERNAL_ERROR", "message": "An unexpected error occurred"}
        )
```

---

### 2.6 Docstring 규칙

**스타일**: Google Style

```python
def calculate_remaining_time(
    target_timestamp: datetime,
    current_timestamp: datetime | None = None
) -> int:
    """
    타이머의 남은 시간을 계산합니다.

    서버 타임스탬프 기반으로 정확한 남은 시간을 계산하여
    클라이언트 간 동기화 오차를 최소화합니다.

    Args:
        target_timestamp: 타이머 종료 예정 시각 (UTC)
        current_timestamp: 현재 시각 (기본값: datetime.utcnow())

    Returns:
        int: 남은 시간 (초 단위). 음수인 경우 0 반환.

    Raises:
        ValueError: target_timestamp가 None인 경우

    Examples:
        >>> target = datetime(2025, 12, 4, 10, 25, 0)
        >>> current = datetime(2025, 12, 4, 10, 0, 0)
        >>> calculate_remaining_time(target, current)
        1500

    Note:
        타임존은 항상 UTC를 사용합니다.
        로컬 타임존 사용 시 동기화 오류 발생 가능.
    """
    if target_timestamp is None:
        raise ValueError("target_timestamp cannot be None")

    current = current_timestamp or datetime.utcnow()
    remaining = (target_timestamp - current).total_seconds()
    return max(0, int(remaining))
```

---

## 3. TypeScript 코딩 표준

### 3.1 스타일 가이드

**기준**: Airbnb Style Guide + Prettier + ESLint

#### 3.1.1 Naming Conventions

```typescript
// 인터페이스/타입: PascalCase
interface TimerState {
  status: TimerStatus;
  remainingSeconds: number;
}

// 컴포넌트: PascalCase
const TimerDisplay: React.FC<TimerDisplayProps> = ({ remainingSeconds }) => {
  return <div>{formatTime(remainingSeconds)}</div>;
};

// 함수/변수: camelCase
const calculateRemainingTime = (targetTimestamp: Date): number => {
  const now = new Date();
  return Math.max(
    0,
    Math.floor((targetTimestamp.getTime() - now.getTime()) / 1000)
  );
};

// 상수: UPPER_SNAKE_CASE
const MAX_RECONNECT_ATTEMPTS = 5;
const DEFAULT_WORK_DURATION = 1500;

// Private: 언더스코어 접두사 (클래스 멤버)
class WebSocketManager {
  private _reconnectAttempts = 0;
}
```

---

### 3.2 타입 정의

#### 3.2.1 엄격한 타입 사용

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "strictBindCallApply": true,
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true
  }
}
```

```typescript
// ✅ Good: 명확한 타입
interface TimerState {
  status: "idle" | "running" | "paused";
  remainingSeconds: number;
  targetTimestamp: Date | null;
  sessionType: "work" | "break";
}

function startTimer(duration: number): TimerState {
  return {
    status: "running",
    remainingSeconds: duration,
    targetTimestamp: new Date(Date.now() + duration * 1000),
    sessionType: "work",
  };
}

// ❌ Bad: any 사용
function startTimer(duration: any): any {
  return {
    status: "running",
    remainingSeconds: duration,
  };
}
```

#### 3.2.2 유틸리티 타입 활용

```typescript
// 기본 타입
interface Room {
  id: string;
  name: string;
  workDuration: number;
  breakDuration: number;
  createdAt: Date;
}

// 생성 시 (id, createdAt 제외)
type RoomCreate = Omit<Room, "id" | "createdAt">;

// 업데이트 시 (모든 필드 선택적)
type RoomUpdate = Partial<Room>;

// 읽기 전용
type RoomReadonly = Readonly<Room>;

// 필수 필드만
type RoomRequired = Required<Pick<Room, "name" | "workDuration">>;
```

---

### 3.3 React 컴포넌트 패턴

#### 3.3.1 함수형 컴포넌트 (Hooks)

```typescript
// ✅ Good: 명확한 Props 타입
interface TimerDisplayProps {
  remainingSeconds: number;
  status: TimerStatus;
  onStart: () => void;
  onPause: () => void;
  onReset: () => void;
}

export const TimerDisplay: React.FC<TimerDisplayProps> = ({
  remainingSeconds,
  status,
  onStart,
  onPause,
  onReset,
}) => {
  // 복잡한 로직은 커스텀 훅으로 분리
  const formattedTime = useFormattedTime(remainingSeconds);

  return (
    <div className="timer-display" data-testid="timer-display">
      <div className="timer-value">{formattedTime}</div>
      <div className="timer-controls">
        {status === "idle" && <button onClick={onStart}>Start</button>}
        {status === "running" && <button onClick={onPause}>Pause</button>}
        <button onClick={onReset}>Reset</button>
      </div>
    </div>
  );
};

// Props 기본값
TimerDisplay.defaultProps = {
  remainingSeconds: 1500,
  status: "idle",
};
```

#### 3.3.2 커스텀 훅

```typescript
// ✅ Good: 재사용 가능한 로직
interface UseTimerOptions {
  initialDuration: number;
  onComplete?: () => void;
}

interface UseTimerReturn {
  remainingSeconds: number;
  status: TimerStatus;
  start: () => void;
  pause: () => void;
  reset: () => void;
}

export const useTimer = ({
  initialDuration,
  onComplete,
}: UseTimerOptions): UseTimerReturn => {
  const [remainingSeconds, setRemainingSeconds] = useState(initialDuration);
  const [status, setStatus] = useState<TimerStatus>("idle");
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const start = useCallback(() => {
    setStatus("running");
    intervalRef.current = setInterval(() => {
      setRemainingSeconds((prev) => {
        if (prev <= 1) {
          clearInterval(intervalRef.current!);
          setStatus("idle");
          onComplete?.();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
  }, [onComplete]);

  const pause = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setStatus("paused");
  }, []);

  const reset = useCallback(() => {
    pause();
    setRemainingSeconds(initialDuration);
    setStatus("idle");
  }, [initialDuration, pause]);

  // Cleanup
  useEffect(() => {
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, []);

  return { remainingSeconds, status, start, pause, reset };
};
```

---

### 3.4 복잡도 관리

#### 3.4.1 ESLint 설정

```json
// .eslintrc.json
{
  "extends": [
    "airbnb",
    "airbnb-typescript",
    "plugin:@typescript-eslint/recommended",
    "plugin:react-hooks/recommended",
    "prettier"
  ],
  "rules": {
    "complexity": ["error", 10],
    "max-lines-per-function": ["error", 50],
    "max-depth": ["error", 3],
    "max-params": ["error", 4],
    "react/jsx-no-bind": "error",
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/explicit-function-return-type": "warn"
  }
}
```

---

### 3.5 에러 처리

```typescript
// ✅ Good: 타입 안전한 에러 처리
class ApiError extends Error {
  constructor(public code: string, message: string, public statusCode: number) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchRoom(roomId: string): Promise<Room> {
  try {
    const response = await fetch(`/api/v1/rooms/${roomId}`);

    if (!response.ok) {
      throw new ApiError(
        "FETCH_FAILED",
        `Failed to fetch room: ${response.statusText}`,
        response.status
      );
    }

    const data: Room = await response.json();
    return data;
  } catch (error) {
    if (error instanceof ApiError) {
      // 예상된 에러
      console.error(`API Error [${error.code}]:`, error.message);
      throw error;
    }

    // 예상치 못한 에러
    console.error("Unexpected error:", error);
    throw new ApiError("UNKNOWN_ERROR", "An unexpected error occurred", 500);
  }
}
```

---

## 4. 코드 리뷰 가이드

### 4.1 리뷰 체크리스트

#### 기능성

- [ ] 요구사항 ID가 명시되어 있는가? (예: REQ-F-001)
- [ ] 모든 엣지 케이스가 처리되었는가?
- [ ] 에러 처리가 적절한가?

#### 코드 품질

- [ ] 복잡도 < 10인가?
- [ ] 함수 길이 < 50줄인가?
- [ ] 타입 안정성이 보장되는가? (Any 타입 없음)
- [ ] 네이밍이 명확한가?

#### 테스트

- [ ] 단위 테스트가 작성되었는가?
- [ ] 테스트 커버리지 > 90%인가?
- [ ] 경계값 테스트가 포함되었는가?

#### 문서화

- [ ] Docstring/JSDoc이 작성되었는가?
- [ ] 복잡한 로직에 주석이 있는가?
- [ ] README가 업데이트되었는가?

---

### 4.2 리뷰 코멘트 예시

````python
# ❌ Bad Comment
# 이거 고쳐

# ✅ Good Comment
"""
REQ-NF-007 위반: 이 함수의 순환 복잡도가 12입니다.
제안: Strategy 패턴을 사용하여 각 이벤트 타입별로 핸들러를 분리하세요.

예시:
```python
def process_event(event: Event) -> None:
    handler = get_handler(event.type)
    handler.handle(event)
````

"""

````

---

## 5. 품질 게이트

### 5.1 자동화된 검사

```bash
# 백엔드
ruff check src/backend/app          # Linting
mypy src/backend/app --strict       # Type checking
radon cc src/backend/app --min A    # Complexity
bandit -r src/backend/app           # Security
pytest --cov=app --cov-fail-under=90  # Tests

# 프론트엔드
eslint src/frontend/src             # Linting
tsc --noEmit                        # Type checking
npm test -- --coverage              # Tests
npm audit                           # Security
````

### 5.2 Pre-commit Hook

```bash
# .git/hooks/pre-commit
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# Backend
cd src/backend
ruff check app/
mypy app/ --strict
pytest tests/unit --maxfail=1

# Frontend
cd ../frontend
npm run lint
npm run type-check
npm test -- --bail

echo "✅ All checks passed!"
```

---

## 6. 부록

### 6.1 도구 설정 파일

#### pyproject.toml

```toml
[tool.ruff]
line-length = 100
target-version = "py312"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "C90"]
ignore = []

[tool.ruff.lint.mccabe]
max-complexity = 10

[tool.black]
line-length = 100
target-version = ['py312']
```

#### .prettierrc

```json
{
  "semi": true,
  "trailingComma": "es5",
  "singleQuote": true,
  "printWidth": 100,
  "tabWidth": 2
}
```

---

**문서 끝**
