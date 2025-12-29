#!/bin/bash

# Cloudflare Tunnel을 시스템 서비스로 설치하는 스크립트
# 사용법: ./scripts/install-cloudflare-service.sh
# 주의: sudo 권한이 필요합니다

set -e

# Tunnel 토큰
TUNNEL_TOKEN="eyJhIjoiZWQyNzU0OGI3ZjNlNTUxY2Y0ZjliM2M4YmFmMzk0MmUiLCJ0IjoiMDI0MWY0MTMtMDBmNS00NmY2LWE3MDUtZjU1ZGI1MjdjYjc4IiwicyI6IlltTTFaVFEwWm1VdFlXSmpZUzAwTldJeExUaG1ZMlF0TnpCbVptWTRNVFJrTkRRNSJ9"

# root 권한 확인
if [ "$EUID" -ne 0 ]; then
    echo "❌ 이 스크립트는 sudo 권한이 필요합니다."
    echo "   실행: sudo ./scripts/install-cloudflare-service.sh"
    exit 1
fi

# cloudflared 확인
if ! command -v cloudflared &> /dev/null; then
    echo "❌ cloudflared가 설치되어 있지 않습니다."
    echo "   설치: brew install cloudflare/cloudflare/cloudflared"
    exit 1
fi

echo "🔧 Cloudflare Tunnel 서비스 설치 중..."
echo ""

# 서비스 설치
cloudflared service install "$TUNNEL_TOKEN"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 서비스가 설치되었습니다."
    echo ""
    echo "📋 서비스 관리 명령어:"
    echo "   시작: sudo launchctl load /Library/LaunchDaemons/com.cloudflare.cloudflared.plist"
    echo "   중지: sudo launchctl unload /Library/LaunchDaemons/com.cloudflare.cloudflared.plist"
    echo "   상태: sudo launchctl list | grep cloudflared"
    echo "   로그: tail -f /usr/local/etc/cloudflared/*.log"
    echo ""
    echo "💡 서비스는 시스템 부팅 시 자동으로 시작됩니다."
else
    echo "❌ 서비스 설치 실패"
    exit 1
fi

