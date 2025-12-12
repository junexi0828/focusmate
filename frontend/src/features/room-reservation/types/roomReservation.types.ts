/**
 * Room Reservation Feature 타입 정의
 */

export interface RoomReservation {
  id: string;
  room_id: string | null;
  user_id: string;
  scheduled_at: string; // ISO datetime string
  work_duration: number; // seconds
  break_duration: number; // seconds
  description: string | null;
  is_active: boolean;
  is_completed: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateRoomReservationRequest {
  scheduled_at: string; // ISO datetime string
  work_duration: number; // seconds
  break_duration: number; // seconds
  description?: string | null;
}

export interface UpdateRoomReservationRequest {
  scheduled_at?: string; // ISO datetime string
  work_duration?: number; // seconds
  break_duration?: number; // seconds
  description?: string | null;
}

