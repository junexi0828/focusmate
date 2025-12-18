# Focus Mate 기술 발표 시각화 자료

> **작성일**: 2025-12-18
> **용도**: 기술 발표용 전문 다이어그램
> **형식**: Mermaid 다이어그램 코드

---

## 사용 방법

### 1. Mermaid Live Editor
1. https://mermaid.live 접속
2. 아래 코드 복사/붙여넣기
3. PNG/SVG로 내보내기

### 2. draw.io (diagrams.net)
1. https://app.diagrams.net 접속
2. Arrange → Insert → Advanced → Mermaid
3. 코드 붙여넣기

### 3. Markdown 문서
- GitHub, GitLab, Notion 등에서 직접 렌더링
- 코드 블록에 \`\`\`mermaid 사용

---

## 1. 시스템 아키텍처 다이어그램

### 전체 시스템 구조

\`\`\`mermaid
graph TB
    subgraph "클라이언트 계층"
        A[React 18.3.1 SPA]
        A1[TanStack Router 1.141.0]
        A2[TanStack Query 5.90.12]
        A3[Tailwind CSS 4.1.18]
        A --> A1
        A --> A2
        A --> A3
    end

    subgraph "백엔드 계층"
        B[FastAPI 0.115.6]
        B1[Python 3.13]
        B2[SQLAlchemy 2.0.35+]
        B3[Pydantic 2.10.6]
        B --> B1
        B --> B2
        B --> B3
    end

    subgraph "데이터 계층"
        C[(PostgreSQL)]
        D[(Redis)]
        C1[38개 테이블]
        D1[Pub/Sub]
        C --> C1
        D --> D1
    end

    A -->|REST API<br/>HTTPS| B
    A -.->|WebSocket| B
    B -->|asyncpg<br/>비동기 쿼리| C
    B -->|Pub/Sub<br/>메시지| D

    style A fill:#3B82F6,stroke:#1E40AF,color:#fff
    style B fill:#10B981,stroke:#047857,color:#fff
    style C fill:#F59E0B,stroke:#D97706,color:#fff
    style D fill:#EF4444,stroke:#DC2626,color:#fff
\`\`\`

---

## 2. 기술 스택 레이어 다이어그램

### 계층별 기술 스택

\`\`\`mermaid
graph TD
    subgraph "프레젠테이션 계층"
        L1[React 18.3.1<br/>TypeScript 5.9.3<br/>Vite 6.4.1]
    end

    subgraph "라우팅 & 상태 관리"
        L2[TanStack Router 1.141.0<br/>TanStack Query 5.90.12<br/>Axios 1.13.2]
    end

    subgraph "UI 컴포넌트"
        L3[Radix UI Components<br/>Tailwind CSS 4.1.18<br/>Framer Motion 12.23.26<br/>Recharts 2.15.4]
    end

    subgraph "백엔드 API"
        L4[FastAPI 0.115.6<br/>Uvicorn 0.34.0<br/>Python 3.13]
    end

    subgraph "비즈니스 로직"
        L5[SQLAlchemy 2.0.35+<br/>Pydantic 2.10.6<br/>JWT + bcrypt]
    end

    subgraph "데이터 저장소"
        L6[PostgreSQL Supabase<br/>Redis Cache/Pub-Sub<br/>Alembic 1.14.0]
    end

    L1 --> L2 --> L3 --> L4 --> L5 --> L6

    style L1 fill:#3B82F6,stroke:#1E40AF,color:#fff
    style L2 fill:#8B5CF6,stroke:#6D28D9,color:#fff
    style L3 fill:#EC4899,stroke:#DB2777,color:#fff
    style L4 fill:#10B981,stroke:#047857,color:#fff
    style L5 fill:#14B8A6,stroke:#0F766E,color:#fff
    style L6 fill:#F59E0B,stroke:#D97706,color:#fff
\`\`\`

---

## 3. 데이터 흐름 다이어그램

### 요청/응답 사이클

\`\`\`mermaid
sequenceDiagram
    participant C as React Client
    participant Q as TanStack Query
    participant A as Axios
    participant B as FastAPI Backend
    participant P as PostgreSQL
    participant R as Redis

    Note over C,R: HTTP 요청 흐름
    C->>Q: useQuery('users')
    Q->>Q: 캐시 확인
    alt 캐시 히트
        Q-->>C: 캐시 데이터 반환
    else 캐시 미스
        Q->>A: HTTP GET /api/v1/users
        A->>A: JWT 토큰 추가
        A->>B: HTTPS Request
        B->>B: JWT 검증
        B->>B: Pydantic 유효성 검사
        B->>P: SELECT * FROM user
        P-->>B: 사용자 목록
        B->>R: 결과 캐싱
        B-->>A: JSON Response
        A-->>Q: 데이터 파싱
        Q->>Q: 캐시 업데이트
        Q-->>C: 데이터 반환
    end

    Note over C,R: WebSocket 실시간 통신
    C->>B: WebSocket 연결
    B->>R: 채널 구독
    B-->>C: 연결 확인

    Note over B,R: 알림 발생
    B->>R: Publish 메시지
    R-->>B: Broadcast
    B-->>C: 실시간 알림 푸시
\`\`\`

---

## 4. 데이터베이스 스키마 개요

### 38개 테이블 도메인 분류

\`\`\`mermaid
graph LR
    subgraph "핵심 도메인"
        CORE[User<br/>Room<br/>Participant<br/>Timer<br/>Session History]
    end

    subgraph "사용자 관리"
        USER[User Settings<br/>User Goals<br/>User Achievement<br/>Achievement<br/>User Verification]
    end

    subgraph "커뮤니티"
        COMM[Post<br/>Comment<br/>Post Like<br/>Comment Like<br/>Post Read]
    end

    subgraph "랭킹 시스템"
        RANK[Leaderboard<br/>Teams<br/>Team Members<br/>Ranking Sessions<br/>Verification Requests]
    end

    subgraph "매칭 시스템"
        MATCH[Matching Pools<br/>Proposals<br/>Matching Chat<br/>Chat Members<br/>Messages]
    end

    subgraph "메시징"
        MSG[Chat Rooms<br/>Chat Members<br/>Chat Messages<br/>Conversation<br/>Message]
    end

    subgraph "친구"
        FRIEND[Friend<br/>Friend Request]
    end

    subgraph "알림"
        NOTIF[Notifications]
    end

    CORE -.-> USER
    CORE -.-> COMM
    CORE -.-> RANK
    CORE -.-> MATCH
    CORE -.-> MSG
    CORE -.-> FRIEND
    CORE -.-> NOTIF

    style CORE fill:#3B82F6,stroke:#1E40AF,color:#fff
    style USER fill:#8B5CF6,stroke:#6D28D9,color:#fff
    style COMM fill:#EC4899,stroke:#DB2777,color:#fff
    style RANK fill:#10B981,stroke:#047857,color:#fff
    style MATCH fill:#F59E0B,stroke:#D97706,color:#fff
    style MSG fill:#14B8A6,stroke:#0F766E,color:#fff
    style FRIEND fill:#EAB308,stroke:#CA8A04,color:#fff
    style NOTIF fill:#EF4444,stroke:#DC2626,color:#fff
\`\`\`

---

## 5. WebSocket 아키텍처

### 실시간 통신 구조

\`\`\`mermaid
graph TB
    subgraph "클라이언트"
        C1[Client 1<br/>WebSocket]
        C2[Client 2<br/>WebSocket]
        C3[Client 3<br/>WebSocket]
    end

    subgraph "백엔드 인스턴스"
        B1[Backend 1<br/>FastAPI WS Handler]
        B2[Backend 2<br/>FastAPI WS Handler]
        B3[Backend 3<br/>FastAPI WS Handler]
    end

    subgraph "Redis Pub/Sub"
        R[Redis<br/>Message Broker]
        CH1[notifications:user:id]
        CH2[room:id:updates]
        CH3[matching:chat:id]
        R --> CH1
        R --> CH2
        R --> CH3
    end

    C1 <-->|WSS| B1
    C2 <-->|WSS| B2
    C3 <-->|WSS| B3

    B1 <-->|Pub/Sub| R
    B2 <-->|Pub/Sub| R
    B3 <-->|Pub/Sub| R

    style C1 fill:#3B82F6,stroke:#1E40AF,color:#fff
    style C2 fill:#3B82F6,stroke:#1E40AF,color:#fff
    style C3 fill:#3B82F6,stroke:#1E40AF,color:#fff
    style B1 fill:#10B981,stroke:#047857,color:#fff
    style B2 fill:#10B981,stroke:#047857,color:#fff
    style B3 fill:#10B981,stroke:#047857,color:#fff
    style R fill:#EF4444,stroke:#DC2626,color:#fff
\`\`\`

---

## 6. API 엔드포인트 개요

### REST API 구조

\`\`\`mermaid
mindmap
  root((Focus Mate<br/>REST API))
    Authentication
      POST /auth/login
      POST /auth/register
      GET /auth/profile
    Rooms
      GET /rooms
      POST /rooms
      GET /rooms/{id}
      DELETE /rooms/{id}
    Community
      GET /community/posts
      POST /community/posts
      GET /community/posts/{id}
      POST /community/posts/{id}/like
    Ranking
      GET /ranking/leaderboard
      GET /ranking/teams
      POST /ranking/teams
      POST /ranking/verification-requests
    Matching
      GET /matching/pools
      POST /matching/pools
      POST /matching/pools/{id}/join
      GET /matching/proposals
    Chat
      GET /chat/rooms
      GET /chat/rooms/{id}/messages
      POST /chat/rooms/{id}/messages
    Friends
      GET /friends
      POST /friends/requests
      POST /friends/requests/{id}/respond
    Stats
      GET /stats/user/{id}
      GET /stats/sessions
      GET /stats/achievements
    Notifications
      WebSocket /notifications/ws
\`\`\`

---

## 7. 인증 흐름

### JWT 인증 프로세스

\`\`\`mermaid
sequenceDiagram
    participant U as User
    participant C as Client
    participant B as Backend
    participant DB as PostgreSQL

    Note over U,DB: 로그인 프로세스
    U->>C: 이메일/비밀번호 입력
    C->>B: POST /auth/login
    B->>DB: SELECT user WHERE email=?
    DB-->>B: User data
    B->>B: bcrypt.verify(password)
    alt 비밀번호 일치
        B->>B: JWT 토큰 생성
        B-->>C: {access_token, user}
        C->>C: localStorage.setItem('token')
        C-->>U: 로그인 성공
    else 비밀번호 불일치
        B-->>C: 401 Unauthorized
        C-->>U: 로그인 실패
    end

    Note over U,DB: 인증된 요청
    U->>C: 데이터 요청
    C->>C: token = localStorage.getItem('token')
    C->>B: GET /api/v1/users/me<br/>Authorization: Bearer {token}
    B->>B: JWT 검증
    alt 토큰 유효
        B->>DB: SELECT user WHERE id=?
        DB-->>B: User data
        B-->>C: User data
        C-->>U: 데이터 표시
    else 토큰 만료/무효
        B-->>C: 401 Unauthorized
        C->>C: localStorage.removeItem('token')
        C-->>U: 로그인 페이지로 이동
    end
\`\`\`

---

## 8. 배포 아키텍처

### 프로덕션 환경

\`\`\`mermaid
graph TB
    subgraph "사용자"
        U[Users]
    end

    subgraph "CDN/Load Balancer"
        CDN[Cloudflare CDN]
        LB[Load Balancer]
    end

    subgraph "프론트엔드"
        FE1[React App<br/>Instance 1]
        FE2[React App<br/>Instance 2]
    end

    subgraph "백엔드 클러스터"
        BE1[FastAPI<br/>Instance 1]
        BE2[FastAPI<br/>Instance 2]
        BE3[FastAPI<br/>Instance 3]
    end

    subgraph "데이터베이스"
        PG[(PostgreSQL<br/>Primary)]
        PGR[(PostgreSQL<br/>Replica)]
        RD[(Redis<br/>Cluster)]
    end

    U -->|HTTPS| CDN
    CDN --> LB
    LB --> FE1
    LB --> FE2

    FE1 -->|API Calls| BE1
    FE1 -->|API Calls| BE2
    FE2 -->|API Calls| BE2
    FE2 -->|API Calls| BE3

    BE1 --> PG
    BE2 --> PG
    BE3 --> PG

    BE1 --> RD
    BE2 --> RD
    BE3 --> RD

    PG -.->|Replication| PGR

    style U fill:#3B82F6,stroke:#1E40AF,color:#fff
    style CDN fill:#8B5CF6,stroke:#6D28D9,color:#fff
    style LB fill:#EC4899,stroke:#DB2777,color:#fff
    style FE1 fill:#10B981,stroke:#047857,color:#fff
    style FE2 fill:#10B981,stroke:#047857,color:#fff
    style BE1 fill:#14B8A6,stroke:#0F766E,color:#fff
    style BE2 fill:#14B8A6,stroke:#0F766E,color:#fff
    style BE3 fill:#14B8A6,stroke:#0F766E,color:#fff
    style PG fill:#F59E0B,stroke:#D97706,color:#fff
    style PGR fill:#F59E0B,stroke:#D97706,color:#fff
    style RD fill:#EF4444,stroke:#DC2626,color:#fff
\`\`\`

---

## 9. 성능 최적화 전략

### 캐싱 및 최적화

\`\`\`mermaid
graph LR
    subgraph "클라이언트 캐싱"
        A[TanStack Query<br/>5분 staleTime]
        B[브라우저 캐시<br/>정적 리소스]
    end

    subgraph "서버 캐싱"
        C[Redis 캐시<br/>1-5분 TTL]
        D[PostgreSQL<br/>Connection Pool]
    end

    subgraph "최적화"
        E[Code Splitting<br/>Lazy Loading]
        F[이미지 최적화<br/>WebP]
        G[Gzip 압축]
    end

    A --> C
    C --> D
    E --> A
    F --> B
    G --> B

    style A fill:#3B82F6,stroke:#1E40AF,color:#fff
    style B fill:#8B5CF6,stroke:#6D28D9,color:#fff
    style C fill:#EF4444,stroke:#DC2626,color:#fff
    style D fill:#F59E0B,stroke:#D97706,color:#fff
    style E fill:#10B981,stroke:#047857,color:#fff
    style F fill:#14B8A6,stroke:#0F766E,color:#fff
    style G fill:#EC4899,stroke:#DB2777,color:#fff
\`\`\`

---

## 10. 보안 아키텍처

### 보안 계층

\`\`\`mermaid
graph TD
    subgraph "네트워크 보안"
        A[HTTPS/TLS 1.3]
        B[CORS 정책]
        C[Rate Limiting]
    end

    subgraph "인증/인가"
        D[JWT 토큰]
        E[bcrypt 해싱]
        F[토큰 만료 검증]
    end

    subgraph "데이터 보안"
        G[SQL Injection 방지<br/>Parameterized Queries]
        H[XSS 방지<br/>Content Security Policy]
        I[CSRF 방지<br/>SameSite Cookies]
    end

    subgraph "모니터링"
        J[로그 수집]
        K[이상 탐지]
        L[보안 감사]
    end

    A --> D
    B --> D
    C --> D
    D --> G
    E --> G
    F --> G
    G --> J
    H --> K
    I --> L

    style A fill:#3B82F6,stroke:#1E40AF,color:#fff
    style B fill:#8B5CF6,stroke:#6D28D9,color:#fff
    style C fill:#EC4899,stroke:#DB2777,color:#fff
    style D fill:#10B981,stroke:#047857,color:#fff
    style E fill:#14B8A6,stroke:#0F766E,color:#fff
    style F fill:#F59E0B,stroke:#D97706,color:#fff
    style G fill:#EF4444,stroke:#DC2626,color:#fff
    style H fill:#EAB308,stroke:#CA8A04,color:#fff
    style I fill:#6366F1,stroke:#4F46E5,color:#fff
    style J fill:#EC4899,stroke:#DB2777,color:#fff
    style K fill:#8B5CF6,stroke:#6D28D9,color:#fff
    style L fill:#3B82F6,stroke:#1E40AF,color:#fff
\`\`\`

---

## 사용 팁

### 고품질 이미지 생성

1. **Mermaid Live Editor**:
   - PNG: 고해상도 (2x, 3x 스케일)
   - SVG: 벡터 형식 (무한 확대)

2. **draw.io**:
   - File → Export as → PNG/SVG
   - 해상도: 300 DPI 이상 권장

3. **PowerPoint/Keynote**:
   - SVG 파일 직접 삽입
   - 크기 조정 시 품질 유지

### 색상 커스터마이징

문서에서 `style` 명령어로 색상 변경 가능:
\`\`\`
style NodeName fill:#COLOR,stroke:#BORDER,color:#TEXT
\`\`\`

---

**작성 완료**: 2025-12-18 19:20
**다이어그램 수**: 10개
**형식**: Mermaid 코드
