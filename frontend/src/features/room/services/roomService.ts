/**
 * Room Feature API Service
 * 방 생성, 조회, 설정 업데이트 등의 API 호출 담당
 */

import { BaseApiClient, ApiResponse } from "../../../lib/api/base";
import {
  Room,
  CreateRoomRequest,
  UpdateRoomSettingsRequest,
} from "../types/room.types";

class RoomService extends BaseApiClient {
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

export const roomService = new RoomService();
