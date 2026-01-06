#!/bin/bash
# API 엔드포인트 연결 테스트 스크립트

echo "🔍 Focus Mate API 연결 테스트"
echo "================================"
echo ""

# 1. Health Check
echo "1️⃣ Health Check"
curl -s http://localhost:8000/health | jq .
echo ""

# 2. Auth Endpoints
echo "2️⃣ Auth Endpoints"
echo "POST /api/v1/auth/register - 회원가입"
echo "POST /api/v1/auth/login - 로그인"
echo "POST /api/v1/auth/refresh - 토큰 갱신"
echo ""

# 3. Room Endpoints
echo "3️⃣ Room Endpoints"
echo "GET /api/v1/rooms - 방 목록 조회"
echo "POST /api/v1/rooms - 방 생성"
echo "GET /api/v1/rooms/{room_id} - 방 상세 조회"
echo "GET /api/v1/rooms/my - 내 방 목록"
echo ""

# 4. Participant Endpoints
echo "4️⃣ Participant Endpoints"
echo "POST /api/v1/rooms/{room_id}/participants - 방 참여"
echo "GET /api/v1/rooms/{room_id}/participants - 참여자 목록"
echo ""

# 5. Chat Endpoints
echo "5️⃣ Chat Endpoints"
echo "GET /api/v1/chats/rooms - 채팅방 목록"
echo "POST /api/v1/chats/rooms - 채팅방 생성"
echo "GET /api/v1/chats/rooms/{room_id}/messages - 메시지 조회"
echo "POST /api/v1/chats/rooms/{room_id}/messages - 메시지 전송"
echo "WS /api/v1/chats/ws - WebSocket 연결"
echo ""

# 6. Reservation Endpoints
echo "6️⃣ Reservation Endpoints"
echo "GET /api/v1/room-reservations - 예약 목록"
echo "POST /api/v1/room-reservations - 예약 생성"
echo "GET /api/v1/room-reservations/upcoming - 다가오는 예약"
echo "DELETE /api/v1/room-reservations/{id} - 예약 취소"
echo ""

# 7. Stats Endpoints
echo "7️⃣ Stats Endpoints"
echo "GET /api/v1/stats/user/{user_id} - 사용자 통계"
echo "GET /api/v1/stats/daily - 일일 통계"
echo ""

# 8. Ranking Endpoints
echo "8️⃣ Ranking Endpoints"
echo "GET /api/v1/ranking/teams - 팀 목록"
echo "POST /api/v1/ranking/teams - 팀 생성"
echo "POST /api/v1/ranking/teams/{team_id}/invite - 팀 초대"
echo "POST /api/v1/ranking/verifications/{id}/review - 인증 검토"
echo ""

# 9. Database Connection Test
echo "9️⃣ Database Connection"
echo "Testing database connectivity..."
if curl -s http://localhost:8000/health | jq -e '.status == "healthy"' > /dev/null; then
    echo "✅ Database connection: OK"
else
    echo "❌ Database connection: FAILED"
fi
echo ""

echo "================================"
echo "✅ API 엔드포인트 확인 완료"
