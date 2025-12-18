/**
 * FastAPI 백엔드와 통신하는 API 클라이언트
 * @deprecated 이 파일은 호환성을 위해 유지됩니다.
 * 새로운 코드는 features/*/services/* 를 사용하세요.
 */

// Re-export from features for backward compatibility
export { roomService as apiClient } from "../features/room/services/roomService";
export { roomService } from "../features/room/services/roomService";
export { timerService } from "../features/timer/services/timerService";
export { participantService } from "../features/participants/services/participantService";

// Re-export types
export type { Room, TimerState, CreateRoomRequest } from "../features/room/types/room.types";
export type { Participant, JoinRoomRequest } from "../features/participants/types/participant.types";
export type { ApiResponse } from "./api/base";

// Legacy ApiClient class for backward compatibility
import { BaseApiClient, ApiResponse } from "./api/base";
import { Room, CreateRoomRequest, UpdateRoomSettingsRequest } from "../features/room/types/room.types";
import { TimerState } from "../features/timer/types/timer.types";
import { Participant, JoinRoomRequest } from "../features/participants/types/participant.types";

class ApiClient extends BaseApiClient {
  // Room Management
  async createRoom(data: CreateRoomRequest): Promise<ApiResponse<Room>> {
    return this.request("/rooms", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getRoom(roomId: string): Promise<ApiResponse<Room>> {
    return this.request(`/rooms/${roomId}`);
  }

  async deleteRoom(roomId: string): Promise<ApiResponse<void>> {
    return this.request(`/rooms/${roomId}`, {
      method: "DELETE",
    });
  }

  // Participant Management
  async joinRoom(
    roomId: string,
    data: JoinRoomRequest
  ): Promise<ApiResponse<Participant>> {
    return this.request(`/rooms/${roomId}/participants`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getParticipants(roomId: string): Promise<ApiResponse<Participant[]>> {
    return this.request(`/rooms/${roomId}/participants`);
  }

  async leaveRoom(
    roomId: string,
    participantId: string
  ): Promise<ApiResponse<void>> {
    return this.request(`/rooms/${roomId}/participants/${participantId}`, {
      method: "DELETE",
    });
  }

  // Timer Control
  async startTimer(
    roomId: string,
    sessionType: "work" | "break" = "work"
  ): Promise<ApiResponse<TimerState>> {
    return this.request(`/rooms/${roomId}/timer/start`, {
      method: "POST",
      body: JSON.stringify({ session_type: sessionType }),
    });
  }

  async pauseTimer(roomId: string): Promise<ApiResponse<TimerState>> {
    return this.request(`/rooms/${roomId}/timer/pause`, {
      method: "POST",
    });
  }

  async resumeTimer(roomId: string): Promise<ApiResponse<TimerState>> {
    return this.request(`/rooms/${roomId}/timer/resume`, {
      method: "POST",
    });
  }

  async resetTimer(roomId: string): Promise<ApiResponse<TimerState>> {
    return this.request(`/rooms/${roomId}/timer/reset`, {
      method: "POST",
    });
  }

  // Room Settings
  async updateRoomSettings(
    roomId: string,
    data: UpdateRoomSettingsRequest
  ): Promise<ApiResponse<Room>> {
    return this.request(`/rooms/${roomId}`, {
      method: "PATCH",
      body: JSON.stringify(data),
    });
  }
}

export const apiClient = new ApiClient();
