/**
 * Room Reservation Feature 타입 정의
 */

export type RecurrenceType = "none" | "daily" | "weekly" | "monthly";

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
  recurrence_type?: string | null;
  recurrence_end_date?: string | null;
  notification_minutes?: number;
  notification_sent?: boolean;
  created_at: string;
  updated_at: string;
}

export interface CreateRoomReservationRequest {
  scheduled_at: string; // ISO datetime string
  work_duration: number; // seconds
  break_duration: number; // seconds
  description?: string | null;
  recurrence_type?: RecurrenceType;
  recurrence_end_date?: string | null;
  notification_minutes?: number;
}

export interface UpdateRoomReservationRequest {
  scheduled_at?: string; // ISO datetime string
  work_duration?: number; // seconds
  break_duration?: number; // seconds
  description?: string | null;
}

