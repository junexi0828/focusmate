/**
 * Timer Feature 타입 정의
 */

export interface TimerState {
  status: "idle" | "running" | "paused" | "completed";
  session_type: "work" | "break";
  remaining_seconds: number;
  target_timestamp?: string;
  started_at?: string;
}

export type SessionType = "work" | "break";

