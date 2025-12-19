# 환경 변수 값 확인 및 수정 가이드

## ⚠️ 중요: 환경 변수 값 확인 필요

이미지에서 보이는 환경 변수 값:
```
VITE_API_BASE_URL = https://93ebcddf793e.ngrok-free.app
```

## 올바른 값

코드(`frontend/src/api/client.ts`)를 보면 환경 변수 값을 그대로 사용하므로, **`/api/v1`까지 포함**되어야 합니다:

```
VITE_API_BASE_URL = https://93ebcddf793e.ngrok-free.app/api/v1
```

## 수정 방법

1. **Vercel 대시보드 접속**
   - https://vercel.com/dashboard
   - `focusmate` 프로젝트 선택
   - Settings → Environment Variables

2. **환경 변수 수정**
   - `VITE_API_BASE_URL` 클릭하여 편집
   - 값 수정: `https://93ebcddf793e.ngrok-free.app/api/v1`
   - 저장

3. **재배포**
   - Deployments 탭 → 최신 배포의 ⋯ 메뉴 → Redeploy
   - 또는 `git push`로 자동 재배포

## 확인 방법

재배포 후 브라우저 콘솔에서:

```javascript
console.log(import.meta.env.VITE_API_BASE_URL);
```

예상 출력: `https://93ebcddf793e.ngrok-free.app/api/v1`

## 현재 코드 동작

`frontend/src/api/client.ts`의 `getApiBaseUrl()` 함수:
1. `VITE_API_BASE_URL` 환경 변수 확인 (우선)
2. 없으면 프로덕션: `window.location.origin + /api/v1`
3. 없으면 개발: `http://localhost:8000/api/v1`

따라서 환경 변수에 `/api/v1`이 포함되어야 합니다!

