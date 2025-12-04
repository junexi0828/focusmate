/**
 * Participants Feature 타입 정의
 */

export interface Participant {
  participant_id: string;
  room_id: string;
  name: string;
  is_host: boolean;
  joined_at: string;
}

export interface JoinRoomRequest {
  participant_name: string;
}

