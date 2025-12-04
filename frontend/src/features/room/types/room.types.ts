/**
 * Room Feature 타입 정의
 */

export interface Room {
  room_id: string;
  room_name: string;
  work_duration: number; // seconds
  break_duration: number; // seconds
  auto_start_break?: boolean;
  current_participants?: number;
  max_participants?: number;
  timer_state?: TimerState;
  created_at: string;
}

export interface TimerState {
  status: "idle" | "running" | "paused" | "completed";
  session_type: "work" | "break";
  remaining_seconds: number;
  target_timestamp?: string;
  started_at?: string;
}

export interface CreateRoomRequest {
  room_name: string;
  work_duration_minutes: number;
  break_duration_minutes: number;
  auto_start_break?: boolean;
}

export interface UpdateRoomSettingsRequest {
  work_duration_minutes?: number;
  break_duration_minutes?: number;
  auto_start_break?: boolean;
}
