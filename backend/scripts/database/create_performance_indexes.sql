-- 성능 최적화를 위한 인덱스 생성 스크립트
-- 실행 방법: psql 또는 데이터베이스 클라이언트에서 실행

-- 1. 랭킹 세션 조회 성능 향상
CREATE INDEX IF NOT EXISTS idx_ranking_sessions_team_completed
ON ranking_sessions (team_id, completed_at DESC);

-- 2. 미니게임 점수 집계 성능 향상
CREATE INDEX IF NOT EXISTS idx_ranking_mini_games_team_played
ON ranking_mini_games (team_id, played_at DESC);

-- 3. 사용자 통계 조회 성능 향상
CREATE INDEX IF NOT EXISTS idx_session_history_user_completed
ON session_history (user_id, completed_at DESC);

-- 4. 채팅 메시지 조회 성능 향상
CREATE INDEX IF NOT EXISTS idx_chat_messages_room_created
ON chat_messages (room_id, created_at DESC);

-- 인덱스 생성 확인
SELECT
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

