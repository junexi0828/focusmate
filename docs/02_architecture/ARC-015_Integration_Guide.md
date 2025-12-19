# FocusMate 통합 가이드

## 개요
백엔드 API와 프론트엔드가 완전히 연동된 FocusMate 애플리케이션입니다.

## 구현된 기능

### 1. 커뮤니티 기능 ✅
- **게시글 목록 표시**: `/community`
- **게시글 상세보기**: `/community/$postId`
- **게시글 작성**: CreatePostDialog 컴포넌트
- **댓글 작성 및 답글**: 상세보기 페이지 내 댓글 시스템
- **좋아요 기능**: 게시글 및 댓글 좋아요

**백엔드 API**:
- `GET /api/v1/community/posts` - 게시글 목록
- `POST /api/v1/community/posts` - 게시글 작성
- `GET /api/v1/community/posts/{post_id}` - 게시글 상세
- `POST /api/v1/community/posts/{post_id}/comments` - 댓글 작성
- `POST /api/v1/community/posts/{post_id}/like` - 게시글 좋아요

### 2. 메시지 시스템 ✅
- **채팅 목록**: `/messages`
- **1:1 대화**: Direct 채팅 탭
- **팀 채팅**: Team 채팅 탭
- **실시간 메시지**: WebSocket 연동
- **파일 첨부**: 이미지 및 파일 공유

**백엔드 API**:
- `GET /api/v1/chat/rooms` - 채팅방 목록
- `POST /api/v1/chat/rooms/direct` - 1:1 채팅방 생성
- `POST /api/v1/chat/rooms/{room_id}/messages` - 메시지 전송
- `GET /api/v1/messages/conversations` - 대화 목록 (추가)
- `POST /api/v1/messages/send` - 메시지 전송 (추가)

### 3. 친구 관리 시스템 ✅ (새로 구현)
- **친구 목록**: `/friends` - 친구 탭
- **친구 추가**: 사용자 ID로 친구 요청
- **받은 요청**: 받은 친구 요청 탭
- **보낸 요청**: 보낸 친구 요청 탭
- **친구 수락/거절**: 요청 관리
- **친구 삭제**: 친구 목록에서 삭제

**백엔드 API** (새로 추가):
- `POST /api/v1/friends/requests` - 친구 요청 보내기
- `GET /api/v1/friends/requests/received` - 받은 요청 목록
- `GET /api/v1/friends/requests/sent` - 보낸 요청 목록
- `POST /api/v1/friends/requests/{request_id}/accept` - 요청 수락
- `POST /api/v1/friends/requests/{request_id}/reject` - 요청 거절
- `GET /api/v1/friends/` - 친구 목록
- `DELETE /api/v1/friends/{friend_id}` - 친구 삭제

### 4. 팀 관리 시스템 ✅
- **팀 생성**: `/ranking`
- **팀 목록**: 랭킹 페이지
- **멤버 초대**: 이메일로 초대
- **초대 수락**: 초대 링크 또는 알림
- **팀 탈퇴**: 팀에서 나가기

**백엔드 API**:
- `POST /api/v1/ranking/teams` - 팀 생성
- `POST /api/v1/ranking/teams/{team_id}/invite` - 멤버 초대
- `POST /api/v1/ranking/teams/invitations/{invitation_id}/accept` - 초대 수락
- `POST /api/v1/ranking/teams/{team_id}/leave` - 팀 탈퇴

### 5. 알림 시스템 ✅
- **알림 목록**: 헤더 NotificationBell 컴포넌트
- **실시간 알림**: WebSocket 연동으로 실시간 수신
- **알림 클릭 시 페이지 이동**: 라우팅 메타데이터 기반
- **읽음 처리**: 개별 또는 전체 읽음 처리

**백엔드 API**:
- `GET /api/v1/notifications/` - 알림 목록
- `POST /api/v1/notifications/mark-read` - 읽음 처리
- `GET /api/v1/notifications/unread-count` - 읽지 않은 알림 수
- `WS /api/v1/notifications/ws` - 실시간 알림 WebSocket

## 시작하기

### 백엔드 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 데이터베이스 마이그레이션 실행
alembic upgrade head

# 서버 실행
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 프론트엔드 실행

```bash
cd frontend
npm install

# 개발 서버 실행
npm run dev
```

## 환경 변수 설정

### 백엔드 (.env)
```
DATABASE_URL=postgresql://user:password@localhost:5432/focusmate
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 프론트엔드 (.env)
```
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000
```

## 데이터베이스 마이그레이션

친구 기능을 위한 새로운 테이블이 추가되었습니다:

```bash
cd backend
alembic revision --autogenerate -m "Add friend tables"
alembic upgrade head
```

또는 제공된 마이그레이션 파일 사용:

```bash
alembic upgrade head
```

## API 엔드포인트 전체 목록

### 인증 (Auth)
- `POST /api/v1/auth/register` - 회원가입
- `POST /api/v1/auth/login` - 로그인
- `POST /api/v1/auth/logout` - 로그아웃

### 커뮤니티 (Community)
- `GET /api/v1/community/posts` - 게시글 목록
- `POST /api/v1/community/posts` - 게시글 작성
- `GET /api/v1/community/posts/{post_id}` - 게시글 상세
- `PUT /api/v1/community/posts/{post_id}` - 게시글 수정
- `DELETE /api/v1/community/posts/{post_id}` - 게시글 삭제
- `POST /api/v1/community/posts/{post_id}/like` - 좋아요
- `POST /api/v1/community/posts/{post_id}/comments` - 댓글 작성
- `GET /api/v1/community/posts/{post_id}/comments` - 댓글 목록

### 친구 (Friends) - 새로 추가
- `POST /api/v1/friends/requests` - 친구 요청
- `GET /api/v1/friends/requests/received` - 받은 요청
- `GET /api/v1/friends/requests/sent` - 보낸 요청
- `POST /api/v1/friends/requests/{id}/accept` - 수락
- `POST /api/v1/friends/requests/{id}/reject` - 거절
- `DELETE /api/v1/friends/requests/{id}` - 취소
- `GET /api/v1/friends/` - 친구 목록
- `DELETE /api/v1/friends/{friend_id}` - 친구 삭제

### 메시지 (Messages)
- `POST /api/v1/messages/send` - 메시지 전송
- `GET /api/v1/messages/conversations` - 대화 목록
- `GET /api/v1/messages/conversations/{id}` - 대화 상세
- `POST /api/v1/messages/conversations/{id}/read` - 읽음 처리

### 채팅 (Chat)
- `GET /api/v1/chat/rooms` - 채팅방 목록
- `POST /api/v1/chat/rooms/direct` - 1:1 채팅방 생성
- `POST /api/v1/chat/rooms/team` - 팀 채팅방 생성
- `GET /api/v1/chat/rooms/{id}/messages` - 메시지 목록
- `POST /api/v1/chat/rooms/{id}/messages` - 메시지 전송
- `WS /api/v1/chat/ws/{room_id}` - WebSocket 연결

### 알림 (Notifications) - 개선
- `GET /api/v1/notifications/` - 알림 목록
- `POST /api/v1/notifications/mark-read` - 읽음 처리
- `POST /api/v1/notifications/mark-all-read` - 전체 읽음
- `GET /api/v1/notifications/unread-count` - 읽지 않은 수
- `WS /api/v1/notifications/ws` - 실시간 WebSocket

### 랭킹/팀 (Ranking)
- `POST /api/v1/ranking/teams` - 팀 생성
- `GET /api/v1/ranking/teams` - 팀 목록
- `POST /api/v1/ranking/teams/{id}/invite` - 초대
- `POST /api/v1/ranking/teams/invitations/{id}/accept` - 수락
- `POST /api/v1/ranking/teams/{id}/leave` - 탈퇴

## 주요 변경사항

### 백엔드
1. ✅ Friend 모델 및 FriendRequest 모델 추가
2. ✅ 친구 관리 API 엔드포인트 전체 구현
3. ✅ WebSocket 실시간 알림 구현
4. ✅ 알림 라우팅 메타데이터 헬퍼 함수
5. ✅ NotificationWebSocketManager 추가

### 프론트엔드
1. ✅ 친구 페이지 (`/friends`) 추가
2. ✅ 친구 서비스 (`friendService.ts`) 구현
3. ✅ 메시지 서비스 (`messagingService.ts`) 구현
4. ✅ 실시간 알림 훅 (`useNotifications.ts`) 추가
5. ✅ NotificationBell WebSocket 연동
6. ✅ Sidebar에 친구 메뉴 추가
7. ✅ API 타입 정의 (`types/api.ts`) 추가

## 테스트 방법

### 1. 친구 기능 테스트
1. 두 개의 계정으로 로그인
2. 한 계정에서 `/friends` 페이지로 이동
3. "친구 추가" 버튼 클릭 후 다른 사용자 ID 입력
4. 다른 계정에서 "받은 요청" 탭 확인
5. 요청 수락/거절 테스트

### 2. 실시간 알림 테스트
1. 로그인 후 헤더의 알림 벨 확인
2. 다른 사용자가 친구 요청/메시지 전송
3. 실시간으로 알림 수신 확인 (초록색 점은 WebSocket 연결 상태)
4. 알림 클릭 시 해당 페이지로 이동 확인

### 3. 메시지 기능 테스트
1. `/messages` 페이지로 이동
2. Direct/Team/Matching 탭 전환
3. 메시지 전송 및 실시간 수신 확인
4. 파일 첨부 기능 테스트

## 트러블슈팅

### WebSocket 연결 실패
- 백엔드가 실행 중인지 확인
- `.env` 파일의 `VITE_WS_BASE_URL` 확인
- 브라우저 콘솔에서 WebSocket 연결 로그 확인

### API 호출 실패
- 백엔드 URL이 올바른지 확인
- CORS 설정 확인
- 인증 토큰이 유효한지 확인

### 데이터베이스 오류
- 마이그레이션이 최신인지 확인: `alembic upgrade head`
- PostgreSQL이 실행 중인지 확인
- 데이터베이스 연결 정보가 올바른지 확인

## 추가 개선 사항
- [ ] 친구 온라인 상태 실시간 업데이트
- [ ] 메시지 검색 기능
- [ ] 알림 필터링 및 카테고리
- [ ] 친구 추천 시스템
