# 프론트엔드 개발 Todo

**작성일**: 2025-12-04
**최종 업데이트**: 2025-12-04
**백엔드 API Base URL**: `http://localhost:8000/api/v1`
**WebSocket Base URL**: `ws://localhost:8000`

---

## 📋 현재 상태 분석

### ✅ 완료된 작업

1. ✅ 프론트엔드 기본 구조 (features 기반 모듈화)
2. ✅ API 클라이언트 베이스 클래스 (`lib/api/base.ts`)
3. ✅ Feature별 서비스 레이어 (room, timer, participants)
4. ✅ WebSocket 클라이언트 기본 구조 (`lib/websocket.ts`)
5. ✅ UI 컴포넌트 (shadcn/ui 기반)
6. ✅ 페이지 구조 (Home, Room, Stats, Community, Messages, Profile, Auth)
7. ✅ **환경 변수 설정 파일** (`.env.example`)
8. ✅ **로딩 스피너 컴포넌트** (`components/ui/loading.tsx`)
9. ✅ **에러 처리 개선** (`BaseApiClient`)

### ✅ Phase 1 완료된 작업

#### 1.1 Room 기능 연동 ✅

- ✅ **Room 생성 API 연동**

  - ✅ `HomePage`의 `onCreateRoom`에서 `roomService.createRoom()` 호출
  - ✅ API 응답에서 `room_id` 받아서 `/room/:roomId`로 라우팅
  - ✅ 에러 처리 (validation error, network error 등)
  - ✅ 로딩 상태 표시

- ✅ **Room 조회 API 연동**

  - ✅ `RoomPage` 마운트 시 `roomService.getRoom(roomId)` 호출
  - ✅ 방 정보 (이름, 설정, 타이머 상태) 서버에서 가져오기
  - ✅ 방이 없을 경우 404 처리 및 홈으로 리다이렉트

- ✅ **Room 설정 업데이트 API 연동**

  - ✅ `RoomSettingsDialog`에서 `roomService.updateRoomSettings()` 호출
  - ✅ 성공 시 로컬 상태 업데이트
  - ✅ 에러 처리 및 사용자 피드백

- ✅ **Room 삭제 API 연동**
  - ✅ 방장만 삭제 가능하도록 권한 체크
  - ✅ `roomService.deleteRoom()` 호출
  - ✅ 삭제 성공 시 홈으로 리다이렉트

#### 1.2 Timer 기능 연동 ✅

- ✅ **서버 사이드 타이머 상태 관리**

  - ✅ `useServerTimer` 훅 생성 (서버 상태 기반)
  - ✅ `RoomPage`에서 서버 타이머 상태 동기화
  - ✅ 클라이언트 타이머는 서버 `target_timestamp` 기반으로 계산

- ✅ **타이머 제어 API 연동**

  - ✅ `timerService.startTimer()` - 타이머 시작
  - ✅ `timerService.pauseTimer()` - 타이머 일시정지
  - ✅ `timerService.resumeTimer()` - 타이머 재개
  - ✅ `timerService.resetTimer()` - 타이머 리셋
  - ✅ 각 API 호출 후 서버 응답으로 상태 업데이트

- ✅ **타이머 완료 처리**
  - ✅ 서버에서 `timer_complete` 이벤트 수신 시 처리
  - ✅ 자동 휴식 시작 옵션 처리
  - ✅ 알림 표시

#### 1.3 WebSocket 실시간 동기화 ✅

- ✅ **WebSocket 연결 관리**

  - ✅ `RoomPage`에서 방 입장 시 WebSocket 연결
  - ✅ 방 나갈 때 WebSocket 연결 해제
  - ✅ 재연결 로직 개선 (exponential backoff)

- ✅ **타이머 상태 실시간 동기화**

  - ✅ `timer_update` 이벤트 수신 시 타이머 상태 업데이트
  - ✅ 서버 `target_timestamp` 기반으로 클라이언트 타이머 계산
  - ✅ 네트워크 지연 보정

- ✅ **참여자 목록 실시간 동기화**

  - ✅ `participant_update` 이벤트 수신 시 참여자 목록 업데이트
  - ⚠️ 참여자 입장/퇴장 애니메이션 (추가 개선 가능)

- ✅ **타이머 제어 WebSocket 메시지 전송**

  - ✅ 타이머 시작/일시정지/재개/리셋 시 WebSocket으로 메시지 전송
  - ✅ REST API와 WebSocket 병행 사용

- ✅ **Heartbeat 구현**
  - ✅ 주기적으로 `ping` 메시지 전송 (30초마다)
  - ✅ `pong` 응답 확인으로 연결 상태 체크

#### 1.4 Participants 기능 연동 ✅

- ✅ **참여자 입장 API 연동**

  - ✅ `RoomPage` 마운트 시 `participantService.joinRoom()` 호출
  - ✅ 사용자 이름 입력 받기 (로컬 스토리지에서 가져오기)
  - ✅ 참여자 ID 저장 (나중에 퇴장 시 사용)

- ✅ **참여자 목록 조회 API 연동**

  - ✅ `participantService.getParticipants()` 호출
  - ✅ WebSocket 이벤트로 업데이트

- ✅ **참여자 퇴장 API 연동**
  - ✅ `RoomPage` 언마운트 시 `participantService.leaveRoom()` 호출
  - ✅ 에러 처리

---

## 🎯 다음 작업 (우선순위 순)

### Phase 2: 에러 처리 및 사용자 경험 개선 (우선순위: 중간)

#### 2.1 에러 처리 개선

- [ ] **에러 바운더리 구현**

  - [ ] React Error Boundary 추가
  - [ ] 예상치 못한 에러 발생 시 폴백 UI

- [ ] **WebSocket 에러 처리 개선**
  - [x] 연결 실패 시 재시도 로직 (완료)
  - [ ] 연결 끊김 시 사용자 알림 개선
  - [ ] 에러 이벤트 처리 개선

#### 2.2 로딩 상태 개선

- [x] **로딩 스피너 컴포넌트** ✅

  - [x] 공통 로딩 컴포넌트 생성
  - [x] API 호출 중 로딩 상태 표시

- [ ] **스켈레톤 UI**
  - [ ] Room 페이지 로딩 시 스켈레톤 UI
  - [ ] 참여자 목록 로딩 스켈레톤

#### 2.3 사용자 피드백 개선

- [x] **Toast 알림 개선** ✅

  - [x] API 성공/실패 시 적절한 메시지 표시
  - [x] WebSocket 연결 상태 알림

- [x] **폼 유효성 검사** ✅
  - [x] Room 생성 폼 유효성 검사 (room_name 패턴 등)
  - [x] 에러 메시지 표시

---

### Phase 3: 추가 기능 연동 (우선순위: 낮음)

#### 3.1 통계 기능

- [ ] **통계 API 연동**
  - [ ] `StatsPage`에서 통계 데이터 조회
  - [ ] 기간별 필터링 (today, week, month)
  - [ ] 차트 데이터 시각화

#### 3.2 커뮤니티 기능

- [ ] **커뮤니티 API 연동**
  - [ ] 게시글 목록 조회
  - [ ] 게시글 작성
  - [ ] 댓글 기능

#### 3.3 메시징 기능

- [ ] **메시징 API 연동**
  - [ ] 대화 목록 조회
  - [ ] 메시지 전송/수신
  - [ ] 실시간 메시지 동기화

#### 3.4 인증 기능 (v1.1)

- [ ] **JWT 인증 구현**
  - [ ] 로그인/회원가입 API 연동
  - [ ] 토큰 저장 및 관리
  - [ ] API 요청 시 토큰 포함
  - [ ] 토큰 만료 시 자동 갱신

---

## 🔧 기술적 개선 사항

### 코드 품질

- [x] **타입 안정성 강화** ✅

  - [x] API 응답 타입 정확히 정의
  - [x] WebSocket 메시지 타입 정의
  - [ ] TypeScript strict mode 활성화 (검토 필요)

- [x] **에러 타입 정의** ✅
  - [x] 백엔드 에러 코드와 매핑
  - [x] 타입 안전한 에러 처리

### 성능 최적화

- [ ] **API 호출 최적화**

  - [ ] 불필요한 API 호출 제거
  - [ ] 캐싱 전략 (React Query 또는 SWR 고려)

- [ ] **WebSocket 최적화**
  - [ ] 메시지 배치 처리
  - [ ] 불필요한 리렌더링 방지 (React.memo, useMemo 활용)

### 테스트

- [ ] **단위 테스트**

  - [ ] API 서비스 테스트
  - [ ] 훅 테스트

- [ ] **통합 테스트**
  - [ ] API 연동 테스트
  - [ ] WebSocket 연결 테스트

---

## 📊 진행률 요약

### Phase 1: 핵심 기능 백엔드 연동

- **완료율**: 100% ✅
  - Room 기능: 100% ✅
  - Timer 기능: 100% ✅
  - WebSocket: 100% ✅
  - Participants: 100% ✅

### Phase 2: 에러 처리 및 사용자 경험 개선

- **완료율**: 60%
  - 에러 처리: 70%
  - 로딩 상태: 50%
  - 사용자 피드백: 100% ✅

### Phase 3: 추가 기능 연동

- **완료율**: 0%
  - 통계: 0%
  - 커뮤니티: 0%
  - 메시징: 0%
  - 인증: 0%

---

## 🚀 다음 단계 추천

### 즉시 진행 가능한 작업 (우선순위 높음)

1. **스켈레톤 UI 추가**

   - Room 페이지 로딩 시 스켈레톤 UI
   - 참여자 목록 로딩 스켈레톤
   - **예상 시간**: 1-2시간

2. **에러 바운더리 구현**

   - React Error Boundary 추가
   - 예상치 못한 에러 발생 시 폴백 UI
   - **예상 시간**: 1시간

3. **WebSocket 연결 상태 UI 개선**
   - 연결 상태 표시 (연결됨/연결 끊김)
   - 재연결 시도 중 표시
   - **예상 시간**: 1시간

### 중기 작업 (우선순위 중간)

4. **성능 최적화**

   - React.memo, useMemo 활용
   - 불필요한 리렌더링 방지
   - **예상 시간**: 2-3시간

5. **API 호출 최적화**
   - React Query 또는 SWR 도입 검토
   - 캐싱 전략 수립
   - **예상 시간**: 3-4시간

### 장기 작업 (우선순위 낮음)

6. **통계 기능 연동**

   - StatsPage API 연동
   - 차트 데이터 시각화
   - **예상 시간**: 4-5시간

7. **커뮤니티/메시징 기능**
   - 각 기능별 API 연동
   - **예상 시간**: 각 5-6시간

---

## 📝 구현 가이드

### API 연동 패턴

```typescript
// 예시: Room 생성
const handleCreateRoom = async (
  roomName: string,
  focusTime: number,
  breakTime: number
) => {
  try {
    setLoading(true);
    const response = await roomService.createRoom({
      room_name: roomName,
      work_duration_minutes: focusTime,
      break_duration_minutes: breakTime,
    });

    if (response.status === "success" && response.data) {
      navigate(`/room/${response.data.room_id}`);
    } else {
      toast.error(response.error?.message || "방 생성에 실패했습니다");
    }
  } catch (error) {
    toast.error("네트워크 오류가 발생했습니다");
  } finally {
    setLoading(false);
  }
};
```

### WebSocket 연동 패턴

```typescript
// 예시: RoomPage에서 WebSocket 사용
useEffect(() => {
  wsClient.connect(roomId);

  const unsubscribe = wsClient.onMessage((message) => {
    if (message.event === "timer_update") {
      updateTimerState(message.data);
    } else if (message.event === "participant_update") {
      updateParticipants(message.data);
    }
  });

  return () => {
    unsubscribe();
    wsClient.disconnect();
  };
}, [roomId]);
```

---

## 📌 참고 사항

1. **백엔드 개발과 병행**

   - 백엔드 API가 준비되면 즉시 연동 가능하도록 구조화 완료 ✅
   - Mock 데이터를 쉽게 제거할 수 있도록 분리 완료 ✅

2. **환경 변수 설정**

   - `.env.example` 파일 생성 완료 ✅
   - `.env` 파일에 `VITE_API_BASE_URL` 설정 필요
   - `.env` 파일에 `VITE_WS_BASE_URL` 설정 필요

3. **API 스펙 확인**

   - `docs/API_SPECIFICATION.md` 참고
   - 백엔드 개발자와 API 스펙 일치 확인 필요

4. **타입 정의**
   - 백엔드 API 응답과 프론트엔드 타입 일치 확인 완료 ✅
   - 타입 불일치 시 백엔드 개발자와 협의

---

## ✅ 완료된 주요 기능

### Room 기능

- ✅ 방 생성 (API 연동)
- ✅ 방 조회 (API 연동)
- ✅ 방 설정 업데이트 (API 연동)
- ✅ 방 삭제 (API 연동)
- ✅ 방 참여 (API 연동)

### Timer 기능

- ✅ 타이머 시작 (API + WebSocket)
- ✅ 타이머 일시정지 (API + WebSocket)
- ✅ 타이머 재개 (API + WebSocket)
- ✅ 타이머 리셋 (API + WebSocket)
- ✅ 실시간 타이머 동기화 (WebSocket)
- ✅ 타이머 완료 처리

### Participants 기능

- ✅ 참여자 입장 (API 연동)
- ✅ 참여자 목록 조회 (API 연동)
- ✅ 참여자 퇴장 (API 연동)
- ✅ 실시간 참여자 목록 업데이트 (WebSocket)

### WebSocket 기능

- ✅ WebSocket 연결 관리
- ✅ 실시간 타이머 동기화
- ✅ 실시간 참여자 목록 동기화
- ✅ Heartbeat (ping/pong)
- ✅ 재연결 로직 (exponential backoff)

---

**마지막 업데이트**: 2025-12-04
