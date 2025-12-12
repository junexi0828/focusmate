/**
 * Participants Feature 타입 정의
 */

export interface Participant {
  id: string; // Backend returns 'id'
  participant_id?: string; // Keep for backward compatibility
  room_id: string;
  username: string; // Backend returns 'username'
  name?: string; // Keep for backward compatibility (use username if not available)
  is_host: boolean;
  joined_at: string;
  // Optional fields from backend
  user_id?: string | null;
  is_connected?: boolean;
  left_at?: string | null;
}

export interface JoinRoomRequest {
  username: string; // Backend expects 'username'
}

