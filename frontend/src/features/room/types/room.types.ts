/**
 * Room Feature 타입 정의
 */

export interface Room {
  id: string; // 백엔드 응답은 'id'를 사용
  name: string; // 백엔드 응답은 'name'을 사용
  work_duration: number; // minutes (백엔드에서 분 단위로 저장/반환)
  break_duration: number; // minutes (백엔드에서 분 단위로 저장/반환)
  auto_start_break: boolean;
  is_active: boolean;
  host_id?: string | null;
  remove_on_leave?: boolean; // If true, participants are removed from room list when they leave
  created_at: string;
  updated_at?: string;
  // 하위 호환성을 위한 필드
  room_id?: string; // id의 별칭
  room_name?: string; // name의 별칭
  current_participants?: number;
  max_participants?: number;
  timer_state?: TimerState;
}

export interface TimerState {
  status: "idle" | "running" | "paused" | "completed";
  session_type: "work" | "break";
  remaining_seconds: number;
  target_timestamp?: string;
  started_at?: string;
}

export interface CreateRoomRequest {
  name: string; // 백엔드 API 스펙에 맞춤
  work_duration: number; // 초 단위 (백엔드 API 스펙)
  break_duration: number; // 초 단위 (백엔드 API 스펙)
  auto_start_break?: boolean;
  remove_on_leave?: boolean; // If true, participants are removed from room list when they leave
}

export interface UpdateRoomSettingsRequest {
  work_duration?: number; // 초 단위 (백엔드 API 스펙)
  break_duration?: number; // 초 단위 (백엔드 API 스펙)
  auto_start_break?: boolean;
  remove_on_leave?: boolean; // If true, participants are removed from room list when they leave
}
