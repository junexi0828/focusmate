# 알림 서비스 구현 상태

## 현재 상태

### ✅ 구현된 부분

1. **데이터베이스 모델**

   - `UserSettings` 모델에 알림 설정 필드들이 모두 존재:
     - `notification_email`: 이메일 알림
     - `notification_push`: 푸시 알림
     - `notification_session`: 세션 알림
     - `notification_achievement`: 업적 알림
     - `notification_message`: 메시지 알림

2. **알림 생성 서비스**

   - `NotificationService`: 알림 생성 및 관리
   - `NotificationHelper`: 다양한 타입의 알림 생성 헬퍼
   - WebSocket을 통한 실시간 알림 전송

3. **프론트엔드 알림 서비스**
   - `notificationService`: 브라우저 푸시 알림 서비스
   - `useNotifications`: 실시간 알림 훅
   - WebSocket 연결을 통한 실시간 알림 수신

### ✅ 구현 완료된 부분

1. **사용자 설정 확인 로직** ✅

   - `NotificationService._check_notification_allowed()` 메서드 구현
   - 알림을 보내기 전에 사용자의 알림 설정을 확인
   - 사용자가 알림을 비활성화하면 알림이 전송되지 않음

2. **이메일 알림 전송** ✅

   - `NotificationService._send_email_notification()` 메서드 구현
   - 알림 생성 시 `notification_email` 설정을 확인하여 이메일 전송
   - 이메일 서비스와 통합 완료

3. **푸시 알림 전송** ✅

   - `NotificationService._send_push_notification()` 메서드 구현
   - 알림 생성 시 `notification_push` 설정을 확인하여 WebSocket으로 푸시 전송
   - 프론트엔드에서 WebSocket으로 받은 알림을 브라우저 푸시 알림으로 표시

4. **알림 타입별 설정 확인** ✅
   - `notification_session`: 세션 알림 전송 전 확인 ✅
   - `notification_achievement`: 업적 알림 전송 전 확인 ✅
   - `notification_message`: 메시지 알림 전송 전 확인 ✅
   - `friend_request`, `team_invitation`, `post_comment`, `post_like`: 메시지 설정 사용 ✅

## 이메일 서비스 통합 상태

### ✅ 통합 완료

1. **NotificationService에 EmailService 통합**

   - `NotificationService` 생성자에 `EmailService` 주입
   - `_send_email_notification()` 메서드로 이메일 전송 로직 구현
   - 사용자 설정(`notification_email`) 확인 후 이메일 전송

2. **이메일 전송 흐름**

   - 알림 생성 시 `_send_email_notification()` 자동 호출
   - 사용자 설정에서 `notification_email` 확인
   - 사용자 이메일 주소 조회 (`UserRepository`)
   - `EmailService._send_email()` 호출하여 이메일 전송

3. **SMTP 설정 확인**
   - ✅ SMTP_ENABLED: `true`
   - ✅ SMTP_HOST: `smtp.gmail.com`
   - ✅ SMTP_PORT: `587`
   - ✅ SMTP_USE_TLS: `true`
   - ✅ SMTP_USER: 설정됨
   - ✅ SMTP_PASSWORD: 설정됨
   - ⚠️ **주의**: Gmail의 경우 앱 비밀번호(Application-specific password)가 필요합니다

### ⚠️ Gmail 앱 비밀번호 설정 필요

현재 Gmail SMTP 연결 시 다음 오류가 발생합니다:

```
Application-specific password required
```

**해결 방법:**

1. Google 계정에서 2단계 인증 활성화
2. [앱 비밀번호 생성](https://myaccount.google.com/apppasswords)
3. 생성된 앱 비밀번호를 `.env` 파일의 `SMTP_PASSWORD`에 설정

또는 개발 환경에서는 SMTP를 비활성화하고 로그만 출력하도록 설정할 수 있습니다.

## 구현 상세

### 1. 알림 전송 전 사용자 설정 확인 로직

`NotificationService._check_notification_allowed()` 메서드:

- 사용자 설정을 조회 (`UserSettingsRepository`)
- 알림 타입에 따라 해당 설정 확인
- 설정이 활성화된 경우에만 알림 전송
- 설정이 없거나 오류 발생 시 기본적으로 알림 허용 (안전한 기본값)

### 2. 이메일 알림 통합

`NotificationService._send_email_notification()` 메서드:

- 알림 생성 시 `notification_email`이 `True`인 경우 이메일 전송
- 사용자 이메일 주소 조회 (`UserRepository`)
- `EmailService`를 사용하여 이메일 전송
- 오류 발생 시 로그만 기록하고 알림 생성은 계속 진행

### 3. 푸시 알림 통합

`NotificationService._send_push_notification()` 메서드:

- 알림 생성 시 `notification_push`가 `True`인 경우 WebSocket으로 푸시 전송
- `NotificationWebSocketManager`를 사용하여 실시간 알림 전송
- 프론트엔드 `useNotifications` 훅에서 WebSocket으로 받은 알림을 브라우저 푸시 알림으로 표시
- `notificationService.show()`를 사용하여 브라우저 푸시 알림 표시

### 4. 알림 타입별 필터링

타입 매핑:

- `session` → `notification_session` 확인
- `achievement` → `notification_achievement` 확인
- `message`, `friend_request`, `team_invitation`, `post_comment`, `post_like` → `notification_message` 확인
- 기타 타입 (system 등) → 기본적으로 허용

## 사용 방법

### 백엔드에서 알림 생성

```python
from app.domain.notification.schemas import NotificationCreate
from app.domain.notification.service import NotificationService

# NotificationService는 의존성 주입으로 자동 설정됨
notification = await service.create_notification(
    NotificationCreate(
        user_id="user_id",
        type="achievement",  # 또는 "session", "message" 등
        title="업적 달성!",
        message="새로운 업적을 달성했습니다.",
        data={"achievement_id": "..."}
    )
)

# notification이 None이면 사용자 설정에 의해 차단됨
```

### 프론트엔드에서 알림 수신

`useNotifications` 훅이 자동으로:

1. WebSocket 연결 유지
2. 알림 수신 시 브라우저 푸시 알림 표시
3. Toast 알림 표시
4. 알림 목록에 추가
