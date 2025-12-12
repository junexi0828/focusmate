# ARCH-007: 과팅 매칭 시스템 아키텍처

## 📋 문서 정보
- **문서 번호**: ARCH-007
- **작성일**: 2025-12-12
- **버전**: 1.0
- **관련 요구사항**: REQ-002

## 🏗️ 시스템 아키텍처

### 전체 구조

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (React)                      │
├─────────────────────────────────────────────────────────┤
│  - 인증 신청 페이지                                        │
│  - 프로필 페이지 (배지 표시)                                │
│  - 매칭 풀 등록 페이지                                      │
│  - 매칭 제안 관리 페이지                                    │
│  - 단체 메시지 페이지                                       │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                   │
├─────────────────────────────────────────────────────────┤
│  - Verification API (인증)                               │
│  - Matching Pool API (매칭 풀)                           │
│  - Matching Proposal API (매칭 제안)                     │
│  - Chat API (메시지)                                     │
│  - Notification API (알림)                               │
└─────────────────────────────────────────────────────────┘
                            ↓
┌──────────────────┬──────────────────┬──────────────────┐
│   PostgreSQL     │   Redis          │   WebSocket      │
│   (메인 DB)       │   (캐시/세션)     │   (실시간 메시지)  │
└──────────────────┴──────────────────┴──────────────────┘
```

## 🗄️ 데이터베이스 설계

### ERD (Entity Relationship Diagram)

```
user
  ├─ user_verification (1:1)
  ├─ matching_pools (1:N) - creator
  └─ matching_chat_members (N:M) - through chat_rooms

matching_pools
  ├─ matching_proposals (N:M) - pool_a / pool_b
  └─ matching_chat_rooms (1:1) - when matched

matching_proposals
  └─ matching_chat_rooms (1:1)

matching_chat_rooms
  ├─ matching_chat_members (N:M)
  └─ matching_messages (1:N)
```

### 테이블 상세 설계

#### 1. user_verification
```sql
CREATE TABLE user_verification (
    verification_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id VARCHAR(36) UNIQUE REFERENCES "user"(id) ON DELETE CASCADE,

    -- 학교 정보
    school_name VARCHAR(100) NOT NULL,

    -- 학과 정보
    department VARCHAR(100) NOT NULL,
    major_category VARCHAR(50), -- 공과대학, 상경계, 인문계 등

    -- 학년 정보
    grade VARCHAR(20) NOT NULL,
    student_id_encrypted TEXT, -- 암호화된 학번

    -- 개인 정보
    gender VARCHAR(10) NOT NULL,

    -- 검증 정보
    verification_status VARCHAR(20) DEFAULT 'pending',
    submitted_documents TEXT[],
    admin_note TEXT,

    -- 노출 설정
    badge_visible BOOLEAN DEFAULT true,
    department_visible BOOLEAN DEFAULT true,

    -- 타임스탬프
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_user_verification_user_id ON user_verification(user_id);
CREATE INDEX idx_user_verification_status ON user_verification(verification_status);
CREATE INDEX idx_user_verification_department ON user_verification(department);
```

#### 2. matching_pools
```sql
CREATE TABLE matching_pools (
    pool_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    creator_id VARCHAR(36) REFERENCES "user"(id) ON DELETE CASCADE,

    -- 그룹 정보
    member_count INTEGER NOT NULL CHECK (member_count BETWEEN 2 AND 8),
    member_ids TEXT[] NOT NULL,

    -- 학과 정보 (대표)
    department VARCHAR(100) NOT NULL,
    grade VARCHAR(20) NOT NULL,
    gender VARCHAR(10) NOT NULL,

    -- 매칭 선호도
    preferred_match_type VARCHAR(20) NOT NULL,
    preferred_categories TEXT[],

    -- 공개 설정
    matching_type VARCHAR(10) NOT NULL,

    -- 메시지
    message TEXT CHECK (LENGTH(message) <= 200),

    -- 상태
    status VARCHAR(20) DEFAULT 'waiting',

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT valid_member_count CHECK (array_length(member_ids, 1) = member_count)
);

CREATE INDEX idx_matching_pools_status ON matching_pools(status);
CREATE INDEX idx_matching_pools_member_count ON matching_pools(member_count);
CREATE INDEX idx_matching_pools_gender ON matching_pools(gender);
CREATE INDEX idx_matching_pools_creator ON matching_pools(creator_id);
```

#### 3. matching_proposals
```sql
CREATE TABLE matching_proposals (
    proposal_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    -- 매칭 그룹
    pool_id_a UUID REFERENCES matching_pools(pool_id) ON DELETE CASCADE,
    pool_id_b UUID REFERENCES matching_pools(pool_id) ON DELETE CASCADE,

    -- 수락 상태
    group_a_status VARCHAR(20) DEFAULT 'pending',
    group_b_status VARCHAR(20) DEFAULT 'pending',

    -- 최종 상태
    final_status VARCHAR(20) DEFAULT 'pending',

    -- 단체 메시지방
    chat_room_id UUID,

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours'),
    matched_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    UNIQUE(pool_id_a, pool_id_b)
);

CREATE INDEX idx_matching_proposals_status ON matching_proposals(final_status);
CREATE INDEX idx_matching_proposals_pool_a ON matching_proposals(pool_id_a);
CREATE INDEX idx_matching_proposals_pool_b ON matching_proposals(pool_id_b);
```

#### 4. matching_chat_rooms
```sql
CREATE TABLE matching_chat_rooms (
    room_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    proposal_id UUID UNIQUE REFERENCES matching_proposals(proposal_id) ON DELETE CASCADE,

    -- 방 정보
    room_name VARCHAR(200) NOT NULL,
    display_mode VARCHAR(10) NOT NULL, -- blind, open

    -- 그룹 정보 (JSON)
    group_a_info JSONB NOT NULL,
    group_b_info JSONB NOT NULL,

    -- 상태
    is_active BOOLEAN DEFAULT true,

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_matching_chat_rooms_proposal ON matching_chat_rooms(proposal_id);
CREATE INDEX idx_matching_chat_rooms_active ON matching_chat_rooms(is_active);
```

#### 5. matching_chat_members
```sql
CREATE TABLE matching_chat_members (
    member_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES matching_chat_rooms(room_id) ON DELETE CASCADE,
    user_id VARCHAR(36) REFERENCES "user"(id) ON DELETE CASCADE,

    -- 그룹 식별
    group_label VARCHAR(10) NOT NULL, -- A, B
    member_index INTEGER NOT NULL, -- 1, 2, 3...

    -- 익명 닉네임 (블라인드 모드)
    anonymous_name VARCHAR(20), -- A1, A2, B1, B2...

    -- 상태
    is_active BOOLEAN DEFAULT true,
    last_read_at TIMESTAMP,

    -- 타임스탬프
    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    left_at TIMESTAMP,

    UNIQUE(room_id, user_id)
);

CREATE INDEX idx_matching_chat_members_room ON matching_chat_members(room_id);
CREATE INDEX idx_matching_chat_members_user ON matching_chat_members(user_id);
```

#### 6. matching_messages
```sql
CREATE TABLE matching_messages (
    message_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID REFERENCES matching_chat_rooms(room_id) ON DELETE CASCADE,
    sender_id VARCHAR(36) REFERENCES "user"(id) ON DELETE CASCADE,

    -- 메시지 내용
    message_type VARCHAR(20) DEFAULT 'text', -- text, image, system
    content TEXT NOT NULL,

    -- 첨부 파일
    attachments TEXT[],

    -- 타임스탬프
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP
);

CREATE INDEX idx_matching_messages_room ON matching_messages(room_id);
CREATE INDEX idx_matching_messages_created ON matching_messages(created_at DESC);
```

## 🔄 매칭 알고리즘

### 알고리즘 로직

```python
async def find_matching_candidates(pool: MatchingPool) -> List[MatchingPool]:
    """
    매칭 후보 찾기
    """
    candidates = await db.query(MatchingPool).filter(
        # 필수 조건
        MatchingPool.status == 'waiting',
        MatchingPool.member_count == pool.member_count,
        MatchingPool.gender != pool.gender,  # 다른 성별
        MatchingPool.pool_id != pool.pool_id,  # 자기 자신 제외

        # 만료되지 않음
        MatchingPool.expires_at > datetime.now()
    ).all()

    # 선호도에 따라 필터링 및 정렬
    scored_candidates = []
    for candidate in candidates:
        score = calculate_match_score(pool, candidate)
        if score > 0:
            scored_candidates.append((candidate, score))

    # 점수 순으로 정렬
    scored_candidates.sort(key=lambda x: x[1], reverse=True)

    return [c[0] for c in scored_candidates]

def calculate_match_score(pool_a: MatchingPool, pool_b: MatchingPool) -> int:
    """
    매칭 점수 계산
    """
    score = 0

    # 학과 매칭
    if pool_a.preferred_match_type == 'same_department':
        if pool_a.department == pool_b.department:
            score += 100
        elif check_major_category_match(pool_a, pool_b):
            score += 50

    # 전공 계열 매칭
    elif pool_a.preferred_match_type == 'major_category':
        if check_major_category_match(pool_a, pool_b):
            score += 80

    # 무관
    else:
        score += 30

    # 상대방 선호도도 고려
    if pool_b.preferred_match_type == 'same_department':
        if pool_a.department == pool_b.department:
            score += 100
    elif pool_b.preferred_match_type == 'major_category':
        if check_major_category_match(pool_a, pool_b):
            score += 80
    else:
        score += 30

    return score
```

### 매칭 스케줄러

```python
# Celery Beat 스케줄러
@celery.task
async def run_matching_algorithm():
    """
    주기적으로 매칭 알고리즘 실행 (5분마다)
    """
    waiting_pools = await get_waiting_pools()

    for pool in waiting_pools:
        candidates = await find_matching_candidates(pool)

        if candidates:
            # 랜덤 선택 (공정성)
            selected = random.choice(candidates[:3])  # 상위 3개 중 랜덤

            # 매칭 제안 생성
            await create_matching_proposal(pool, selected)
```

## 🔔 알림 시스템

### 알림 타입

```typescript
enum NotificationType {
  MATCHING_PROPOSAL = 'matching_proposal',
  MATCHING_ACCEPTED = 'matching_accepted',
  MATCHING_REJECTED = 'matching_rejected',
  MATCHING_EXPIRED = 'matching_expired',
  NEW_MESSAGE = 'new_message',
}

interface Notification {
  id: string;
  userId: string;
  type: NotificationType;
  title: string;
  message: string;
  data: any; // 추가 데이터
  read: boolean;
  createdAt: Date;
}
```

### 알림 전송 채널

1. **In-App 알림**: 실시간 (WebSocket)
2. **푸시 알림**: FCM/APNS
3. **이메일**: 중요 알림만

## 🔐 보안 설계

### 데이터 암호화

```python
from cryptography.fernet import Fernet

class EncryptionService:
    def __init__(self, key: str):
        self.cipher = Fernet(key.encode())

    def encrypt_student_id(self, student_id: str) -> str:
        """학번 암호화"""
        return self.cipher.encrypt(student_id.encode()).decode()

    def decrypt_student_id(self, encrypted: str) -> str:
        """학번 복호화"""
        return self.cipher.decrypt(encrypted.encode()).decode()
```

### 접근 제어

```python
# 권한 데코레이터
@require_verified_user
async def create_matching_pool(user_id: str, data: dict):
    """인증된 사용자만 매칭 풀 생성 가능"""
    pass

@require_admin
async def review_verification(verification_id: str, approved: bool):
    """관리자만 인증 검토 가능"""
    pass
```

## 📊 성능 최적화

### 캐싱 전략

```python
# Redis 캐싱
@cache(ttl=300)  # 5분 캐시
async def get_user_verification(user_id: str):
    """사용자 인증 정보 캐싱"""
    return await db.query(UserVerification).filter_by(user_id=user_id).first()

@cache(ttl=60)  # 1분 캐시
async def get_waiting_pools_count():
    """대기 중인 풀 개수 캐싱"""
    return await db.query(MatchingPool).filter_by(status='waiting').count()
```

### 데이터베이스 최적화

```sql
-- 복합 인덱스
CREATE INDEX idx_matching_pools_composite
ON matching_pools(status, member_count, gender);

-- 부분 인덱스
CREATE INDEX idx_matching_pools_waiting
ON matching_pools(created_at)
WHERE status = 'waiting';
```

## 🧪 테스트 전략

### 단위 테스트
- 매칭 알고리즘 로직
- 암호화/복호화
- 권한 검증

### 통합 테스트
- API 엔드포인트
- 데이터베이스 트랜잭션
- WebSocket 연결

### E2E 테스트
- 전체 매칭 프로세스
- 메시지 전송/수신
- 알림 전송

---

**문서 승인**: 대기 중
**다음 단계**: API 명세서 작성 (ARCH-008)
