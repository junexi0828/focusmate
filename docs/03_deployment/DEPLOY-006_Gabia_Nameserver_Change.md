# Gabia Nameserver 변경 가이드

Cloudflare를 통해 DNS를 관리하기 위해 Gabia에서 Nameserver를 변경해야 합니다.

## 변경 전 확인사항

현재 Gabia DNS 레코드:

- A 레코드: `@` → `76.76.21.21`
- CNAME 레코드: `www` → `cname.vercel-dns.com.`
- TXT 레코드: `@` → Google site verification

**중요:** Cloudflare에서 이미 DNS 레코드를 스캔했으므로, Nameserver 변경 후에도 기존 레코드가 유지됩니다.

## Gabia에서 Nameserver 변경 방법

### 1단계: Gabia 로그인

1. https://www.gabia.com 접속
2. 로그인

### 2단계: 도메인 관리 페이지 접속

1. "My 가비아" 또는 "도메인 관리" 메뉴 클릭
2. `eieconcierge.com` 도메인 선택
3. "DNS 설정" 또는 "네임서버 설정" 메뉴 찾기

### 3단계: Nameserver 변경

Gabia에서 Nameserver 설정 위치는 보통:

- **"도메인 관리" → "네임서버 설정"** 또는
- **"DNS 설정" → "네임서버 변경"**

**변경할 Nameserver:**

```
carol.ns.cloudflare.com
henry.ns.cloudflare.com
```

**제거할 Nameserver (기존):**

```
ns.gabia.co.kr
ns.gabia.net
ns1.gabia.co.kr
```

### 4단계: DNSSEC 확인

- DNSSEC가 활성화되어 있다면 **비활성화**해야 합니다
- Cloudflare에서 나중에 다시 활성화할 수 있습니다

### 5단계: 저장

- 변경사항 저장
- 변경 완료까지 최대 24시간 소요 (보통 몇 시간 내 완료)

## 주의사항

1. **다운타임 없음**: Nameserver 변경은 일반적으로 다운타임을 발생시키지 않습니다
2. **DNS 전파 시간**: 변경사항이 전 세계에 전파되는데 시간이 걸립니다
3. **기존 DNS 레코드**: Cloudflare에서 이미 스캔한 레코드들이 자동으로 유지됩니다

## 변경 후 확인

### Cloudflare 대시보드에서 확인

1. Cloudflare Dashboard → DNS → Records
2. 기존 레코드들이 표시되는지 확인:
   - A 레코드: `eieconcierge.com` → `76.76.21.21`
   - CNAME 레코드: `www` → `cname.vercel-dns.com`
   - TXT 레코드: Google site verification

### Nameserver 변경 확인

```bash
# 터미널에서 확인
dig NS eieconcierge.com

# 또는 온라인 도구 사용
# https://www.whatsmydns.net/#NS/eieconcierge.com
```

결과에 다음이 포함되어야 합니다:

- `carol.ns.cloudflare.com`
- `henry.ns.cloudflare.com`

## 다음 단계

Nameserver 변경이 완료되면:

1. **Cloudflare Tunnel 생성**

   - Zero Trust 대시보드 → Networks → Tunnels → Create a tunnel

2. **Public Hostname 설정**

   - Subdomain: `api`
   - Domain: `eieconcierge.com`
   - Service: `http://localhost:8000`

3. **Tunnel 실행**
   ```bash
   ./scripts/start-cloudflare-tunnel.sh
   ```

## Gabia에서 찾기 어려운 경우

Gabia 인터페이스가 다를 수 있으므로:

- "네임서버" 또는 "Nameserver" 검색
- "DNS 관리" 메뉴 확인
- 고객센터 문의: 1588-5821

## 참고 링크

- [Cloudflare Nameserver 변경 가이드](https://developers.cloudflare.com/dns/zone-setups/full-setup/setup/)
- [Gabia 도메인 관리](https://www.gabia.com)
