# Vercel 배포 가이드 - 404 에러 해결

## 문제 원인

프론트엔드가 `https://eieconcierge.com`에 배포되어 있지만, 백엔드 API가 `http://localhost:8000`에서 실행 중이거나 다른 도메인에 있어서 404 에러가 발생합니다.

**에러 예시:**

- `GET https://eieconcierge.com/api/v1/chats/unread-count 404`
- `GET https://eieconcierge.com/api/v1/notifications/unread-count 404`
- `GET https://eieconcierge.com/api/v1/matching/proposals/my 404`

## ⚠️ 중요 사항

**Vercel은 localhost로 프록시할 수 없습니다!**

- Vercel의 rewrites는 공개적으로 접근 가능한 HTTPS URL로만 프록시 가능
- `localhost:8000`은 작동하지 않음
- 백엔드를 프로덕션 서버에 배포하거나 터널링 서비스 사용 필요

## 해결 방법

### 방법 1: Vercel 환경 변수 설정 (필수) ⭐

**Vercel 대시보드에서 환경 변수 추가:**

1. **Vercel 대시보드 접속**
   - https://vercel.com/dashboard
   - `focusmate` 프로젝트 선택

2. **Settings → Environment Variables** 클릭

3. **환경 변수 추가**

   ```
   Name: VITE_API_BASE_URL
   Value: https://your-backend-url.com/api/v1

   Environment:
   ✅ Production
   ✅ Preview
   ✅ Development
   ```

4. **저장 후 재배포**
   - Vercel 대시보드에서 "Redeploy" 클릭
   - 또는 `git push`로 자동 재배포

**참고:** Vercel의 시스템 환경 변수는 자동으로 제공되지만, 백엔드 URL은 수동으로 설정해야 합니다.
[Vercel 시스템 환경 변수 문서](https://vercel.com/docs/environment-variables/system-environment-variables)

#### 1단계: 백엔드 URL 확인

**백엔드가 프로덕션에 배포되어 있다면:**

- 백엔드 URL 확인 (예: `https://api.eieconcierge.com` 또는 Railway/Render URL)

**백엔드가 localhost에 있다면 (임시 테스트):**

```bash
# ngrok 설치 및 실행
ngrok http 8000
# 출력 예: https://xxxx-xx-xx-xx-xx.ngrok-free.app
```

#### 2단계: Vercel 환경 변수 설정

1. **Vercel 대시보드 접속**
   - https://vercel.com/dashboard
   - `focusmate` 프로젝트 선택

2. **Settings → Environment Variables**

3. **환경 변수 추가**

   ```
   Name: VITE_API_BASE_URL
   Value: https://your-backend-url.com/api/v1

   Environment:
   ✅ Production
   ✅ Preview
   ✅ Development
   ```

4. **저장 후 재배포**
   - Vercel 대시보드에서 "Redeploy" 클릭
   - 또는 `git push`로 자동 재배포

### 방법 2: 백엔드 프로덕션 배포 (권장)

#### 옵션 A: Railway (추천)

```bash
# Railway CLI 설치
npm i -g @railway/cli

# Railway에 로그인 및 배포
railway login
railway init
railway up
```

배포 후 URL 예: `https://your-app.railway.app`

```
VITE_API_BASE_URL=https://your-app.railway.app/api/v1
```

#### 옵션 B: Render

```bash
# Render 대시보드에서 새 Web Service 생성
# GitHub 저장소 연결 후 배포
```

배포 후 URL 예: `https://your-app.onrender.com`

```
VITE_API_BASE_URL=https://your-app.onrender.com/api/v1
```

#### 옵션 C: Fly.io

```bash
# Fly.io CLI 설치 및 배포
fly launch
fly deploy
```

배포 후 URL 예: `https://your-app.fly.dev`

```
VITE_API_BASE_URL=https://your-app.fly.dev/api/v1
```

## 현재 코드 동작 방식

`frontend/src/api/client.ts`는 다음 순서로 API URL을 결정합니다:

1. **`VITE_API_BASE_URL` 환경 변수** (최우선)
2. 프로덕션: `window.location.origin + /api/v1` (같은 도메인 가정)
3. 개발: `http://localhost:8000/api/v1`

## 즉시 해결 (임시 테스트)

**ngrok 사용:**

```bash
# 1. ngrok 설치 (macOS)
brew install ngrok

# 2. ngrok 실행
ngrok http 8000

# 3. 출력된 URL 복사
# 예: https://abc123.ngrok-free.app

# 4. Vercel 환경 변수 설정
VITE_API_BASE_URL=https://abc123.ngrok-free.app/api/v1

# 5. 재배포
```

⚠️ **주의:** ngrok 무료 버전은 URL이 재시작 시마다 변경됩니다.

## 확인 사항

배포 전 확인:

- ✅ 백엔드 CORS 설정에 `https://eieconcierge.com` 포함
  - 현재 설정: `CORS_ORIGINS=...,https://eieconcierge.com,...` ✅
- ✅ 백엔드가 HTTPS로 접근 가능
- ✅ Vercel 환경 변수가 모든 환경(Production, Preview, Development)에 설정됨
- ✅ 환경 변수 이름이 `VITE_`로 시작 (Vite 빌드 시 포함됨)

## 문제 해결 체크리스트

- [ ] Vercel 환경 변수 `VITE_API_BASE_URL` 설정됨
- [ ] 환경 변수가 Production, Preview, Development 모두에 적용됨
- [ ] 재배포 완료
- [ ] 브라우저 콘솔에서 실제 요청 URL 확인
- [ ] 백엔드 CORS 설정 확인
- [ ] 백엔드가 실제로 해당 URL에서 접근 가능한지 확인

## 디버깅

브라우저 콘솔에서 확인:

```javascript
// 실제 사용 중인 API URL 확인
console.log(import.meta.env.VITE_API_BASE_URL);
```

Network 탭에서:

- 요청 URL이 올바른지 확인
- 404 에러가 발생하는 URL 확인
- CORS 에러인지 404 에러인지 구분
