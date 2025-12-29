# Cloudflare Tunnel 설정 완료 후 다음 단계

## 현재 완료된 작업

- ✅ Cloudflare Tunnel 생성 및 실행 (`focusmate-backend`)
- ✅ DNS 레코드 설정 (`api.eieconcierge.com` → Tunnel)
- ✅ 백엔드 서버 실행 중
- ✅ Tunnel 상태: 정상

## 다음 단계

### 1. Vercel 환경 변수 설정 (필수)

Vercel 대시보드에서 다음 환경 변수를 설정하세요:

1. **Vercel 대시보드 접속**

   - https://vercel.com/dashboard
   - `focusmate` 프로젝트 선택

2. **Settings → Environment Variables** 클릭

3. **환경 변수 추가/수정**

   | Key                 | Value                                 | Environment                      |
   | ------------------- | ------------------------------------- | -------------------------------- |
   | `VITE_API_BASE_URL` | `https://api.eieconcierge.com/api/v1` | Production, Preview, Development |
   | `VITE_WS_BASE_URL`  | `wss://api.eieconcierge.com`          | Production, Preview, Development |

   **중요:**

   - 모든 환경(Production, Preview, Development)에 설정
   - `VITE_API_BASE_URL`에는 `/api/v1`까지 포함
   - `VITE_WS_BASE_URL`은 `wss://` (WebSocket Secure) 사용

4. **저장**

### 2. Vercel 재배포 (필수!)

환경 변수를 추가/수정한 후 반드시 재배포해야 합니다.

#### 방법 A: Vercel 대시보드에서 재배포

1. **Deployments** 탭으로 이동
2. 최신 배포의 **⋯** 메뉴 클릭
3. **Redeploy** 선택
4. 배포 완료 대기 (보통 1-2분)

#### 방법 B: Git Push로 재배포

```bash
git commit --allow-empty -m "Update API URLs for Cloudflare Tunnel"
git push
```

### 3. 백엔드 CORS 설정 확인

`backend/.env` 파일의 `CORS_ORIGINS`에 Vercel 도메인이 포함되어 있는지 확인:

```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:8080,https://eieconcierge.com,https://www.eieconcierge.com
```

**확인 사항:**

- `https://eieconcierge.com` 포함 확인
- `https://www.eieconcierge.com` 포함 확인
- 백엔드 서버 재시작 (변경 사항 적용)

### 4. 연결 테스트

#### API 연결 테스트

```bash
# Tunnel을 통한 API Health Check
curl https://api.eieconcierge.com/health

# 예상 응답: {"status":"ok"} 또는 200 OK
```

#### 로컬 백엔드 확인

```bash
# 로컬 백엔드 Health Check
curl http://localhost:8000/health
```

### 5. 프론트엔드 테스트

1. **Vercel 배포된 프론트엔드 접속**

   - https://eieconcierge.com 또는 https://www.eieconcierge.com

2. **브라우저 개발자 도구 열기**

   - F12 또는 Cmd+Option+I (Mac)
   - **Network** 탭 선택

3. **확인 사항:**
   - API 요청이 `https://api.eieconcierge.com`으로 가는지 확인
   - CORS 에러가 없는지 확인
   - WebSocket 연결이 `wss://api.eieconcierge.com`으로 가는지 확인

### 6. 문제 해결

#### CORS 에러 발생 시

1. `backend/.env`의 `CORS_ORIGINS` 확인
2. 백엔드 서버 재시작
3. 브라우저 캐시 삭제

#### 502/503 에러 발생 시

1. Tunnel 실행 상태 확인:
   ```bash
   ps aux | grep cloudflared
   ```
2. 백엔드 서버 실행 상태 확인:
   ```bash
   curl http://localhost:8000/health
   ```
3. Tunnel 로그 확인:
   ```bash
   tail -f ~/.cloudflare-tunnel/tunnel.log
   ```

#### API 연결 실패 시

1. Tunnel 상태 확인 (Cloudflare 대시보드)
2. DNS 전파 확인 (최대 24시간 소요, 보통 몇 시간 내)
3. SSL 인증서 확인 (Cloudflare에서 자동 발급)

## 체크리스트

- [ ] Vercel 환경 변수 설정 (`VITE_API_BASE_URL`, `VITE_WS_BASE_URL`)
- [ ] Vercel 재배포 완료
- [ ] 백엔드 CORS 설정 확인
- [ ] API 연결 테스트 성공
- [ ] 프론트엔드에서 API 호출 확인
- [ ] WebSocket 연결 확인
- [ ] CORS 에러 없음 확인

## 참고 링크

- [Vercel 환경 변수 설정 가이드](./DEPLOY-003_Vercel_Env_Setup.md)
- [Cloudflare Tunnel 설정 가이드](./DEPLOY-007_Cloudflare_Tunnel_Setup.md)
- [하이브리드 아키텍처 가이드](./HYBRID_ARCHITECTURE.md)
