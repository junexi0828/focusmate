# Software Requirements Specification (SRS)

# Team Pomodoro Timer (Focus Mate)

**문서 버전**: 1.0
**작성일**: 2025-12-04
**표준 준수**: ISO/IEC/IEEE 29148:2018

---

## 목차

1. [서론](#1-서론)
2. [전체 설명](#2-전체-설명)
3. [기능 요구사항](#3-기능-요구사항)
4. [비기능 요구사항](#4-비기능-요구사항)
5. [요구사항 추적성 매트릭스](#5-요구사항-추적성-매트릭스)

---

## 1. 서론

### 1.1 목적

본 문서는 Team Pomodoro Timer (Focus Mate) 시스템의 소프트웨어 요구사항을 정의합니다.
이 문서는 개발자, 테스터, AI 에이전트가 시스템을 구현하고 검증하기 위한 명확한 기준을 제공합니다.

### 1.2 범위

Focus Mate는 웹 기반 실시간 협업 포모도로 타이머 애플리케이션입니다.

- **포함 범위**: 타이머 동기화, 방 관리, 사용자 통계, 실시간 알림
- **제외 범위**: 모바일 네이티브 앱, 오프라인 모드, 소셜 로그인 (v1.0)

### 1.3 정의 및 약어

- **Pomodoro**: 25분 집중 + 5분 휴식의 시간 관리 기법
- **Room**: 팀원들이 타이머를 공유하는 가상 공간
- **Session**: 하나의 포모도로 사이클 (집중 + 휴식)
- **WebSocket**: 실시간 양방향 통신 프로토콜
- **RTM**: Requirements Traceability Matrix (요구사항 추적성 매트릭스)

### 1.4 참조 문서

- ISO/IEC 25010: Software Quality Model
- ISO/IEC/IEEE 29148: Requirements Engineering
- docs/ARCHITECTURE.md: System Architecture Document
- docs/API_SPECIFICATION.md: API Documentation

---

## 2. 전체 설명

### 2.1 제품 관점

Focus Mate는 클라이언트-서버 아키텍처 기반의 웹 애플리케이션입니다.

- **클라이언트**: React SPA (Single Page Application)
- **서버**: FastAPI 기반 REST API + WebSocket 서버
- **데이터베이스**: SQLite (개발), PostgreSQL (프로덕션 호환)

### 2.2 제품 기능 요약

1. 팀 방 생성 및 관리
2. 실시간 타이머 동기화 (오차 < 1초)
3. 타이머 제어 (시작, 일시정지, 재설정)
4. 포모도로 설정 커스터마이징
5. 브라우저 알림 및 소리 알림
6. 사용자별 통계 및 히스토리

### 2.3 사용자 특성

- **주 사용자**: 원격 근무 팀, 프리랜서, 학습 그룹
- **기술 수준**: 웹 브라우저 사용 가능한 일반 사용자
- **접근성**: WCAG 2.1 Level AA 준수

### 2.4 운영 환경

- **클라이언트**: 최신 브라우저 (Chrome, Firefox, Safari, Edge)
- **서버**: Docker 컨테이너 환경
- **네트워크**: 인터넷 연결 필수 (실시간 동기화)

---

## 3. 기능 요구사항

### 3.1 방 관리 (Room Management)

#### REQ-F-001: 방 생성

**우선순위**: 높음
**설명**: 사용자는 고유한 이름으로 팀 방을 생성할 수 있어야 한다.

**상세 요구사항**:

- 방 이름은 3-50자, 영문/숫자/하이픈/언더스코어만 허용
- 방 생성 시 고유한 공유 URL 자동 생성
- 방 생성자는 자동으로 방장(Host) 권한 획득
- 방 설정: 집중 시간, 휴식 시간, 자동 시작 여부

**입력**:

```json
{
  "room_name": "team-alpha",
  "work_duration_minutes": 25,
  "break_duration_minutes": 5,
  "auto_start_break": true
}
```

**출력**:

```json
{
  "room_id": "uuid-v4",
  "room_name": "team-alpha",
  "share_url": "https://focusmate.app/room/uuid-v4",
  "created_at": "2025-12-04T10:00:00Z"
}
```

**검증 조건**:

- ✅ 중복된 방 이름 허용 (UUID로 구분)
- ✅ 유효하지 않은 방 이름 입력 시 400 에러 반환
- ✅ 방 생성 후 즉시 입장 가능

---

#### REQ-F-002: 방 참여

**우선순위**: 높음
**설명**: 사용자는 공유 URL 또는 방 ID를 통해 기존 방에 참여할 수 있어야 한다.

**상세 요구사항**:

- 존재하지 않는 방 접근 시 404 에러
- 방 입장 시 현재 타이머 상태 즉시 동기화
- 최대 참여 인원: 50명 (설정 가능)

**입력**: `GET /api/v1/rooms/{room_id}`

**출력**:

```json
{
  "room_id": "uuid-v4",
  "room_name": "team-alpha",
  "current_participants": 3,
  "max_participants": 50,
  "timer_state": {
    "status": "running",
    "remaining_seconds": 1234,
    "session_type": "work"
  }
}
```

---

#### REQ-F-003: 방 나가기 및 삭제

**우선순위**: 중간
**설명**: 사용자는 방을 나갈 수 있으며, 방장은 방을 삭제할 수 있어야 한다.

**상세 요구사항**:

- 일반 사용자: 방 나가기 (다른 참여자에게 영향 없음)
- 방장: 방 삭제 시 모든 참여자 강제 퇴장
- 마지막 참여자 퇴장 시 방 자동 삭제 (설정 가능)

---

### 3.2 타이머 동기화 (Timer Synchronization)

#### REQ-F-004: 실시간 타이머 동기화

**우선순위**: 높음 (핵심 기능)
**설명**: 방에 참여한 모든 사용자는 서버 기준의 단일 타이머 상태를 실시간으로 공유받아야 한다.

**상세 요구사항**:

- **정확성**: 클라이언트 간 타이머 오차 < 1초
- **동기화 방식**: 서버가 진실의 원천(Single Source of Truth)
- **클라이언트 계산**: `remaining_time = target_timestamp - current_time`
- **재연결 처리**: 연결 끊김 후 재접속 시 자동 동기화

**WebSocket 메시지 포맷**:

```json
{
  "event": "timer_update",
  "data": {
    "status": "running",
    "session_type": "work",
    "target_timestamp": "2025-12-04T10:25:00Z",
    "work_duration": 1500,
    "break_duration": 300
  }
}
```

**검증 조건**:

- ✅ 네트워크 지연 200ms 환경에서도 오차 < 1초
- ✅ 50명 동시 접속 시 동기화 유지
- ✅ 브라우저 탭 비활성화 시에도 정확한 시간 표시

---

### 3.3 타이머 제어 (Timer Control)

#### REQ-F-005: 타이머 시작

**우선순위**: 높음
**설명**: 권한이 있는 사용자는 타이머를 시작할 수 있어야 한다.

**상세 요구사항**:

- 기본 권한: 방장만 시작 가능
- 옵션: 모든 참여자 시작 가능 (방 설정)
- 이미 실행 중인 타이머 재시작 시 경고 메시지

**API 엔드포인트**: `POST /api/v1/rooms/{room_id}/timer/start`

**응답**:

```json
{
  "status": "success",
  "message": "Timer started",
  "data": {
    "started_at": "2025-12-04T10:00:00Z",
    "target_timestamp": "2025-12-04T10:25:00Z"
  }
}
```

---

#### REQ-F-006: 타이머 일시정지

**우선순위**: 높음
**설명**: 권한이 있는 사용자는 타이머를 일시정지할 수 있어야 한다.

**상세 요구사항**:

- 일시정지 시 남은 시간 저장
- 재개 시 남은 시간부터 계속 진행
- 일시정지 상태는 모든 클라이언트에 즉시 전파

---

#### REQ-F-007: 타이머 재설정

**우선순위**: 중간
**설명**: 권한이 있는 사용자는 타이머를 초기 상태로 재설정할 수 있어야 한다.

**상세 요구사항**:

- 진행 중인 세션 데이터 저장 (통계용)
- 타이머를 설정된 초기 시간으로 리셋
- 확인 다이얼로그 표시 (실수 방지)

---

### 3.4 설정 관리 (Configuration)

#### REQ-F-008: 포모도로 설정

**우선순위**: 중간
**설명**: 사용자는 집중 시간과 휴식 시간을 커스터마이징할 수 있어야 한다.

**상세 요구사항**:

- 집중 시간: 1-60분 (기본 25분)
- 휴식 시간: 1-30분 (기본 5분)
- 긴 휴식 시간: 1-60분 (기본 15분, 4세션마다)
- 자동 시작 옵션: 휴식 후 자동으로 다음 세션 시작

**유효성 검증**:

```python
work_duration: StrictInt = Field(gt=0, le=60)
break_duration: StrictInt = Field(gt=0, le=30)
```

---

### 3.5 알림 (Notifications)

#### REQ-F-009: 타이머 종료 알림

**우선순위**: 중간
**설명**: 타이머 종료 시 사용자에게 알림을 제공해야 한다.

**상세 요구사항**:

- 브라우저 알림 (Notification API)
- 소리 알림 (선택 가능)
- 탭 타이틀 깜빡임 (백그라운드 탭)

**알림 메시지**:

- 집중 시간 종료: "🎉 집중 시간 완료! 휴식 시간입니다."
- 휴식 시간 종료: "⏰ 휴식 종료! 다음 세션을 시작하세요."

---

### 3.6 통계 및 히스토리 (Statistics)

#### REQ-F-010: 사용자 통계

**우선순위**: 낮음 (v1.1)
**설명**: 사용자는 자신의 포모도로 수행 기록을 확인할 수 있어야 한다.

**상세 요구사항**:

- 오늘 완료한 포모도로 수
- 주간/월간 통계
- 총 집중 시간
- 세션 완료율

---

## 4. 비기능 요구사항

### 4.1 성능 효율성 (Performance Efficiency)

#### REQ-NF-001: API 응답 시간

**우선순위**: 높음
**메트릭**: 95분위(p95) 응답 시간 < 200ms

**측정 방법**:

- Load Testing: Locust 또는 k6 사용
- 모니터링: Prometheus + Grafana

---

#### REQ-NF-002: WebSocket 지연

**우선순위**: 높음
**메트릭**: 타이머 상태 변경 이벤트 전파 < 100ms

**검증 조건**:

- 50명 동시 접속 환경에서 측정
- 네트워크 지연 50ms 가정

---

#### REQ-NF-003: 동시 접속 처리

**우선순위**: 중간
**메트릭**: 최소 100개 방, 방당 50명 동시 지원

**부하 테스트 시나리오**:

```python
# Locust 테스트
class PomodoroUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def join_room_and_sync(self):
        # 방 참여 및 타이머 동기화 시뮬레이션
        pass
```

---

### 4.2 신뢰성 (Reliability)

#### REQ-NF-004: 타입 안정성

**우선순위**: 높음
**메트릭**:

- Python: mypy --strict 통과 (Any 타입 0개)
- TypeScript: strict: true, 타입 에러 0개

**검증 방법**:

```bash
# Backend
mypy src/backend/app --strict

# Frontend
tsc --noEmit
```

---

#### REQ-NF-005: 테스트 커버리지

**우선순위**: 높음
**메트릭**:

- 라인 커버리지 > 90%
- 분기 커버리지 > 85%

**검증 방법**:

```bash
# Backend
pytest --cov=app --cov-report=term-missing --cov-fail-under=90

# Frontend
npm test -- --coverage --coverageThreshold='{"global":{"lines":90}}'
```

---

#### REQ-NF-006: 결함 허용성

**우선순위**: 중간
**요구사항**:

- WebSocket 연결 끊김 시 자동 재연결 (지수 백오프)
- 재연결 후 타이머 상태 자동 동기화
- 서버 오류 시 사용자 친화적 에러 메시지

**재연결 로직**:

```typescript
const reconnect = (attempt: number) => {
  const delay = Math.min(1000 * 2 ** attempt, 30000); // 최대 30초
  setTimeout(() => connectWebSocket(), delay);
};
```

---

### 4.3 유지보수성 (Maintainability)

#### REQ-NF-007: 코드 복잡도

**우선순위**: 높음
**메트릭**:

- Cyclomatic Complexity < 10 (함수당)
- Maintainability Index > 20 (Grade A)

**검증 방법**:

```bash
# Backend
radon cc src/backend/app --min A

# Frontend
eslint --rule 'complexity: ["error", 10]'
```

---

#### REQ-NF-008: 모듈성

**우선순위**: 중간
**요구사항**:

- 높은 응집도 (High Cohesion)
- 낮은 결합도 (Low Coupling)
- 의존성 주입 패턴 사용

**아키텍처 원칙**:

- Backend: 레이어드 아키텍처 (API → Service → Repository)
- Frontend: Atomic Design 패턴

---

### 4.4 보안성 (Security)

#### REQ-NF-009: 입력 검증

**우선순위**: 높음
**요구사항**:

- 모든 API 입력은 Pydantic Strict 모드로 검증
- SQL Injection 방지 (ORM 사용)
- XSS 방지 (입력 sanitization)

---

#### REQ-NF-010: 인증 및 권한

**우선순위**: 중간 (v1.1)
**요구사항**:

- JWT 기반 인증
- 방별 권한 관리 (방장, 참여자)
- HTTPS 강제

---

### 4.5 이식성 (Portability)

#### REQ-NF-011: 컨테이너화

**우선순위**: 높음
**요구사항**:

- 모든 서비스는 Docker 컨테이너로 실행
- `docker-compose up` 명령 하나로 전체 스택 실행
- 환경 변수를 통한 설정 관리

---

#### REQ-NF-012: 브라우저 호환성

**우선순위**: 중간
**지원 브라우저**:

- Chrome/Edge: 최신 2개 버전
- Firefox: 최신 2개 버전
- Safari: 최신 2개 버전

---

## 5. 요구사항 추적성 매트릭스

| 요구사항 ID | 기능 설명       | 우선순위 | 구현 모듈                            | 테스트 케이스   | 상태   |
| ----------- | --------------- | -------- | ------------------------------------ | --------------- | ------ |
| REQ-F-001   | 방 생성         | 높음     | `services/room.py`, `RoomCreate.tsx` | TC-ROOM-001     | 미구현 |
| REQ-F-002   | 방 참여         | 높음     | `services/room.py`, `RoomJoin.tsx`   | TC-ROOM-002     | 미구현 |
| REQ-F-004   | 타이머 동기화   | 높음     | `services/timer.py`, `useTimer.ts`   | TC-TIMER-001    | 미구현 |
| REQ-F-005   | 타이머 시작     | 높음     | `api/timer.py`, `TimerControls.tsx`  | TC-TIMER-002    | 미구현 |
| REQ-F-009   | 알림            | 중간     | `hooks/useNotification.ts`           | TC-NOTIF-001    | 미구현 |
| REQ-NF-001  | API 응답 시간   | 높음     | 전체 백엔드                          | TC-PERF-001     | 미구현 |
| REQ-NF-004  | 타입 안정성     | 높음     | 전체 코드베이스                      | CI/CD 자동 검증 | 미구현 |
| REQ-NF-005  | 테스트 커버리지 | 높음     | 전체 코드베이스                      | CI/CD 자동 검증 | 미구현 |
| REQ-NF-007  | 코드 복잡도     | 높음     | 전체 코드베이스                      | CI/CD 자동 검증 | 미구현 |

---

## 6. 부록

### 6.1 변경 이력

| 버전 | 날짜       | 작성자  | 변경 내용      |
| ---- | ---------- | ------- | -------------- |
| 1.0  | 2025-12-04 | AI Team | 초기 버전 작성 |

### 6.2 승인

- [ ] 프로젝트 관리자
- [ ] 기술 리드
- [ ] QA 리드

---

**문서 끝**
