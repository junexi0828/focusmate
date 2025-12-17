#!/bin/bash
# 전체 시스템 연동 테스트 (Backend-Frontend-DB)

echo "🔍 Focus Mate 전체 시스템 연동 테스트"
echo "========================================"
echo ""

BASE_URL="http://localhost:8000/api/v1"
TOKEN=""

# 색상 코드
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 테스트 결과 카운터
PASSED=0
FAILED=0

# 테스트 함수
test_endpoint() {
    local name=$1
    local method=$2
    local endpoint=$3
    local data=$4
    local expected_status=$5

    echo -n "Testing: $name ... "

    if [ "$method" = "GET" ]; then
        if [ -z "$TOKEN" ]; then
            response=$(curl -s -w "\n%{http_code}" "$BASE_URL$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" -H "Authorization: Bearer $TOKEN" "$BASE_URL$endpoint")
        fi
    elif [ "$method" = "POST" ]; then
        if [ -z "$TOKEN" ]; then
            response=$(curl -s -w "\n%{http_code}" -X POST -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint")
        else
            response=$(curl -s -w "\n%{http_code}" -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d "$data" "$BASE_URL$endpoint")
        fi
    fi

    status_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$status_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $status_code)"
        PASSED=$((PASSED + 1))
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status_code)"
        echo "Response: $body"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo "1️⃣ 인증 시스템 테스트"
echo "-------------------"

# 로그인
echo "로그인 테스트..."
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d '{"email":"junexi@naver.com","password":"admin123"}')

if echo "$LOGIN_RESPONSE" | jq -e '.access_token' > /dev/null 2>&1; then
    TOKEN=$(echo "$LOGIN_RESPONSE" | jq -r '.access_token')
    echo -e "${GREEN}✅ 로그인 성공${NC}"
    echo "Token: ${TOKEN:0:20}..."
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ 로그인 실패${NC}"
    echo "Response: $LOGIN_RESPONSE"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "2️⃣ 방 관리 시스템 테스트"
echo "-------------------"

# 내 방 목록 조회
test_endpoint "내 방 목록 조회" "GET" "/rooms/my" "" "200"

# 방 생성
ROOM_DATA='{"name":"테스트방","work_duration":1500,"break_duration":300,"auto_start_break":false}'
ROOM_RESPONSE=$(curl -s -X POST "$BASE_URL/rooms" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$ROOM_DATA")

if echo "$ROOM_RESPONSE" | jq -e '.data.id' > /dev/null 2>&1; then
    ROOM_ID=$(echo "$ROOM_RESPONSE" | jq -r '.data.id')
    echo -e "방 생성: ${GREEN}✅ PASS${NC}"
    echo "Room ID: $ROOM_ID"
    PASSED=$((PASSED + 1))
else
    echo -e "방 생성: ${RED}❌ FAIL${NC}"
    FAILED=$((FAILED + 1))
fi
echo ""

echo "3️⃣ 채팅 시스템 테스트"
echo "-------------------"

# 채팅방 목록 조회
test_endpoint "채팅방 목록 조회" "GET" "/chats/rooms?room_type=direct" "" "200"
echo ""

echo "4️⃣ 예약 시스템 테스트"
echo "-------------------"

# 예약 목록 조회
test_endpoint "예약 목록 조회" "GET" "/room-reservations" "" "200"

# 다가오는 예약 조회
test_endpoint "다가오는 예약 조회" "GET" "/room-reservations/upcoming" "" "200"
echo ""

echo "5️⃣ 통계 시스템 테스트"
echo "-------------------"

# 사용자 통계 조회
USER_ID=$(echo "$LOGIN_RESPONSE" | jq -r '.user.id')
test_endpoint "사용자 통계 조회" "GET" "/stats/user/$USER_ID?days=7" "" "200"
echo ""

echo "6️⃣ 랭킹 시스템 테스트"
echo "-------------------"

# 팀 목록 조회
test_endpoint "팀 목록 조회" "GET" "/ranking/teams" "" "200"

# 리더보드 조회
test_endpoint "리더보드 조회" "GET" "/ranking/leaderboard?period=weekly" "" "200"
echo ""

echo "========================================"
echo "📊 테스트 결과 요약"
echo "========================================"
echo -e "${GREEN}✅ 통과: $PASSED${NC}"
echo -e "${RED}❌ 실패: $FAILED${NC}"
echo "총 테스트: $((PASSED + FAILED))"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 모든 테스트 통과!${NC}"
    exit 0
else
    echo -e "${YELLOW}⚠️  일부 테스트 실패${NC}"
    exit 1
fi
