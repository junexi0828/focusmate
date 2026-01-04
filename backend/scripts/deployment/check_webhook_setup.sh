#!/bin/bash
# GitHub Webhook 설정 확인 스크립트

echo "=" * 60
echo "GitHub Webhook 설정 확인"
echo "=" * 60
echo ""

PROJECT_DIR="/volume1/web/focusmate-backend"

# 1. Webhook listener 스크립트 확인
echo "1️⃣ Webhook listener 스크립트 확인..."
if [ -f "$PROJECT_DIR/scripts/deployment/github-webhook-listener.py" ]; then
    echo "   ✅ github-webhook-listener.py 존재"
else
    echo "   ❌ github-webhook-listener.py 없음"
fi

if [ -f "$PROJECT_DIR/scripts/deployment/start-webhook-listener.sh" ]; then
    echo "   ✅ start-webhook-listener.sh 존재"
else
    echo "   ❌ start-webhook-listener.sh 없음"
fi
echo ""

# 2. Webhook listener 실행 상태 확인
echo "2️⃣ Webhook listener 실행 상태 확인..."
WEBHOOK_PID_FILE="$PROJECT_DIR/webhook-listener.pid"
if [ -f "$WEBHOOK_PID_FILE" ]; then
    WEBHOOK_PID=$(cat "$WEBHOOK_PID_FILE" 2>/dev/null || echo "")
    if [ -n "$WEBHOOK_PID" ] && ps -p "$WEBHOOK_PID" > /dev/null 2>&1; then
        echo "   ✅ Webhook listener 실행 중 (PID: $WEBHOOK_PID)"
    else
        echo "   ⚠️  PID 파일은 있지만 프로세스가 실행 중이지 않음"
    fi
else
    echo "   ⚠️  Webhook listener가 실행 중이지 않음"
fi

# 포트 확인
if netstat -tuln 2>/dev/null | grep -q ":9000"; then
    echo "   ✅ 포트 9000에서 리스닝 중"
else
    echo "   ⚠️  포트 9000에서 리스닝하지 않음"
fi
echo ""

# 3. Webhook secret 확인
echo "3️⃣ Webhook secret 확인..."
if [ -f "$PROJECT_DIR/.env" ]; then
    if grep -q "^GITHUB_WEBHOOK_SECRET=" "$PROJECT_DIR/.env"; then
        echo "   ✅ GITHUB_WEBHOOK_SECRET 설정됨"
    else
        echo "   ⚠️  GITHUB_WEBHOOK_SECRET이 .env에 없음"
        echo "      .env 파일에 추가하세요: GITHUB_WEBHOOK_SECRET=your-secret"
    fi
else
    echo "   ⚠️  .env 파일이 없음"
fi
echo ""

# 4. Cloudflare Tunnel 확인
echo "4️⃣ Cloudflare Tunnel 확인..."
TUNNEL_DIR="/volume1/web/cloudflare-tunnel"
TUNNEL_PID_FILE="$TUNNEL_DIR/tunnel.pid"
if [ -f "$TUNNEL_PID_FILE" ]; then
    TUNNEL_PID=$(cat "$TUNNEL_PID_FILE" 2>/dev/null || echo "")
    if [ -n "$TUNNEL_PID" ] && ps -p "$TUNNEL_PID" > /dev/null 2>&1; then
        echo "   ✅ Cloudflare Tunnel 실행 중 (PID: $TUNNEL_PID)"
        echo "   💡 Tunnel의 Public Hostname에 /webhook 경로가 추가되어 있는지 확인하세요"
    else
        echo "   ⚠️  Cloudflare Tunnel이 실행 중이지 않음"
    fi
else
    echo "   ⚠️  Cloudflare Tunnel이 실행 중이지 않음"
fi
echo ""

# 5. Git 저장소 확인
echo "5️⃣ Git 저장소 확인..."
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "   ✅ Git 저장소 존재"
    REMOTE_URL=$(cd "$PROJECT_DIR" && git remote get-url origin 2>/dev/null || echo "")
    if [ -n "$REMOTE_URL" ]; then
        echo "   ✅ Remote URL: $REMOTE_URL"
    else
        echo "   ⚠️  Remote URL이 설정되지 않음"
    fi
else
    echo "   ⚠️  Git 저장소가 없음 (git clone 필요)"
fi
echo ""

echo "=" * 60
echo "설정 요약"
echo "=" * 60
echo ""
echo "✅ 완료된 설정:"
echo "   - Webhook listener 스크립트 생성"
echo "   - start-nas.sh에 webhook listener 자동 시작 추가"
echo "   - stop-nas.sh에 webhook listener 중지 추가"
echo ""
echo "📋 다음 단계:"
echo "   1. NAS에서 webhook listener 시작:"
echo "      cd /volume1/web/focusmate-backend"
echo "      ./scripts/deployment/start-webhook-listener.sh"
echo ""
echo "   2. .env 파일에 GITHUB_WEBHOOK_SECRET 추가"
echo ""
echo "   3. Cloudflare Tunnel에 /webhook 경로 추가"
echo ""
echo "   4. GitHub 저장소에 webhook 추가:"
echo "      Settings → Webhooks → Add webhook"
echo "      Payload URL: https://your-tunnel-url/webhook"
echo "      Secret: .env의 GITHUB_WEBHOOK_SECRET 값"
echo "      Events: Just the push event"
echo ""

