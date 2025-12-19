# ngrok을 사용한 임시 백엔드 배포 가이드

## 현재 ngrok 설정

**ngrok URL:** `https://93ebcddf793e.ngrok-free.app`

이 URL은 ngrok이 실행 중일 때만 유효하며, ngrok을 재시작하면 변경됩니다.

## Vercel 환경 변수 설정

### 1단계: Vercel 대시보드 접속

1. https://vercel.com/dashboard 접속
2. `focusmate` 프로젝트 선택
3. **Settings** → **Environment Variables** 클릭

### 2단계: 환경 변수 추가

다음 환경 변수를 추가하세요:

```
Name: VITE_API_BASE_URL
Value: https://93ebcddf793e.ngrok-free.app/api/v1

Environment:
✅ Production
✅ Preview
✅ Development
```

### 3단계: 저장 및 재배포

1. **Add** 버튼 클릭하여 저장
2. **Deployments** 탭으로 이동
3. 최신 배포의 **⋯** 메뉴 → **Redeploy** 클릭
4. 또는 `git push`로 자동 재배포

## ⚠️ 중요 사항

### ngrok URL 변경 시

ngrok을 재시작하면 URL이 변경됩니다. 변경 시:

1. 새로운 ngrok URL 확인
2. Vercel 환경 변수 `VITE_API_BASE_URL` 업데이트
3. 재배포

### ngrok 무료 버전 제한

- URL이 재시작 시마다 변경됨
- 연결 수 제한
- 세션 타임아웃 (8시간)

### 영구 해결책

임시 테스트용으로는 ngrok이 좋지만, 프로덕션에서는 다음을 권장합니다:

- **Railway**: https://railway.app
- **Render**: https://render.com
- **Fly.io**: https://fly.io

## 백엔드 CORS 설정 확인

백엔드 `.env` 파일에 다음이 포함되어 있는지 확인:

```
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080,https://eieconcierge.com,https://www.eieconcierge.com
```

✅ 이미 설정되어 있습니다.

## 테스트

환경 변수 설정 후:

1. Vercel 재배포 완료 대기
2. https://eieconcierge.com 접속
3. 브라우저 개발자 도구 → Network 탭 확인
4. API 요청이 `https://93ebcddf793e.ngrok-free.app/api/v1`로 가는지 확인

## 문제 해결

### 여전히 404 에러가 발생하는 경우

1. **ngrok이 실행 중인지 확인**
   ```bash
   # ngrok이 실행 중이어야 함
   # 터미널에서 확인: https://93ebcddf793e.ngrok-free.app 접속 가능한지
   ```

2. **Vercel 환경 변수 확인**
   - Vercel 대시보드에서 `VITE_API_BASE_URL` 값 확인
   - 올바른 환경(Production, Preview, Development)에 설정되었는지 확인

3. **재배포 확인**
   - 환경 변수 변경 후 반드시 재배포 필요
   - 빌드 로그에서 환경 변수가 포함되었는지 확인

4. **브라우저 캐시 클리어**
   - 하드 리프레시: `Cmd+Shift+R` (Mac) 또는 `Ctrl+Shift+R` (Windows)

### CORS 에러가 발생하는 경우

백엔드 `.env` 파일의 `CORS_ORIGINS`에 `https://eieconcierge.com`이 포함되어 있는지 확인하고, 백엔드를 재시작하세요.

