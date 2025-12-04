/**
 * Room 관련 타입 정의
 */

export interface RoomData {
  roomId: string;
  roomName: string;
  focusTime: number; // minutes
  breakTime: number; // minutes
  autoStartBreak?: boolean;
}

export interface ParticipantData {
  id: string;
  name: string;
  isHost: boolean;
  joinedAt?: string;
}

export interface TimerStatus {
  status: 'idle' | 'running' | 'paused' | 'completed';
  sessionType: 'focus' | 'break';
  remainingSeconds: number;
  totalSeconds: number;
}

