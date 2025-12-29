# Cloudflare Tunnel 설정 가이드

백엔드를 Cloudflare Tunnel로 연결하기 위한 단계별 설정 가이드입니다.

## 준비 상태 확인

### 필수 도구 설치

- `cloudflared` 설치 완료
- 백엔드 서버 실행 가능 상태

### Cloudflare 계정 설정

- Cloudflare 계정 생성 완료
- 도메인 `eieconcierge.com` 추가 완료
- DNS 레코드 스캔/설정 완료
- Nameserver 변경 완료 (도메인 등록업체에서)

## Cloudflare Zero Trust 설정

### 3. Zero Trust 팀 설정

- [x] Zero Trust 팀 이름 설정 완료
  - 대시보드: https://one.dash.cloudflare.com/
  - 팀 이름 예: `focusmate` 또는 원하는 이름

### 4. Tunnel 생성

- [x] Zero Trust 대시보드 접속
  - 경로: Networks → Tunnels
- [x] "Create a tunnel" 클릭
- [x] Tunnel 이름 입력: `focusmate-backend`
- [x] Connector 선택: `cloudflared` 선택
- [x] 설치 명령어 복사 (나중에 사용)

### 5. Public Hostname 설정

- [x] 생성한 Tunnel 선택
- [x] "Public Hostname" 탭 클릭
- [x] "Add a public hostname" 클릭
- [x] 설정 입력:
  - **Subdomain**: `api`
  - **Domain**: `eieconcierge.com`
  - **Service**: `http://localhost:8000`
  - **Path**: (비워두기 - 모든 경로 허용)
- [x] "Save hostname" 클릭

### 6. DNS 레코드 확인

- [x] Cloudflare 대시보드 → DNS → Records
- [x] `api.eieconcierge.com` CNAME 레코드 자동 생성 확인
  - 형식: `api` → CNAME → `[tunnel-id].cfargotunnel.com`

## 로컬 설정 및 실행

### 7. 백엔드 CORS 설정 확인

- [ ] `backend/.env` 파일 확인
- [ ] `CORS_ORIGINS`에 Vercel 도메인 포함 확인
  ```bash
  CORS_ORIGINS=...,https://eieconcierge.com,https://www.eieconcierge.com
  ```

### 8. 백엔드 서버 실행

```bash
cd backend
./run.sh
```

- [ ] 백엔드가 `http://localhost:8000`에서 실행 중
- [ ] Health check 확인: `curl http://localhost:8000/health`

### 9. Cloudflare Tunnel 실행

```bash
# 방법 1: 스크립트 사용 (권장)
./scripts/start-cloudflare-tunnel.sh

# 방법 2: 직접 실행
cloudflared tunnel run focusmate-backend
```

- [ ] Tunnel 실행 확인
- [ ] 로그 확인: `tail -f ~/.cloudflare-tunnel/tunnel.log`

### 10. Tunnel 연결 테스트

- [ ] `https://api.eieconcierge.com/health` 접속 테스트
- [ ] 또는 Zero Trust 대시보드에서 Tunnel 상태 확인

## Vercel 환경 변수 설정

### 11. Vercel 대시보드 설정

- [ ] Vercel 대시보드 접속: https://vercel.com/dashboard
- [ ] 프로젝트 선택
- [ ] Settings → Environment Variables

### 12. 환경 변수 추가

다음 환경 변수를 **모든 환경** (Production, Preview, Development)에 추가:

| Key                 | Value                                 | 설명          |
| ------------------- | ------------------------------------- | ------------- |
| `VITE_API_BASE_URL` | `https://api.eieconcierge.com/api/v1` | API 기본 URL  |
| `VITE_WS_BASE_URL`  | `wss://api.eieconcierge.com`          | WebSocket URL |

- [ ] `VITE_API_BASE_URL` 설정 완료
- [ ] `VITE_WS_BASE_URL` 설정 완료
- [ ] 모든 환경에 적용 확인

### 13. Vercel 재배포

- [ ] 환경 변수 저장 후 재배포
- [ ] 또는 `git push`로 자동 재배포

## 최종 테스트

### 14. 통합 테스트

- [ ] Vercel 배포된 프론트엔드 접속
- [ ] 브라우저 개발자 도구 → Network 탭
- [ ] API 요청이 `https://api.eieconcierge.com`으로 가는지 확인
- [ ] CORS 에러 없는지 확인
- [ ] WebSocket 연결 확인

### 15. 문제 해결

- [ ] CORS 에러 발생 시:
  - `backend/.env`의 `CORS_ORIGINS` 확인
  - 백엔드 서버 재시작
- [ ] 502/503 에러 발생 시:
  - Tunnel 실행 상태 확인
  - 백엔드 서버 실행 상태 확인
  - Tunnel 로그 확인

## 유용한 명령어

```bash
# Tunnel 상태 확인
cloudflared tunnel list

# Tunnel 로그 확인
tail -f ~/.cloudflare-tunnel/tunnel.log

# Tunnel 시작
./scripts/start-cloudflare-tunnel.sh

# Tunnel 중지
./scripts/stop-cloudflare-tunnel.sh

# 백엔드 Health check
curl http://localhost:8000/health

# API Health check (Tunnel을 통해)
curl https://api.eieconcierge.com/health
```

## 참고 링크

- [Cloudflare Zero Trust 대시보드](https://one.dash.cloudflare.com/)
- [Cloudflare Dashboard](https://dash.cloudflare.com/)
- [하이브리드 아키텍처 가이드](./HYBRID_ARCHITECTURE.md)
- [Vercel 환경 변수 설정](./DEPLOY-003_Vercel_Env_Setup.md)
