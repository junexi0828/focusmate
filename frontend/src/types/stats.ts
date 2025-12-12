/**
 * 통계 계산용 세션 레코드 (프론트엔드 내부 사용)
 * 변환 유틸리티를 통해 백엔드 응답에서 생성됩니다.
 */
export interface SessionRecord {
  id: string;
  date: Date;
  duration: number; // in minutes
  type: "focus" | "break";
  completed: boolean;
  roomName?: string;
}

export interface DailyStats {
  date: string;
  focusTime: number; // in minutes
  breakTime: number; // in minutes
  sessions: number;
}

export interface WeeklyStats {
  week: string;
  focusTime: number;
  breakTime: number;
  sessions: number;
}

export interface MonthlyStats {
  month: string;
  focusTime: number;
  breakTime: number;
  sessions: number;
}

export type StatsTimeRange = "daily" | "weekly" | "monthly";
