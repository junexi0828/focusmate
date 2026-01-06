# Future Feature Ideas

## 1. 타이머 제어 권한 설정 (Timer Control Permissions)

### 개요
방장이 타이머 제어 권한을 설정할 수 있는 기능. 기본적으로는 모든 참여자가 타이머를 제어할 수 있지만, 방장이 원할 경우 자신만 제어하도록 제한 가능.

### 현재 상태
- ✅ **방 삭제 권한**: 방장만 가능 (`RoomHostRequiredException`으로 구현됨)
- ✅ **타이머 제어**: 모든 참여자 가능 (권한 체크 없음)

### 요구사항
- 방 설정에 "모든 참여자 타이머 제어 허용" 토글 추가
- 방장만 이 설정을 변경할 수 있음
- 설정이 꺼져 있을 때는 방장만 타이머 시작/일시정지/재개/리셋 가능
- 권한이 없는 사용자에게는 타이머 버튼이 비활성화되어야 함

### 구현 계획

#### 1. 데이터 모델 확장
**Room 테이블**
```python
allow_all_control: Mapped[bool] = mapped_column(
    Boolean,
    nullable=False,
    default=True,
    comment="Allow all participants to control timer (default: True)",
)
```

#### 2. 백엔드 로직
**타이머 엔드포인트 권한 체크**
```python
# app/api/v1/endpoints/timer.py
async def check_timer_control_permission(room_id: str, user_id: str):
    room = await room_repo.get_by_id(room_id)
    if not room.allow_all_control and room.host_id != user_id:
        raise TimerControlPermissionException(room_id)
```

**적용 대상 엔드포인트**
- `POST /timer/{room_id}/start`
- `POST /timer/{room_id}/pause`
- `POST /timer/{room_id}/resume`
- `POST /timer/{room_id}/reset`

#### 3. 프론트엔드 UI
**방 설정 페이지**
- "모든 참여자 타이머 제어 허용" 토글 추가
- 방장만 수정 가능하도록 조건부 렌더링

**타이머 화면**
- 권한이 없을 때 버튼 비활성화
- 툴팁으로 "방장만 타이머를 제어할 수 있습니다" 표시

### 우선순위
- **Priority**: Medium (Nice-to-have)
- **Estimated Effort**: 2-3 hours
- **Dependencies**: 없음 (독립적으로 구현 가능)

### 사용 시나리오
- **스터디 그룹**: 방장이 시간 관리를 주도하고 싶을 때
- **강의/세미나**: 진행자만 타이머를 제어하고 참여자는 따라가는 형태
- **자유 모드**: 모든 참여자가 자유롭게 타이머 조작 (기본값)

---

## 2. 연속 세션 추적 및 긴 휴식 (Long Break)

### 개요
사용자의 연속 집중 세션을 추적하고, 4세션마다 긴 휴식(15-30분)을 권장하는 기능.

### 요구사항
- **연속 세션 카운터**: 사용자가 완료한 연속 work 세션 수를 추적
- **긴 휴식 트리거**: 4세션 완료 시 자동으로 긴 휴식 제안
- **통계 연동**: 연속 달성 기록을 통계에 반영 (최장 연속 기록, 오늘의 연속 기록 등)

### 구현 계획

#### 1. 데이터 모델 확장
**Room 테이블**
```python
long_break_duration: int = 15  # 긴 휴식 시간 (분)
long_break_interval: int = 4   # 긴 휴식 주기 (세션 수)
```

**SessionHistory 테이블**
```python
streak_count: int  # 해당 세션이 몇 번째 연속 세션인지
is_long_break: bool  # 긴 휴식 세션 여부
```

#### 2. 비즈니스 로직
- `complete_phase` 호출 시 연속 카운터 증가
- 4의 배수 달성 시 `long_break` 페이즈로 전환
- 중간에 리셋하거나 이탈 시 카운터 초기화

#### 3. UI/UX
- 타이머 화면에 "🔥 연속 3세션 달성!" 배지 표시
- 4세션 완료 시 "긴 휴식을 권장합니다" 모달
- 통계 페이지에 "최장 연속 기록" 표시

### 우선순위
- **Priority**: Low (Nice-to-have)
- **Estimated Effort**: 1-2 days
- **Dependencies**: 현재 타이머 시스템 안정화 후 진행

### 참고
- Pomodoro 기법의 표준 패턴
- 사용자 피로도 관리 및 장기 집중력 향상에 기여
