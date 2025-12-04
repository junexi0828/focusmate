/**
 * Participants Feature API Service
 * 참여자 관리 관련 API 호출 담당
 */

import { BaseApiClient, ApiResponse } from "../../../lib/api/base";
import { Participant, JoinRoomRequest } from "../types/participant.types";

class ParticipantService extends BaseApiClient {
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
}

export const participantService = new ParticipantService();

