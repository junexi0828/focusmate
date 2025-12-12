/**
 * API Response Transformers
 *
 * 백엔드의 snake_case 컨벤션을 프론트엔드의 camelCase로 변환하는 유틸리티 함수들
 * PostgreSQL의 snake_case와 TypeScript의 camelCase 간 변환을 처리합니다.
 */

// 백엔드 응답 타입 (snake_case)
export interface SessionRecordResponse {
  session_id: string;
  user_id: string;
  room_id: string;
  session_type: 'work' | 'break';
  duration_minutes: number;
  completed_at: string;
  room_name?: string | null;
}

// 프론트엔드 타입 (camelCase)
export interface SessionRecord {
  sessionId: string;
  userId: string;
  roomId: string;
  sessionType: 'work' | 'break';
  durationMinutes: number;
  completedAt: string;
  roomName?: string | null;
}

/**
 * 백엔드 세션 레코드를 프론트엔드 형식으로 변환
 */
export function transformSessionRecord(response: SessionRecordResponse): SessionRecord {
  return {
    sessionId: response.session_id,
    userId: response.user_id,
    roomId: response.room_id,
    sessionType: response.session_type,
    durationMinutes: response.duration_minutes,
    completedAt: response.completed_at,
    roomName: response.room_name ?? undefined,
  };
}

/**
 * 세션 레코드 배열 변환
 */
export function transformSessionRecords(responses: SessionRecordResponse[]): SessionRecord[] {
  return responses.map(transformSessionRecord);
}

/**
 * UserStatsResponse 변환
 */
export interface UserStatsResponseBackend {
  total_focus_time: number;
  total_sessions: number;
  average_session: number;
  sessions: SessionRecordResponse[];
}

export interface UserStatsResponseFrontend {
  totalFocusTime: number;
  totalSessions: number;
  averageSession: number;
  sessions: SessionRecord[];
}

export function transformUserStatsResponse(
  response: UserStatsResponseBackend
): UserStatsResponseFrontend {
  return {
    totalFocusTime: response.total_focus_time,
    totalSessions: response.total_sessions,
    averageSession: response.average_session,
    sessions: transformSessionRecords(response.sessions),
  };
}

/**
 * SessionRecord를 프론트엔드 내부 사용 형식으로 변환
 * (통계 계산용 - date를 Date 객체로 변환)
 */
export interface SessionRecordForStats {
  id: string;
  date: Date;
  duration: number; // in minutes
  type: 'focus' | 'break';
  completed: boolean;
  roomName?: string;
}

/**
 * SessionRecord를 통계 계산용 형식으로 변환
 */
export function transformSessionRecordForStats(record: SessionRecord): SessionRecordForStats {
  return {
    id: record.sessionId,
    date: new Date(record.completedAt),
    duration: record.durationMinutes,
    type: record.sessionType === 'work' ? 'focus' : 'break',
    completed: true,
    roomName: record.roomName ?? undefined,
  };
}

/**
 * SessionRecord 배열을 통계 계산용 형식으로 변환
 */
export function transformSessionRecordsForStats(records: SessionRecord[]): SessionRecordForStats[] {
  return records.map(transformSessionRecordForStats);
}

