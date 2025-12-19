# Vercel 환경 변수 설정 및 재배포 가이드

## 현재 문제

에러 로그를 보면 여전히 `https://eieconcierge.com/api/v1`로 요청이 가고 있습니다.
이는 Vercel 환경 변수가 설정되지 않았거나 재배포가 되지 않았음을 의미합니다.

## 해결 방법

### 1단계: Vercel 환경 변수 확인 및 설정

1. **Vercel 대시보드 접속**
   - https://vercel.com/dashboard
   - `focusmate` 프로젝트 선택

2. **Settings → Environment Variables** 클릭

3. **환경 변수 확인**
   - `VITE_API_BASE_URL`이 있는지 확인
   - 값이 `https://93ebcddf793e.ngrok-free.app/api/v1`인지 확인
   - Production, Preview, Development 모두에 설정되었는지 확인

4. **없다면 추가**
   ```
   Name: VITE_API_BASE_URL
   Value: https://93ebcddf793e.ngrok-free.app/api/v1

   Environment:
   ✅ Production
   ✅ Preview
   ✅ Development
   ```

### 2단계: 재배포 (필수!)

**중요:** 환경 변수를 추가/수정한 후 반드시 재배포해야 합니다!

#### 방법 A: Vercel 대시보드에서 재배포
1. **Deployments** 탭으로 이동
2. 최신 배포의 **⋯** 메뉴 클릭
3. **Redeploy** 선택
4. 배포 완료 대기 (보통 1-2분)

#### 방법 B: Git Push로 재배포
```bash
# 아무 변경사항이나 커밋하고 푸시
git commit --allow-empty -m "Trigger redeploy for env vars"
git push
```

### 3단계: 빌드 로그 확인

재배포 후:

1. **Deployments** 탭에서 최신 배포 클릭
2. **Build Logs** 확인
3. 환경 변수가 포함되었는지 확인:
   ```
   VITE_API_BASE_URL=https://93ebcddf793e.ngrok-free.app/api/v1
   ```

### 4단계: 브라우저에서 확인

1. **하드 리프레시**
   - Mac: `Cmd + Shift + R`
   - Windows: `Ctrl + Shift + R`

2. **개발자 도구 → Network 탭**
   - API 요청이 `https://93ebcddf793e.ngrok-free.app/api/v1`로 가는지 확인
   - 더 이상 `https://eieconcierge.com/api/v1`로 가지 않는지 확인

3. **콘솔 확인**
   - 404 에러가 사라졌는지 확인

## 문제 해결

### 여전히 `eieconcierge.com`으로 요청이 가는 경우

1. **환경 변수 이름 확인**
   - 반드시 `VITE_API_BASE_URL` (대소문자 정확히)
   - `VITE_` 접두사 필수 (Vite 빌드 시 포함됨)

2. **재배포 확인**
   - 환경 변수 변경 후 반드시 재배포 필요
   - 빌드 로그에서 환경 변수 확인

3. **브라우저 캐시**
   - 하드 리프레시 시도
   - 시크릿 모드에서 테스트

4. **빌드 시점 확인**
   - Vercel은 빌드 시점에 환경 변수를 포함
   - 런타임이 아닌 빌드 타임에 포함됨

### ngrok URL이 변경된 경우

ngrok을 재시작하면 URL이 변경됩니다:

1. 새로운 ngrok URL 확인
2. Vercel 환경 변수 업데이트
3. 재배포

## 디버깅 팁

### 브라우저 콘솔에서 확인

```javascript
// 실제 사용 중인 API URL 확인
console.log(import.meta.env.VITE_API_BASE_URL);
```

이 값이 `undefined`이면 환경 변수가 설정되지 않은 것입니다.

### Vercel 빌드 로그 확인

빌드 로그에서 다음을 확인:
- 환경 변수가 빌드에 포함되었는지
- 빌드 에러가 없는지
- 빌드가 성공적으로 완료되었는지

## 체크리스트

- [ ] Vercel 환경 변수 `VITE_API_BASE_URL` 설정됨
- [ ] 환경 변수 값이 올바름: `https://93ebcddf793e.ngrok-free.app/api/v1`
- [ ] Production, Preview, Development 모두에 설정됨
- [ ] 재배포 완료됨
- [ ] 빌드 로그에서 환경 변수 확인됨
- [ ] 브라우저 하드 리프레시 완료
- [ ] Network 탭에서 올바른 URL로 요청 확인됨

