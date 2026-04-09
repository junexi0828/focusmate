---
id: DEV-002
title: Contributing Guide
version: 1.0
status: Approved
date: 2025-12-04
author: Focus Mate Team
iso_standard: ISO/IEC 25010 Maintainability
---

# Contributing to Team Pomodoro Timer (Focus Mate)

**환영합니다!** 🎉
Focus Mate 프로젝트에 기여해주셔서 감사합니다.

---

## 목차
1. [개발 환경 설정](#1-개발-환경-설정)
2. [개발 워크플로우](#2-개발-워크플로우)
3. [코드 작성 가이드](#3-코드-작성-가이드)
4. [테스트 작성](#4-테스트-작성)
5. [Pull Request 프로세스](#5-pull-request-프로세스)

---

## 1. 개발 환경 설정

### 1.1 필수 요구사항

- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Node.js**: 20+ (로컬 개발 시)
- **Python**: 3.12+ (로컬 개발 시)
- **Git**: 2.30+

### 1.2 저장소 클론

```bash
git clone https://github.com/junexi0828/focusmate.git
cd focusmate
```

### 1.3 Docker 환경 설정

```bash
# 전체 스택 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f

# 중지
docker-compose down
```

### 1.4 로컬 개발 환경 (선택)

#### 백엔드

```bash
cd src/backend

# 가상 환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
pip install -r requirements-dev.txt

# 개발 서버 실행
uvicorn app.main:app --reload --port 8000
```

#### 프론트엔드

```bash
cd src/frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev
```

---

## 2. 개발 워크플로우

### 2.1 Git 브랜치 전략

```
main (프로덕션)
  └─ develop (개발)
      ├─ feature/room-management
      ├─ feature/timer-sync
      ├─ bugfix/timer-drift
      └─ hotfix/critical-bug
```

**브랜치 네이밍**:
- `feature/기능명`: 새 기능 개발
- `bugfix/버그명`: 버그 수정
- `hotfix/긴급수정명`: 긴급 수정
- `refactor/리팩토링명`: 코드 개선
- `docs/문서명`: 문서 작업

### 2.2 작업 시작

```bash
# 최신 코드 가져오기
git checkout develop
git pull origin develop

# 새 브랜치 생성
git checkout -b feature/timer-pause

# 작업 진행...
```

### 2.3 커밋 메시지 규칙

**포맷**: `<type>(<scope>): <subject>`

**타입**:
- `feat`: 새로운 기능
- `fix`: 버그 수정
- `docs`: 문서 변경
- `style`: 코드 포맷팅 (기능 변경 없음)
- `refactor`: 리팩토링
- `test`: 테스트 추가/수정
- `chore`: 빌드, 설정 변경

**예시**:
```bash
git commit -m "feat(timer): implement pause functionality (REQ-F-006)"
git commit -m "fix(websocket): resolve reconnection issue"
git commit -m "docs(api): update timer endpoints documentation"
git commit -m "test(timer): add unit tests for pause/resume"
```

---

## 3. 코드 작성 가이드

### 3.1 요구사항 추적

모든 코드는 요구사항 ID를 참조해야 합니다:

```python
def start_timer(room_id: str, duration: int) -> TimerState:
    """
    타이머를 시작합니다.

    Implements: REQ-F-005 (타이머 시작)
    Related: REQ-F-004 (타이머 동기화)
    """
    pass
```

### 3.2 코드 품질 체크

```bash
# 백엔드
cd src/backend
ruff check app/                    # Linting
mypy app/ --strict                 # Type checking
radon cc app/ --min A              # Complexity
pytest tests/ --cov=app            # Tests

# 프론트엔드
cd src/frontend
npm run lint                       # ESLint
npm run type-check                 # TypeScript
npm test                           # Jest
```

### 3.3 Pre-commit Hook 설정

```bash
# Pre-commit 설치
pip install pre-commit

# Hook 활성화
pre-commit install

# 수동 실행
pre-commit run --all-files
```

---

## 4. 테스트 작성

### 4.1 테스트 작성 원칙

1. **TDD (Test-Driven Development)**: 테스트를 먼저 작성
2. **AAA 패턴**: Arrange, Act, Assert
3. **격리**: 각 테스트는 독립적
4. **명확한 네이밍**: `test_<function>_<scenario>_<expected>`

### 4.2 백엔드 테스트 예시

```python
# tests/unit/services/test_timer_service.py
import pytest
from app.services.timer_service import TimerService

class TestTimerService:
    """
    타이머 서비스 테스트.
    Coverage: REQ-F-005, REQ-F-006
    """

    def test_start_timer_creates_running_state(self):
        """
        Given: 타이머 서비스와 유효한 입력
        When: start_timer 호출
        Then: RUNNING 상태의 타이머 반환
        """
        # Arrange
        service = TimerService()
        room_id = "test-room"
        duration = 1500

        # Act
        result = service.start_timer(room_id, duration)

        # Assert
        assert result.status == TimerStatus.RUNNING
        assert result.remaining_seconds == duration
```

### 4.3 프론트엔드 테스트 예시

```typescript
// tests/unit/hooks/useTimer.test.ts
import { renderHook, act } from '@testing-library/react-hooks';
import { useTimer } from '@/hooks/useTimer';

describe('useTimer', () => {
  it('should start timer and decrease remaining seconds', () => {
    // Arrange
    const { result } = renderHook(() => useTimer({ initialDuration: 10 }));

    // Act
    act(() => {
      result.current.start();
    });

    // Assert
    expect(result.current.status).toBe('running');

    // Wait 1 second
    act(() => {
      jest.advanceTimersByTime(1000);
    });

    expect(result.current.remainingSeconds).toBe(9);
  });
});
```

---

## 5. Pull Request 프로세스

### 5.1 PR 생성 전 체크리스트

- [ ] 모든 테스트 통과 (`npm test`, `pytest`)
- [ ] 코드 커버리지 > 90%
- [ ] Linting 통과 (`npm run lint`, `ruff check`)
- [ ] Type checking 통과 (`tsc`, `mypy`)
- [ ] 복잡도 < 10 (`radon cc`)
- [ ] 문서 업데이트 (필요 시)
- [ ] 커밋 메시지 규칙 준수

### 5.2 PR 생성

```bash
# 변경사항 푸시
git push origin feature/timer-pause

# GitHub에서 PR 생성
# Base: develop
# Compare: feature/timer-pause
```

### 5.3 PR 템플릿

```markdown
## 변경 사항
- 타이머 일시정지 기능 구현 (REQ-F-006)
- 일시정지 상태 UI 추가

## 관련 이슈
- Closes #123

## 테스트
- [x] 단위 테스트 추가 (test_pause_timer)
- [x] 통합 테스트 추가 (test_pause_api)
- [x] E2E 테스트 추가 (timer-pause.spec.ts)

## 체크리스트
- [x] 테스트 커버리지 > 90%
- [x] 복잡도 < 10
- [x] 타입 체크 통과
- [x] 문서 업데이트

## 스크린샷 (UI 변경 시)
![타이머 일시정지 UI](screenshot.png)
```

### 5.4 코드 리뷰

**리뷰어 체크리스트**:
- [ ] 요구사항 충족
- [ ] 코드 품질 (복잡도, 네이밍)
- [ ] 테스트 충분성
- [ ] 보안 이슈 없음
- [ ] 성능 문제 없음

**리뷰 코멘트 예시**:
```markdown
**제안**: 이 함수의 복잡도가 12입니다. Strategy 패턴을 사용하여 분리하는 것을 권장합니다.

```python
# 현재
def process_event(event):
    if event.type == "start":
        # 10 lines
    elif event.type == "pause":
        # 10 lines
    # ...

# 제안
def process_event(event):
    handler = get_handler(event.type)
    handler.handle(event)
```
```

### 5.5 Merge 조건

- ✅ 최소 1명의 Approve
- ✅ CI/CD 파이프라인 통과
- ✅ 충돌 해결 완료
- ✅ 모든 코멘트 해결

---

## 6. 자주 묻는 질문 (FAQ)

### Q1: Docker 없이 개발할 수 있나요?
**A**: 가능합니다. 위의 "로컬 개발 환경" 섹션을 참조하세요.

### Q2: 테스트가 실패하면 어떻게 하나요?
**A**:
```bash
# 실패한 테스트만 재실행
pytest tests/ --lf

# 상세 로그 확인
pytest tests/ -vv
```

### Q3: 복잡도를 낮추는 방법은?
**A**: [CODING_STANDARDS.md](./CODING_STANDARDS.md#24-복잡도-관리) 참조

### Q4: 타입 에러를 해결하려면?
**A**:
```bash
# 백엔드
mypy app/ --strict --show-error-codes

# 프론트엔드
tsc --noEmit
```

---

## 7. 도움 받기

- **문서**: [docs/](./docs/) 폴더 참조
- **이슈**: [GitHub Issues](https://github.com/junexi0828/focusmate/issues)
- **토론**: [GitHub Discussions](https://github.com/junexi0828/focusmate/discussions)

---

**다시 한 번 기여해주셔서 감사합니다!** 🙏

