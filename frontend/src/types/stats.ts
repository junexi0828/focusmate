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
