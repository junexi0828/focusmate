#!/bin/bash

# Cloudflare Tunnel 설정 및 실행 스크립트
# 사용법: ./scripts/cloudflare-tunnel-setup.sh

set -e

echo "🚀 Cloudflare Tunnel 설정 시작..."

# 1. Tunnel 이름 확인
TUNNEL_NAME="focusmate-backend"
BACKEND_URL="http://localhost:8000"

echo ""
echo "📋 설정 정보:"
echo "  - Tunnel 이름: $TUNNEL_NAME"
echo "  - 백엔드 URL: $BACKEND_URL"
echo ""

# 2. cloudflared 설치 확인
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared가 설치되어 있지 않습니다."
    echo "   설치 명령: brew install cloudflare/cloudflare/cloudflared"
    exit 1
fi

echo "✅ cloudflared 설치 확인됨: $(which cloudflared)"
echo "   버전: $(cloudflared --version | head -n 1)"
echo ""

# 3. Tunnel 생성 (이미 생성되어 있으면 스킵)
echo "🔍 Tunnel 상태 확인 중..."
if cloudflared tunnel list 2>/dev/null | grep -q "$TUNNEL_NAME"; then
    echo "✅ Tunnel '$TUNNEL_NAME'이 이미 존재합니다."
else
    echo "📝 Tunnel '$TUNNEL_NAME' 생성 중..."
    echo "   ⚠️  Zero Trust 대시보드에서 Tunnel을 먼저 생성해야 합니다."
    echo "   대시보드: https://one.dash.cloudflare.com/"
    echo "   경로: Networks → Tunnels → Create a tunnel"
    echo ""
    read -p "Tunnel을 대시보드에서 생성하셨나요? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Tunnel을 먼저 생성해주세요."
        exit 1
    fi
fi

# 4. Tunnel 실행 방법 안내
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📝 Tunnel 실행 방법:"
echo ""
echo "방법 1: 스크립트로 실행 (권장)"
echo "   ./scripts/start-cloudflare-tunnel.sh"
echo ""
echo "방법 2: 수동 실행 (임시 테스트용)"
echo "   cloudflared tunnel run --token [토큰]"
echo ""
echo "방법 3: 시스템 서비스로 설치 (자동 시작, 재부팅 후에도 실행)"
echo "   sudo cloudflared service install [토큰]"
echo "   sudo launchctl load /Library/LaunchDaemons/com.cloudflare.cloudflared.plist"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 5. 백엔드 서버 확인
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ 백엔드 서버가 실행 중입니다."
else
    echo "⚠️  백엔드 서버가 실행되지 않았습니다."
    echo "   백엔드를 먼저 실행해주세요:"
    echo "   cd backend && ./run.sh"
    echo ""
fi

echo ""
echo "✨ 설정 완료!"
echo ""

