# Test Plan and Strategy

# Team Pomodoro Timer (Focus Mate)

**문서 버전**: 1.0
**작성일**: 2025-12-04
**표준 준수**: ISO/IEC/IEEE 29119 (Software Testing)

---

## 목차

1. [테스트 전략 개요](#1-테스트-전략-개요)
2. [테스트 레벨](#2-테스트-레벨)
3. [테스트 시나리오](#3-테스트-시나리오)
4. [품질 메트릭](#4-품질-메트릭)
5. [테스트 자동화](#5-테스트-자동화)

---

## 1. 테스트 전략 개요

### 1.1 테스트 목표

Focus Mate 프로젝트의 테스트는 **ISO/IEC 25010 품질 모델**을 기반으로 다음을 보장합니다:

| 품질 특성       | 테스트 목표        | 성공 기준               |
| --------------- | ------------------ | ----------------------- |
| **기능 적합성** | 모든 요구사항 검증 | 요구사항 커버리지 100%  |
| **신뢰성**      | 결함 최소화        | 테스트 커버리지 > 90%   |
| **성능 효율성** | 응답 시간 검증     | API < 200ms, WS < 100ms |
| **사용성**      | 접근성 준수        | A11y 위반 0건           |
| **유지보수성**  | 코드 품질          | CC < 10, MI > 20        |

### 1.2 테스트 피라미드

```
        ┌─────────────┐
        │     E2E     │  10% (Playwright)
        │   Tests     │
        └─────────────┘
      ┌───────────────────┐
      │  Integration      │  30% (Pytest, Jest)
      │     Tests         │
      └───────────────────┘
    ┌───────────────────────┐
    │    Unit Tests         │  60% (Pytest, Jest)
    │  (Functions, Classes) │
    └───────────────────────┘
```

**원칙**:

- 단위 테스트: 빠르고 격리된 테스트 (밀리초 단위)
- 통합 테스트: API 및 DB 연동 검증 (초 단위)
- E2E 테스트: 사용자 시나리오 검증 (분 단위)

### 1.3 테스트 환경

| 환경         | 목적                 | 데이터베이스      | 실행 빈도 |
| ------------ | -------------------- | ----------------- | --------- |
| **로컬**     | 개발 중 빠른 피드백  | SQLite (인메모리) | 매 커밋   |
| **CI/CD**    | 자동화된 품질 게이트 | SQLite (파일)     | 매 PR     |
| **스테이징** | 프로덕션 유사 환경   | PostgreSQL        | 배포 전   |

---

## 2. 테스트 레벨

### 2.1 단위 테스트 (Unit Tests)

#### 2.1.1 백엔드 단위 테스트 (Pytest)

**대상**:

- 비즈니스 로직 (Service Layer)
- 유틸리티 함수
- Pydantic 모델 검증

**예시: 타이머 서비스 테스트**

```python
# tests/unit/services/test_timer_service.py
import pytest
from datetime import datetime, timedelta
from app.services.timer_service import TimerService
from app.models.timer import TimerStatus, SessionType

class TestTimerService:
    """
    타이머 서비스 단위 테스트.
    REQ-F-004, REQ-F-005 검증.
    """

    def test_start_timer_sets_correct_target_timestamp(self):
        """
        TC-TIMER-001: 타이머 시작 시 정확한 종료 시각 계산
        """
        # Given
        service = TimerService()
        work_duration = 25 * 60  # 25분

        # When
        result = service.start_timer(
            room_id="test-room",
            duration_seconds=work_duration,
            session_type=SessionType.WORK
        )

        # Then
        expected_target = datetime.utcnow() + timedelta(seconds=work_duration)
        assert result.status == TimerStatus.RUNNING
        assert abs((result.target_timestamp - expected_target).total_seconds()) < 1

    def test_pause_timer_saves_remaining_time(self):
        """
        TC-TIMER-002: 일시정지 시 남은 시간 저장
        """
        # Given
        service = TimerService()
        service.start_timer("test-room", 1500, SessionType.WORK)

        # When
        result = service.pause_timer("test-room")

        # Then
        assert result.status == TimerStatus.PAUSED
        assert result.remaining_seconds > 0
        assert result.remaining_seconds <= 1500

    @pytest.mark.parametrize("duration,expected_valid", [
        (1, True),      # 최소값
        (3600, True),   # 최대값
        (0, False),     # 경계값 (무효)
        (-1, False),    # 음수 (무효)
        (3601, False),  # 초과 (무효)
    ])
    def test_timer_duration_validation(self, duration, expected_valid):
        """
        TC-TIMER-003: 타이머 시간 유효성 검증
        REQ-NF-009 (입력 검증) 준수
        """
        service = TimerService()

        if expected_valid:
            result = service.start_timer("test-room", duration, SessionType.WORK)
            assert result is not None
        else:
            with pytest.raises(ValueError):
                service.start_timer("test-room", duration, SessionType.WORK)
```

**커버리지 목표**:

- 라인 커버리지: > 95%
- 분기 커버리지: > 90%
- 함수 커버리지: 100%

---

#### 2.1.2 프론트엔드 단위 테스트 (Jest/Vitest)

**대상**:

- 유틸리티 함수
- 커스텀 훅
- 순수 컴포넌트 (UI 로직)

**예시: 시간 포맷 유틸리티 테스트**

```typescript
// tests/unit/utils/timeFormatter.test.ts
import { formatTime, calculateRemaining } from "@/utils/timeFormatter";

describe("timeFormatter", () => {
  describe("formatTime", () => {
    it("TC-UTIL-001: 정확한 MM:SS 포맷 변환", () => {
      // Given
      const seconds = 1505; // 25분 5초

      // When
      const result = formatTime(seconds);

      // Then
      expect(result).toBe("25:05");
    });

    it("TC-UTIL-002: 0초 처리", () => {
      expect(formatTime(0)).toBe("00:00");
    });

    it("TC-UTIL-003: 1시간 이상 처리", () => {
      expect(formatTime(3665)).toBe("61:05");
    });
  });

  describe("calculateRemaining", () => {
    it("TC-UTIL-004: 서버 타임스탬프 기반 남은 시간 계산", () => {
      // Given
      const targetTimestamp = new Date(Date.now() + 60000); // 1분 후

      // When
      const remaining = calculateRemaining(targetTimestamp);

      // Then
      expect(remaining).toBeGreaterThanOrEqual(59);
      expect(remaining).toBeLessThanOrEqual(60);
    });
  });
});
```

---

### 2.2 통합 테스트 (Integration Tests)

#### 2.2.1 API 통합 테스트

**대상**:

- REST API 엔드포인트
- 데이터베이스 연동
- 인증/인가

**예시: 방 생성 API 테스트**

```python
# tests/integration/api/test_rooms.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestRoomAPI:
    """
    방 관리 API 통합 테스트.
    REQ-F-001, REQ-F-002 검증.
    """

    def test_create_room_success(self, db_session):
        """
        TC-ROOM-001: 방 생성 성공 시나리오
        """
        # Given
        payload = {
            "room_name": "test-room-123",
            "work_duration_minutes": 25,
            "break_duration_minutes": 5
        }

        # When
        response = client.post("/api/v1/rooms", json=payload)

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["room_name"] == "test-room-123"
        assert "room_id" in data
        assert "share_url" in data

    def test_create_room_invalid_name(self):
        """
        TC-ROOM-002: 유효하지 않은 방 이름 거부
        REQ-NF-009 (입력 검증) 준수
        """
        # Given
        payload = {
            "room_name": "invalid name!",  # 공백과 특수문자 포함
            "work_duration_minutes": 25,
            "break_duration_minutes": 5
        }

        # When
        response = client.post("/api/v1/rooms", json=payload)

        # Then
        assert response.status_code == 422  # Validation Error
        assert "room_name" in response.json()["detail"][0]["loc"]

    def test_join_room_success(self, db_session, sample_room):
        """
        TC-ROOM-003: 방 참여 성공
        """
        # Given
        room_id = sample_room.id

        # When
        response = client.get(f"/api/v1/rooms/{room_id}")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["room_id"] == str(room_id)
        assert "timer_state" in data

    def test_join_nonexistent_room(self):
        """
        TC-ROOM-004: 존재하지 않는 방 접근 시 404
        """
        # Given
        fake_room_id = "00000000-0000-0000-0000-000000000000"

        # When
        response = client.get(f"/api/v1/rooms/{fake_room_id}")

        # Then
        assert response.status_code == 404
```

---

#### 2.2.2 WebSocket 통합 테스트

```python
# tests/integration/websocket/test_timer_sync.py
import pytest
from fastapi.testclient import TestClient
from app.main import app

def test_timer_synchronization_multiple_clients():
    """
    TC-SYNC-001: 다중 클라이언트 타이머 동기화
    REQ-F-004 검증
    """
    with TestClient(app) as client:
        # Client A 연결
        with client.websocket_connect("/ws/room/test-room") as ws_a:
            # Client B 연결
            with client.websocket_connect("/ws/room/test-room") as ws_b:
                # Client A가 타이머 시작
                ws_a.send_json({
                    "action": "start_timer",
                    "duration": 1500
                })

                # Client A 메시지 수신
                msg_a = ws_a.receive_json()
                assert msg_a["event"] == "timer_update"
                assert msg_a["data"]["status"] == "running"

                # Client B도 동일한 메시지 수신 (브로드캐스트)
                msg_b = ws_b.receive_json()
                assert msg_b["event"] == "timer_update"
                assert msg_b["data"]["status"] == "running"

                # 타임스탬프 오차 < 1초 검증
                assert abs(
                    msg_a["data"]["target_timestamp"] -
                    msg_b["data"]["target_timestamp"]
                ) < 1
```

---

### 2.3 E2E 테스트 (End-to-End Tests)

#### 2.3.1 Playwright 시나리오

**대상**:

- 사용자 워크플로우
- 브라우저 호환성
- 접근성 (A11y)

**예시: 방 생성 및 타이머 시작 시나리오**

```typescript
// tests/e2e/room-workflow.spec.ts
import { test, expect } from "@playwright/test";

test.describe("Room Creation and Timer Workflow", () => {
  test("TC-E2E-001: 사용자가 방을 생성하고 타이머를 시작할 수 있다", async ({
    page,
  }) => {
    // Given: 홈페이지 접속
    await page.goto("http://localhost:3000");

    // When: 방 생성 버튼 클릭
    await page.click('button:has-text("Create Room")');

    // Then: 방 생성 폼 표시
    await expect(page.locator('input[name="room_name"]')).toBeVisible();

    // When: 방 정보 입력
    await page.fill('input[name="room_name"]', "e2e-test-room");
    await page.fill('input[name="work_duration"]', "25");
    await page.click('button[type="submit"]');

    // Then: 방 페이지로 이동
    await expect(page).toHaveURL(/\/room\/.+/);
    await expect(page.locator("h1")).toContainText("e2e-test-room");

    // When: 타이머 시작
    await page.click('button:has-text("Start")');

    // Then: 타이머 실행 중 표시
    await expect(page.locator('[data-testid="timer-status"]')).toHaveText(
      "Running"
    );
    await expect(page.locator('[data-testid="timer-display"]')).toContainText(
      "25:00"
    );

    // Wait: 1초 후 시간 감소 확인
    await page.waitForTimeout(1000);
    await expect(page.locator('[data-testid="timer-display"]')).toContainText(
      "24:59"
    );
  });

  test("TC-E2E-002: 접근성 검증", async ({ page }) => {
    await page.goto("http://localhost:3000");

    // axe-core를 사용한 A11y 검증
    const accessibilityScanResults = await page.evaluate(() => {
      // @ts-ignore
      return window.axe.run();
    });

    expect(accessibilityScanResults.violations).toHaveLength(0);
  });
});
```

---

## 3. 테스트 시나리오

### 3.1 핵심 사용자 시나리오

#### 시나리오 1: 팀 포모도로 세션

```gherkin
Feature: 팀 포모도로 세션 진행
  As a 팀 리더
  I want to 팀원들과 포모도로 타이머를 공유하고
  So that 함께 집중 시간을 관리할 수 있다

Scenario: 팀 세션 생성 및 진행
  Given 사용자 A가 "team-alpha" 방을 생성했다
  And 사용자 B가 공유 URL로 방에 참여했다
  When 사용자 A가 25분 타이머를 시작한다
  Then 사용자 B의 화면에도 25분 타이머가 표시된다
  And 두 사용자의 타이머 오차는 1초 이내이다

  When 25분이 경과한다
  Then 모든 사용자에게 "집중 시간 완료" 알림이 표시된다
  And 자동으로 5분 휴식 타이머가 시작된다
```

#### 시나리오 2: 네트워크 단절 복구

```gherkin
Scenario: 연결 끊김 후 재접속
  Given 타이머가 실행 중이다
  When 사용자의 네트워크 연결이 끊긴다
  And 10초 후 네트워크가 복구된다
  Then 자동으로 WebSocket 재연결이 시도된다
  And 현재 타이머 상태가 동기화된다
  And 사용자는 정확한 남은 시간을 확인할 수 있다
```

### 3.2 경계값 테스트 (Boundary Value Analysis)

| 입력 필드 | 유효 범위 | 경계값 테스트 케이스                         |
| --------- | --------- | -------------------------------------------- |
| 방 이름   | 3-50자    | 2자(무효), 3자(유효), 50자(유효), 51자(무효) |
| 집중 시간 | 1-60분    | 0분(무효), 1분(유효), 60분(유효), 61분(무효) |
| 휴식 시간 | 1-30분    | 0분(무효), 1분(유효), 30분(유효), 31분(무효) |

---

## 4. 품질 메트릭

### 4.1 코드 커버리지

**목표**:

```yaml
backend:
  line_coverage: 90%
  branch_coverage: 85%
  function_coverage: 95%

frontend:
  line_coverage: 90%
  branch_coverage: 85%
  statement_coverage: 90%
```

**측정 도구**:

- Backend: `pytest-cov`
- Frontend: `jest --coverage` 또는 `vitest --coverage`

**CI 설정**:

```yaml
# .github/workflows/test.yml
- name: Run Backend Tests
  run: |
    pytest --cov=app --cov-report=xml --cov-fail-under=90

- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

---

### 4.2 성능 메트릭

#### 부하 테스트 시나리오 (Locust)

```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class PomodoroUser(HttpUser):
    """
    TC-PERF-001: 동시 접속 부하 테스트
    REQ-NF-001, REQ-NF-003 검증
    """
    wait_time = between(1, 3)

    def on_start(self):
        """사용자 초기화: 방 생성"""
        response = self.client.post("/api/v1/rooms", json={
            "room_name": f"load-test-{self.environment.runner.user_count}",
            "work_duration_minutes": 25,
            "break_duration_minutes": 5
        })
        self.room_id = response.json()["room_id"]

    @task(3)
    def get_room_info(self):
        """방 정보 조회 (빈도 높음)"""
        self.client.get(f"/api/v1/rooms/{self.room_id}")

    @task(1)
    def start_timer(self):
        """타이머 시작 (빈도 낮음)"""
        self.client.post(f"/api/v1/rooms/{self.room_id}/timer/start")
```

**성능 기준**:

- 동시 사용자: 500명
- 응답 시간 p95: < 200ms
- 에러율: < 0.1%

---

### 4.3 복잡도 메트릭

**목표**:

- Cyclomatic Complexity < 10 (함수당)
- Maintainability Index > 20 (Grade A)

**측정**:

```bash
# Backend
radon cc src/backend/app --min A --show-complexity

# Frontend
eslint src/frontend/src --rule 'complexity: ["error", 10]'
```

---

## 5. 테스트 자동화

### 5.1 CI/CD 파이프라인

```yaml
# .github/workflows/ci.yml
name: CI Pipeline

on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.12"

      - name: Install Dependencies
        run: |
          cd src/backend
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-asyncio

      - name: Run Unit Tests
        run: |
          cd src/backend
          pytest tests/unit --cov=app --cov-report=xml

      - name: Run Integration Tests
        run: |
          cd src/backend
          pytest tests/integration --cov=app --cov-append

      - name: Check Coverage
        run: |
          cd src/backend
          pytest --cov=app --cov-fail-under=90

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: "20"

      - name: Install Dependencies
        run: |
          cd src/frontend
          npm ci

      - name: Run Tests
        run: |
          cd src/frontend
          npm test -- --coverage --coverageThreshold='{"global":{"lines":90}}'

  e2e-tests:
    runs-on: ubuntu-latest
    needs: [backend-tests, frontend-tests]
    steps:
      - uses: actions/checkout@v3

      - name: Start Services
        run: docker-compose up -d

      - name: Wait for Services
        run: ./scripts/wait-for-services.sh

      - name: Run E2E Tests
        run: |
          npx playwright test

      - name: Upload Test Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: playwright-report
          path: playwright-report/
```

---

### 5.2 Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: local
    hooks:
      - id: pytest-check
        name: pytest-check
        entry: pytest tests/unit --maxfail=1
        language: system
        pass_filenames: false
        always_run: true

      - id: mypy
        name: mypy
        entry: mypy src/backend/app --strict
        language: system
        types: [python]

      - id: eslint
        name: eslint
        entry: eslint src/frontend/src
        language: system
        types: [javascript, typescript, tsx]
```

---

### 5.3 테스트 데이터 관리

#### Fixture 전략

```python
# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.database import Base

@pytest.fixture(scope="function")
def db_session():
    """
    각 테스트마다 격리된 DB 세션 제공.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    yield session

    session.close()
    Base.metadata.drop_all(engine)

@pytest.fixture
def sample_room(db_session):
    """샘플 방 데이터"""
    from app.models.room import Room
    room = Room(
        name="test-room",
        work_duration=1500,
        break_duration=300
    )
    db_session.add(room)
    db_session.commit()
    return room
```

---

## 6. 테스트 실행 가이드

### 6.1 로컬 실행

```bash
# 전체 테스트 실행
make test

# 백엔드만
cd src/backend && pytest

# 프론트엔드만
cd src/frontend && npm test

# E2E 테스트
docker-compose up -d
npx playwright test
```

### 6.2 특정 테스트 실행

```bash
# 특정 파일
pytest tests/unit/services/test_timer_service.py

# 특정 테스트 케이스
pytest tests/unit/services/test_timer_service.py::TestTimerService::test_start_timer

# 마커 기반 실행
pytest -m "not slow"  # slow 마커 제외
```

---

## 7. 결함 관리

### 7.1 버그 우선순위

| 심각도       | 정의                     | 대응 시간     |
| ------------ | ------------------------ | ------------- |
| **Critical** | 서비스 중단, 데이터 손실 | 즉시          |
| **High**     | 주요 기능 불가           | 24시간        |
| **Medium**   | 부분 기능 오류           | 1주일         |
| **Low**      | UI 개선, 사소한 버그     | 다음 스프린트 |

### 7.2 회귀 테스트

- 모든 버그 수정 시 재현 테스트 케이스 추가
- 릴리스 전 전체 회귀 테스트 실행

---

## 8. 부록

### 8.1 테스트 체크리스트

- [ ] 모든 요구사항에 대한 테스트 케이스 작성
- [ ] 테스트 커버리지 90% 이상 달성
- [ ] 복잡도 메트릭 기준 충족
- [ ] E2E 테스트 통과
- [ ] 성능 테스트 기준 충족
- [ ] 접근성 검증 완료

### 8.2 참조

- [SRS.md](./SRS.md): 요구사항 명세서
- [ARCHITECTURE.md](./ARCHITECTURE.md): 아키텍처 문서
- ISO/IEC/IEEE 29119: Software Testing Standards

---

**문서 끝**
