# ADR-004: Zustand 상태 관리 라이브러리

**날짜**: 2025-12-04
**상태**: 승인됨
**결정자**: 아키텍처 팀

---

## 컨텍스트 (Context)

React 애플리케이션에서 전역 상태 관리가 필요했습니다.
타이머 상태, 방 정보, 사용자 설정 등을 여러 컴포넌트에서 공유해야 합니다.

고려한 옵션:

1. **Redux Toolkit**: 업계 표준, 강력한 기능
2. **Zustand**: 경량, 단순한 API
3. **Jotai**: 원자적 상태 관리
4. **Context API**: 내장 솔루션

ISO/IEC 25010의 **유지보수성(Maintainability)** 특성 중 **모듈성(Modularity)**과 **변경 용이성(Modifiability)**을 고려해야 했습니다.

---

## 결정 (Decision)

**Zustand**를 상태 관리 라이브러리로 선택합니다.

**이유**:

- 최소한의 보일러플레이트
- TypeScript 우수한 지원
- 낮은 학습 곡선
- 충분한 기능

---

## 근거 (Rationale)

### 1. 단순성 (Simplicity)

**코드 비교**:

**Redux Toolkit**:

```typescript
// store.ts
import { configureStore, createSlice } from "@reduxjs/toolkit";

const timerSlice = createSlice({
  name: "timer",
  initialState: { remainingSeconds: 1500 },
  reducers: {
    setRemaining: (state, action) => {
      state.remainingSeconds = action.payload;
    },
  },
});

export const store = configureStore({
  reducer: {
    timer: timerSlice.reducer,
  },
});

// 사용
import { useDispatch, useSelector } from "react-redux";
const remaining = useSelector((state) => state.timer.remainingSeconds);
const dispatch = useDispatch();
```

**Zustand**:

```typescript
// store.ts
import create from "zustand";

interface TimerStore {
  remainingSeconds: number;
  setRemaining: (seconds: number) => void;
}

export const useTimerStore = create<TimerStore>((set) => ({
  remainingSeconds: 1500,
  setRemaining: (seconds) => set({ remainingSeconds: seconds }),
}));

// 사용
const remaining = useTimerStore((state) => state.remainingSeconds);
const setRemaining = useTimerStore((state) => state.setRemaining);
```

**결과**: Zustand가 70% 적은 코드로 동일한 기능 제공

### 2. 유지보수성

**ISO 25010 모듈성 준수**:

- **낮은 결합도**: 컴포넌트가 필요한 상태만 선택적 구독
- **높은 응집도**: 관련 상태가 하나의 스토어에 그룹화
- **변경 용이성**: 스토어 구조 변경 시 영향 범위 최소화

### 3. 성능

**선택적 리렌더링**:

```typescript
// 필요한 상태만 구독 (자동 최적화)
const remaining = useTimerStore((state) => state.remainingSeconds);

// 다른 상태 변경 시 리렌더링 없음
```

### 4. TypeScript 지원

**완벽한 타입 추론**:

```typescript
// 타입 자동 추론
const { remainingSeconds, setRemaining } = useTimerStore();
// remainingSeconds: number
// setRemaining: (seconds: number) => void
```

---

## 대안 (Alternatives)

### 대안 1: Redux Toolkit

**장점**:

- 업계 표준
- 강력한 DevTools
- 미들웨어 생태계
- 대규모 팀에서 검증됨

**단점**:

- 보일러플레이트 많음
- 학습 곡선 높음
- 작은 프로젝트에는 과함

**결론**: 프로젝트 규모에 비해 과도하여 채택하지 않음

### 대안 2: Context API

**장점**:

- 추가 의존성 없음
- React 내장

**단점**:

- 성능 이슈 (불필요한 리렌더링)
- Provider 지옥 가능
- 복잡한 상태 관리 어려움

**결론**: 전역 상태 관리에 부적합하여 채택하지 않음

### 대안 3: Jotai

**장점**:

- 원자적 상태 관리
- 세밀한 최적화

**단점**:

- 학습 곡선 존재
- 생태계 작음
- 프로젝트 요구사항에 과함

**결론**: 프로젝트 요구사항에 비해 복잡하여 채택하지 않음

---

## 결과 (Consequences)

### 긍정적 결과

✅ **개발 속도**: 적은 보일러플레이트로 빠른 개발
✅ **코드 가독성**: 직관적인 API
✅ **유지보수성**: 단순한 구조로 이해하기 쉬움
✅ **성능**: 선택적 리렌더링으로 최적화
✅ **TypeScript**: 완벽한 타입 지원

### 부정적 결과

⚠️ **생태계**: Redux 대비 플러그인/미들웨어 적음
⚠️ **대규모 프로젝트**: 매우 복잡한 상태 관리에는 제한적

### 완화 전략

- **필요 시 마이그레이션**: 프로젝트 성장 시 Redux로 전환 가능
- **하이브리드 접근**: 복잡한 상태는 Zustand, 단순 상태는 Context API

---

## 사용 예시

### 타이머 스토어

```typescript
// stores/timerStore.ts
import create from "zustand";

interface TimerState {
  status: "idle" | "running" | "paused";
  remainingSeconds: number;
  sessionType: "work" | "break";
  start: () => void;
  pause: () => void;
  reset: () => void;
  tick: () => void;
}

export const useTimerStore = create<TimerState>((set) => ({
  status: "idle",
  remainingSeconds: 1500,
  sessionType: "work",

  start: () => set({ status: "running" }),
  pause: () => set({ status: "paused" }),
  reset: () => set({ status: "idle", remainingSeconds: 1500 }),
  tick: () =>
    set((state) => ({
      remainingSeconds: Math.max(0, state.remainingSeconds - 1),
    })),
}));
```

### 컴포넌트에서 사용

```typescript
// components/TimerDisplay.tsx
import { useTimerStore } from "@/stores/timerStore";

export const TimerDisplay = () => {
  const remainingSeconds = useTimerStore((state) => state.remainingSeconds);
  const status = useTimerStore((state) => state.status);

  return (
    <div>
      <span>{formatTime(remainingSeconds)}</span>
      <span>{status}</span>
    </div>
  );
};
```

---

## 참조 (References)

- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [ISO/IEC 25010 - Maintainability](https://iso25000.com/index.php/en/iso-25000-standards/iso-25010)
- [ARCHITECTURE.md](./../ARCHITECTURE.md#adr-004-zustand-상태-관리): 아키텍처 문서
- [CODING_STANDARDS.md](./../CODING_STANDARDS.md#32-typescript-코딩-표준): 프론트엔드 코딩 표준

---

**문서 끝**
