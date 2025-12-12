랭킹전 시스템 구현 계획서
프로젝트 개요
목표: 팀 기반 경쟁 시스템 구축
예상 기간: 11주
팀 구성: Backend 2명, Frontend 2명, Designer 1명

구현 단계
Phase 1: 기본 팀 시스템 (2주)
Backend 작업
데이터베이스 스키마 생성

ranking_teams 테이블
ranking_team_members 테이블
ranking_team_invitations 테이블 (추가)
팀 관리 API 구현

POST /api/ranking/teams - 팀 생성
GET /api/ranking/teams/{team_id} - 팀 조회
PATCH /api/ranking/teams/{team_id} - 팀 수정
DELETE /api/ranking/teams/{team_id} - 팀 삭제
팀원 관리 API 구현

POST /api/ranking/teams/{team_id}/invite - 초대 발송
POST /api/ranking/teams/invitations/{id}/accept - 초대 수락
POST /api/ranking/teams/invitations/{id}/reject - 초대 거절
DELETE /api/ranking/teams/{team_id}/members/{user_id} - 팀원 제명
POST /api/ranking/teams/{team_id}/leave - 팀 탈퇴
이메일 알림 시스템

초대 이메일 템플릿
수락/거절 알림
Frontend 작업
팀 생성 페이지

팀명 입력
소속 선택 (일반/학과/연구실/동아리)
미니게임 참여 설정
팀 관리 페이지

팀 정보 표시
팀원 목록
초대 코드 생성/공유
이메일 초대 폼
팀원 초대 UI

초대 링크 복사
이메일 입력 폼
초대 상태 표시
내 팀 대시보드

팀 기본 정보 카드
팀원 리스트
간단한 통계
검증 항목
4명 미만 팀 생성 방지
중복 초대 방지
팀장 권한 검증
초대 만료 처리 (7일)
Phase 2: 학교 인증 시스템 (1주)
Backend 작업
인증 요청 테이블

ranking_verification_requests 생성
인증 API 구현

POST /api/ranking/verification/request - 인증 요청
GET /api/ranking/verification/status/{team_id} - 상태 조회
파일 업로드 처리

S3/Cloud Storage 연동
이미지 검증 (형식, 크기)
보안 처리
관리자 API

GET /api/admin/ranking/verification/requests - 요청 목록
POST /api/admin/ranking/verification/{id}/review - 승인/반려
Frontend 작업
인증 신청 페이지

서류 업로드 UI
팀원 명단 입력
진행 상태 표시
관리자 페이지

인증 요청 목록
서류 미리보기
승인/반려 버튼
메모 작성
인증 상태 표시

대기/승인/반려 뱃지
알림 메시지
검증 항목
파일 크기 제한 (10MB)
허용 파일 형식 (JPG, PNG, PDF)
관리자 권한 검증
인증 상태 변경 로그
Phase 3: 랭킹전 세션 시스템 (2주)
Backend 작업
세션 테이블

ranking_sessions 생성
인덱스 최적화
세션 API 구현

POST /api/ranking/sessions/start - 세션 시작
POST /api/ranking/sessions/{id}/complete - 세션 완료
GET /api/ranking/teams/{team_id}/sessions/stats - 통계 조회
통계 계산 로직

팀 총 집중 시간
일일/주간/월간 집계
평균 계산
연속 성공 계산

일일 목표 달성 여부
연속 일수 계산
스트릭 초기화 로직
Frontend 작업
랭킹전 세션 UI

세션 시작 버튼
타이머 표시
팀 통계 실시간 업데이트
팀 통계 대시보드

총 집중 시간 차트
팀원별 기여도
일일 목표 진행률
연속 성공 표시

스트릭 카운터 (🔥)
연속 일수 그래프
목표 달성 체크리스트
검증 항목
동시 세션 방지
세션 시간 검증
통계 정확성 테스트
연속 성공 로직 검증
Phase 4: 미니게임 시스템 (3주)
Backend 작업
게임 테이블

ranking_mini_games 생성
mini_game_questions 테이블 (퀴즈용)
게임 API 구현

POST /api/ranking/mini-games/start - 게임 시작
POST /api/ranking/mini-games/{id}/submit - 답안 제출
GET /api/ranking/teams/{team_id}/mini-games - 기록 조회
게임 로직

퀴즈 문제 랜덤 선택
정답 검증
점수 계산 (기본 + 보너스)
시간 초과 처리
부정 방지

서버 사이드 검증
중복 제출 방지
이상 패턴 감지
Frontend 작업
퀴즈 게임

문제 표시
선택지 버튼
타이머 (30초)
결과 화면
반응속도 게임

아이콘 랜덤 표시
클릭 시간 측정
점수 계산
기억력 게임

카드 뒤집기
짝 맞추기
제한 시간
게임 결과 UI

점수 표시
순위 변동
팀 총점 업데이트
검증 항목
게임 타이밍 정확성
점수 계산 검증
중복 참여 방지
부정 행위 감지
Phase 5: 명예의 전당 (2주)
Backend 작업
리더보드 테이블

ranking_leaderboard 생성
캐싱 전략 (Redis)
리더보드 API

GET /api/ranking/leaderboard/study-time - 순공부시간
GET /api/ranking/leaderboard/streak - 연속 성공
GET /api/ranking/leaderboard/mini-game - 미니게임
GET /api/ranking/teams/{team_id}/rank - 내 팀 순위
순위 계산 로직

주간/월간/전체 집계
순위 변동 추적
자동 업데이트 (Cron Job)
WebSocket 구현

실시간 순위 업데이트
팀 활동 알림
순위 변동 알림
Frontend 작업
명예의 전당 페이지

3개 탭 (순공부시간/연속성공/미니게임)
기간 필터 (주간/월간/전체)
순위 리스트
리더보드 UI

1-3위 특별 표시 (🥇🥈🥉)
팀 정보 카드
순위 변동 표시 (↑↓)
내 팀 하이라이트
실시간 업데이트

WebSocket 연결
순위 변동 애니메이션
알림 토스트
검증 항목
순위 계산 정확성
실시간 업데이트 성능
대량 데이터 처리
캐싱 효율성
Phase 6: 최적화 및 테스트 (1주)
Backend 작업
성능 최적화

쿼리 최적화
인덱스 추가
N+1 문제 해결
캐싱 전략

Redis 캐싱
리더보드 캐시
통계 캐시
부하 테스트

동시 접속 테스트
API 응답 시간 측정
병목 지점 파악
Frontend 작업
성능 최적화

코드 스플리팅
이미지 최적화
번들 크기 감소
사용자 경험 개선

로딩 스켈레톤
에러 처리
오프라인 지원
테스트
단위 테스트

팀 생성/수정/삭제
세션 기록
게임 로직
순위 계산
통합 테스트

전체 플로우
API 연동
WebSocket 통신
E2E 테스트

팀 생성부터 랭킹 진입까지
미니게임 참여
순위 확인
기술 스택
Backend
FastAPI: REST API 프레임워크
PostgreSQL: 메인 데이터베이스
Redis: 캐싱 및 실시간 데이터
Socket.io: WebSocket 통신
Celery: 비동기 작업 (통계 계산)
AWS S3: 파일 저장소
Frontend
React 18: UI 프레임워크
TanStack Query: 데이터 페칭
Socket.io Client: 실시간 통신
Recharts: 통계 차트
Framer Motion: 애니메이션
일정표
주차 Phase 주요 작업
1-2 Phase 1 팀 시스템 구축
3 Phase 2 학교 인증
4-5 Phase 3 세션 시스템
6-8 Phase 4 미니게임
9-10 Phase 5 명예의 전당
11 Phase 6 최적화 및 테스트
리스크 관리
기술적 리스크
실시간 업데이트 성능

완화: Redis 캐싱, WebSocket 최적화
대량 데이터 처리

완화: 인덱싱, 파티셔닝, 배치 처리
게임 부정 행위

완화: 서버 검증, 이상 패턴 감지
일정 리스크
미니게임 개발 지연

완화: 게임 유형 우선순위 설정
인증 시스템 복잡도

완화: MVP 먼저 구현, 점진적 개선
성공 지표
개발 완료 기준
모든 API 엔드포인트 구현
단위 테스트 커버리지 80% 이상
E2E 테스트 통과
성능 기준 충족 (API 응답 < 200ms)
사용자 지표
팀 생성 수 > 50개 (첫 달)
일일 활성 팀 > 30개
미니게임 참여율 > 60%
평균 세션 시간 증가 > 20%
작성일: 2025-01-12
버전: 1.0
