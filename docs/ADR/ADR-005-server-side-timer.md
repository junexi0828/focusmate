# ADR-005: 서버 사이드 타이머 로직

**날짜**: 2025-12-04
**상태**: 승인됨
**결정자**: 아키텍처 팀

---

## 컨텍스트 (Context)

타이머 동기화는 Focus Mate의 핵심 기능입니다.
여러 클라이언트가 동일한 타이머 상태를 실시간으로 공유해야 합니다.

두 가지 접근 방식:

1. **클라이언트 사이드**: 각 클라이언트가 독립적으로 타이머 계산
2. **서버 사이드**: 서버가 타이머 상태를 관리하고 클라이언트에 전파

REQ-F-004 (타이머 동기화) 요구사항에 따르면 **클라이언트 간 타이머 오차 < 1초**를 보장해야 합니다.

---

## 결정 (Decision)

**서버 사이드 타이머 로직**을 채택합니다.

**아키텍처**:

- 서버가 타이머의 **진실의 원천(Single Source of Truth)**
- 클라이언트는 `target_timestamp`를 받아 로컬에서 남은 시간 계산
- 서버는 상태 변경 시에만 브로드캐스트 (대역폭 절약)

---

## 근거 (Rationale)

### 1. 정확성 보장

**문제**: 클라이언트 사이드 타이머의 한계

```typescript
// 클라이언트 사이드 (문제)
setInterval(() => {
  setRemainingSeconds((prev) => prev - 1);
}, 1000);
```

**문제점**:

- 브라우저 탭 비활성화 시 `setInterval` 정지
- CPU 스로틀링으로 정확도 저하
- 네트워크 지연으로 클라이언트 간 불일치

**해결**: 서버 사이드

```python
# 서버 사이드 (해결)
target_timestamp = datetime.utcnow() + timedelta(seconds=1500)
remaining = (target_timestamp - datetime.utcnow()).total_seconds()
```

**장점**:

- 서버 시간 기준으로 정확한 계산
- 클라이언트는 `target_timestamp`만 받아 로컬 계산
- 재연결 시 자동 동기화

### 2. ISO 25010 신뢰성 준수

**REQ-F-004 요구사항**:

- 타이머 오차 < 1초
- 네트워크 지연 200ms 환경에서도 정확성 유지

**서버 사이드 접근**:

- 서버가 정확한 `target_timestamp` 제공
- 클라이언트는 현재 시간과 비교하여 남은 시간 계산
- 네트워크 지연과 무관하게 정확성 보장

### 3. 확장성

**다중 클라이언트 지원**:

- 서버가 단일 타이머 상태 관리
- 모든 클라이언트에 동일한 상태 브로드캐스트
- 50명 동시 접속 시에도 정확성 유지

---

## 대안 (Alternatives)

### 대안 1: 클라이언트 사이드 타이머

**장점**:

- 서버 부하 적음
- 오프라인 모드 가능

**단점**:

- 클라이언트 간 불일치
- 브라우저 제약 (탭 비활성화, 스로틀링)
- REQ-F-004 요구사항 미충족

**결론**: 정확성 요구사항을 충족하지 못하여 채택하지 않음

### 대안 2: 하이브리드 (클라이언트 계산 + 주기적 동기화)

**장점**:

- 서버 부하 감소
- 오프라인 모드 가능

**단점**:

- 복잡도 증가
- 동기화 주기 설정 어려움
- 여전히 불일치 가능성

**결론**: 복잡도 증가 대비 이점 부족하여 채택하지 않음

---

## 결과 (Consequences)

### 긍정적 결과

✅ **정확성**: 서버 시간 기준으로 정확한 타이머
✅ **동기화**: 모든 클라이언트가 동일한 상태
✅ **신뢰성**: REQ-F-004 요구사항 충족
✅ **재연결 복원력**: 재접속 시 자동 동기화

### 부정적 결과

⚠️ **서버 부하**: WebSocket 연결 관리 필요
⚠️ **네트워크 의존성**: 오프라인 모드 불가 (v1.0)

### 완화 전략

**서버 부하**:

- 상태 변경 시에만 브로드캐스트 (1초마다가 아님)
- 효율적인 WebSocket 메시지 포맷

**오프라인 모드**:

- v1.1에서 로컬 폴백 모드 고려

---

## 구현 상세

### 서버 사이드 로직

```python
# services/timer_service.py
from datetime import datetime, timedelta

class TimerService:
    def start_timer(
        self,
        room_id: str,
        duration_seconds: int
    ) -> TimerState:
        """
        타이머 시작.
        서버 시간 기준으로 target_timestamp 계산.
        """
        target_timestamp = datetime.utcnow() + timedelta(seconds=duration_seconds)

        return TimerState(
            status=TimerStatus.RUNNING,
            target_timestamp=target_timestamp,
            started_at=datetime.utcnow()
        )

    def get_remaining_seconds(
        self,
        target_timestamp: datetime
    ) -> int:
        """
        남은 시간 계산.
        클라이언트도 동일한 로직 사용 가능.
        """
        if target_timestamp is None:
            return 0

        remaining = (target_timestamp - datetime.utcnow()).total_seconds()
        return max(0, int(remaining))
```

### 클라이언트 사이드 로직

```typescript
// hooks/useTimer.ts
import { useEffect, useState } from "react";

export const useTimer = (targetTimestamp: string | null) => {
  const [remainingSeconds, setRemainingSeconds] = useState(0);

  useEffect(() => {
    if (!targetTimestamp) {
      setRemainingSeconds(0);
      return;
    }

    const updateRemaining = () => {
      const target = new Date(targetTimestamp);
      const now = new Date();
      const remaining = Math.max(
        0,
        Math.floor((target.getTime() - now.getTime()) / 1000)
      );
      setRemainingSeconds(remaining);
    };

    // 즉시 업데이트
    updateRemaining();

    // 1초마다 업데이트
    const interval = setInterval(updateRemaining, 1000);

    return () => clearInterval(interval);
  }, [targetTimestamp]);

  return remainingSeconds;
};
```

### WebSocket 메시지 포맷

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

## 검증

### 테스트 시나리오

```python
# tests/integration/test_timer_sync.py
def test_timer_synchronization_multiple_clients():
    """
    TC-SYNC-001: 다중 클라이언트 타이머 동기화
    REQ-F-004 검증
    """
    # Client A, B 동시 연결
    # Client A가 타이머 시작
    # 두 클라이언트의 target_timestamp 차이 < 1초 검증
    pass
```

---

## 참조 (References)

- [SRS.md](./../SRS.md#req-f-004-실시간-타이머-동기화): REQ-F-004 요구사항
- [ARCHITECTURE.md](./../ARCHITECTURE.md#222-타이머-동기화-메커니즘): 아키텍처 문서
- [API_SPECIFICATION.md](./../API_SPECIFICATION.md#4-websocket-프로토콜): WebSocket 프로토콜

---

**문서 끝**
