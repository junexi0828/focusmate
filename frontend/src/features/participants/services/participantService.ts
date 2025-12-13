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
    // Backend endpoint: POST /api/v1/participants/{room_id}/join
    return this.request(`/participants/${roomId}/join`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getParticipants(roomId: string): Promise<ApiResponse<Participant[]>> {
    // Backend endpoint: GET /api/v1/participants/{room_id}
    // Backend returns: { participants: ParticipantResponse[], total: int }
    const response = await this.request<{ participants: Participant[]; total: number }>(`/participants/${roomId}`);
    // Extract participants array from response
    if (response.status === "success" && response.data) {
      return {
        ...response,
        data: response.data.participants,
      };
    }
    return response as ApiResponse<Participant[]>;
  }

  async leaveRoom(
    _roomId: string,
    participantId: string
  ): Promise<ApiResponse<void>> {
    // Backend endpoint: DELETE /api/v1/participants/{participant_id}
    return this.request(`/participants/${participantId}`, {
      method: "DELETE",
    });
  }
}

export const participantService = new ParticipantService();

