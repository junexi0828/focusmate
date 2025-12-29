# CORS 문제 해결 가이드

CORS 에러 발생 시 단계별 진단 및 해결 방법입니다.

## 문제 원인

브라우저에서 다음과 같은 CORS 에러 발생:

```
Access to XMLHttpRequest at 'https://api.eieconcierge.com/api/v1/auth/login'
from origin 'https://eieconcierge.com' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

주요 원인:

1. 백엔드가 요청에 응답하지 않음 (타임아웃)
2. 백엔드가 응답하지 않아 CORS 헤더가 전달되지 않음
3. Cloudflare Tunnel은 실행 중이지만 백엔드 연결 문제

## 해결 단계

### 1단계: 백엔드 상태 확인

```bash
# 백엔드 프로세스 확인
ps aux | grep uvicorn | grep -v grep

# 포트 8000 사용 확인
lsof -ti:8000

# 로컬 백엔드 Health Check
curl http://localhost:8000/health
```

**예상 결과**: `{"status":"healthy",...}` JSON 응답

### 2단계: 백엔드 재시작 (필요시)

```bash
cd /Users/juns/code/personal/notion/juns_workspace/FocusMate/backend

# 기존 프로세스 종료
pkill -f "uvicorn app.main:app"

# 가상환경 활성화 및 백엔드 시작
source venv/bin/activate
nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/focusmate-backend.log 2>&1 &

# 5초 대기 후 확인
sleep 5
curl http://localhost:8000/health
```

### 3단계: CORS 설정 확인

```bash
# CORS_ORIGINS 확인
grep "^CORS_ORIGINS" backend/.env
```

**확인 사항**: 다음이 포함되어 있어야 함

```
CORS_ORIGINS=...,https://eieconcierge.com,https://www.eieconcierge.com
```

### 4단계: 로컬 CORS 테스트

```bash
# OPTIONS 요청 (Preflight) 테스트
curl -X OPTIONS \
  -H "Origin: https://eieconcierge.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type,authorization" \
  -v http://localhost:8000/api/v1/auth/login 2>&1 | grep -i "access-control"
```

**예상 결과**: 다음 헤더가 포함되어야 함

```
< access-control-allow-origin: https://eieconcierge.com
< access-control-allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
< access-control-allow-credentials: true
```

### 5단계: Cloudflare Tunnel 재시작

```bash
cd /Users/juns/code/personal/notion/juns_workspace/FocusMate

# Tunnel 중지
./scripts/stop-cloudflare-tunnel.sh

# 2초 대기
sleep 2

# Tunnel 시작
./scripts/start-cloudflare-tunnel.sh

# 3초 대기 후 확인
sleep 3
curl https://api.eieconcierge.com/health
```

### 6단계: Tunnel을 통한 CORS 테스트

```bash
# OPTIONS 요청 테스트
curl -X OPTIONS \
  -H "Origin: https://eieconcierge.com" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: content-type,authorization" \
  -I https://api.eieconcierge.com/api/v1/auth/login 2>&1 | grep -i "access-control\|HTTP/"
```

**예상 결과**:

```
HTTP/2 200
access-control-allow-origin: https://eieconcierge.com
access-control-allow-methods: GET, POST, PUT, PATCH, DELETE, OPTIONS
access-control-allow-credentials: true
```

## 빠른 해결 스크립트

```bash
#!/bin/bash
cd /Users/juns/code/personal/notion/juns_workspace/FocusMate

echo "=== 1. 백엔드 재시작 ==="
pkill -f "uvicorn app.main:app"
cd backend
source venv/bin/activate
nohup python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/focusmate-backend.log 2>&1 &
sleep 5
echo "✅ 백엔드 시작됨"

echo ""
echo "=== 2. 백엔드 Health Check ==="
curl -s http://localhost:8000/health | head -1

echo ""
echo "=== 3. 로컬 CORS 테스트 ==="
curl -s -X OPTIONS \
  -H "Origin: https://eieconcierge.com" \
  -H "Access-Control-Request-Method: POST" \
  -I http://localhost:8000/api/v1/auth/login 2>&1 | grep -i "access-control" | head -3

echo ""
echo "=== 4. Cloudflare Tunnel 재시작 ==="
./scripts/stop-cloudflare-tunnel.sh
sleep 2
./scripts/start-cloudflare-tunnel.sh
sleep 3

echo ""
echo "=== 5. Tunnel API 테스트 ==="
curl -s -o /dev/null -w "HTTP Status: %{http_code}\n" https://api.eieconcierge.com/health

echo ""
echo "=== 6. Tunnel CORS 테스트 ==="
curl -s -X OPTIONS \
  -H "Origin: https://eieconcierge.com" \
  -H "Access-Control-Request-Method: POST" \
  -I https://api.eieconcierge.com/api/v1/auth/login 2>&1 | grep -i "access-control\|HTTP/" | head -5
```

## 문제가 계속되면 확인할 사항

1. **백엔드 로그 확인**

   ```bash
   tail -50 /tmp/focusmate-backend.log
   ```

2. **Cloudflare Tunnel 로그 확인**

   ```bash
   tail -50 ~/.cloudflare-tunnel/tunnel.log
   ```

3. **포트 충돌 확인**

   ```bash
   lsof -ti:8000
   ```

4. **환경 변수 확인**
   ```bash
   cd backend
   source venv/bin/activate
   python -c "from app.core.config import settings; print('CORS_ORIGINS:', settings.CORS_ORIGINS)"
   ```

## 성공 확인

모든 단계가 성공하면:

- ✅ 로컬 백엔드: `http://localhost:8000/health` → 200 OK
- ✅ Tunnel API: `https://api.eieconcierge.com/health` → 200 OK
- ✅ CORS 헤더: `access-control-allow-origin: https://eieconcierge.com`
- ✅ 브라우저에서 로그인 시도 → CORS 에러 없음
