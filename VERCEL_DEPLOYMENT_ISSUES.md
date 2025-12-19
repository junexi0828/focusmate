# Vercel 도메인 연결 후 발생한 문제 및 해결 방법

## 문제 요약

Vercel에 `https://eieconcierge.com` 도메인을 연결한 후 다음과 같은 에러들이 발생했습니다:

### 1. 401 Unauthorized 에러
- `/api/v1/notifications/unread-count`
- `/api/v1/chats/unread-count`

### 2. 500 Internal Server Error
- `/api/v1/stats/goals` (CORS 에러도 함께 발생)
- `/api/v1/matching/stats/comprehensive`

### 3. React 경고
- `Function components cannot be given refs` (DialogOverlay)
- Input autocomplete warning

## 근본 원인

### 1. 환경 변수 미설정
- Vercel 프론트엔드가 잘못된 API URL을 사용하고 있을 가능성
- 백엔드 URL이 로컬호스트로 설정되어 프로덕션에서 접근 불가

### 2. 백엔드 CORS 설정
- 백엔드가 새 도메인 요청을 허용하지 않음 (설정은 되어있으나 서버 재시작 필요)

### 3. 데이터베이스 쿼리 오류
- `stats/goals` 엔드포인트에서 비동기 쿼리 오류

## 해결 방법

### 1단계: Vercel 환경 변수 설정

Vercel 대시보드에서 다음 환경 변수를 설정하세요:

```bash
# Frontend 환경 변수 (Vercel에서 설정)
VITE_API_BASE_URL=https://your-backend-url.com/api/v1
VITE_WS_BASE_URL=wss://your-backend-url.com
```

**주의**: 백엔드 서버의 실제 URL로 교체해야 합니다.

#### Vercel 환경 변수 설정 방법:
1. Vercel 대시보드 → 프로젝트 선택
2. Settings → Environment Variables
3. 위 변수들을 추가
4. Deployments → Redeploy (재배포)

### 2단계: 백엔드 서버 재시작

백엔드 `.env` 파일에 CORS 설정이 이미 추가되어 있습니다:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080,https://eieconcierge.com,https://www.eieconcierge.com
```

백엔드 서버를 재시작하여 새 CORS 설정을 적용하세요:

```bash
cd backend
# 현재 실행 중인 서버 종료 (Ctrl+C)

# 서버 재시작
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3단계: 데이터베이스 쿼리 오류 수정

`backend/app/api/v1/endpoints/stats.py` 파일의 비동기 쿼리 문제가 이미 수정되었습니다.

변경사항을 커밋하고 백엔드를 다시 배포하세요:

```bash
git add .
git commit -m "fix: Fix database query errors in stats endpoints"
git push
```

### 4단계: 백엔드 배포 확인

백엔드가 어디에 배포되어 있는지 확인하세요:

#### 옵션 A: 백엔드도 Vercel에 배포
만약 백엔드도 Vercel에 배포하려면:

1. `vercel.json` 파일 생성:
```json
{
  "version": 2,
  "builds": [
    {
      "src": "backend/app/main.py",
      "use": "@vercel/python"
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "backend/app/main.py"
    }
  ],
  "env": {
    "DATABASE_URL": "@database_url",
    "SECRET_KEY": "@secret_key",
    "CORS_ORIGINS": "https://eieconcierge.com,https://www.eieconcierge.com"
  }
}
```

2. Vercel에 환경 변수 추가 (Secret):
```bash
vercel env add DATABASE_URL
vercel env add SECRET_KEY
```

#### 옵션 B: 백엔드를 다른 플랫폼에 배포
백엔드를 Railway, Render, AWS, GCP 등에 배포하고 URL을 Vercel 환경 변수에 설정하세요.

### 5단계: 프론트엔드 환경 변수 확인

`frontend/.env` 파일 확인:
```bash
# 로컬 개발용
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_WS_BASE_URL=ws://localhost:8000
```

**Vercel에서는 별도로 설정해야 합니다** (1단계 참조)

## 테스트 방법

### 1. 로컬 환경 테스트
```bash
# 터미널 1: 백엔드 실행
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 터미널 2: 프론트엔드 실행
cd frontend
npm run dev
```

브라우저에서 `http://localhost:3000` 접속하여 에러가 없는지 확인

### 2. 프로덕션 환경 테스트
1. Vercel에 재배포 후 `https://eieconcierge.com` 접속
2. 브라우저 개발자 도구 (F12) → Console 탭에서 에러 확인
3. Network 탭에서 API 요청이 올바른 URL로 가는지 확인

## 추가 확인 사항

### 백엔드 URL 찾기
백엔드가 어디에 배포되어 있는지 확인:
```bash
# 로컬에서 실행 중이라면
curl http://localhost:8000/health

# 응답:
# {"status":"healthy","service":"Focus Mate","version":"1.0.0","environment":"development"}
```

### Vercel 로그 확인
```bash
vercel logs
```

## 현재 변경사항 커밋

변경사항을 커밋하고 푸시하세요:

```bash
# 변경사항 확인
git status

# 모든 변경사항 추가
git add .

# 커밋
git commit -m "fix: Fix CORS, database queries, and WebSocket errors

- Fix 422 error on leaderboard endpoint (incorrect DB dependency)
- Fix ReferenceError in useChatWebSocket (duration variable)
- Fix missing key prop warning in Profile page
- Update CORS configuration for eieconcierge.com domain
- Fix async database queries in stats endpoints"

# 푸시
git push origin main
```

## 예상되는 추가 문제 및 해결

### 1. 여전히 CORS 에러가 발생하는 경우
백엔드 서버가 재시작되었는지 확인하고, 백엔드 로그를 확인하세요:
```bash
# 백엔드 로그에서 CORS 설정 확인
# 서버 시작 시 다음과 같은 로그가 보여야 합니다:
# INFO:     Started server process
# CORS origins: ['http://localhost:3000', ..., 'https://eieconcierge.com']
```

### 2. 401 에러가 계속 발생하는 경우
- 로그인이 제대로 되어 있는지 확인
- JWT 토큰이 제대로 저장되어 있는지 확인 (브라우저 개발자 도구 → Application → Local Storage)
- 토큰 만료 시간 확인 (`ACCESS_TOKEN_EXPIRE_MINUTES=30`)

### 3. 500 에러가 계속 발생하는 경우
백엔드 로그를 확인하여 정확한 에러 메시지를 확인하세요:
```bash
cd backend
tail -f logs/app.log  # 로그 파일이 있다면
# 또는 서버를 직접 실행하여 콘솔에서 에러 확인
```

## 문의사항

추가 도움이 필요하면 다음 정보를 제공해주세요:
1. 백엔드가 어디에 배포되어 있는지 (로컬/Vercel/Railway/기타)
2. Vercel 환경 변수 설정 스크린샷
3. 브라우저 콘솔의 전체 에러 메시지
4. 백엔드 서버 로그
