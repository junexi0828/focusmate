/**
 * Chat Invitation Service
 * Handles room invitation codes
 */

import { api } from "../../../api/client";
import type { ApiResponse } from "../../../types/api";

export interface InvitationCodeInfo {
  code: string;
  room_id: string;
  expires_at: string | null;
  max_uses: number | null;
  current_uses: number;
  is_valid: boolean;
}

export interface InvitationCodeCreate {
  expires_hours?: number;
  max_uses?: number;
}

export interface ChatRoom {
  room_id: string;
  room_type: string;
  room_name: string | null;
  description: string | null;
  invitation_code: string | null;
  created_at: string;
}

export interface FriendRoomCreate {
  friend_ids: string[];
  room_name?: string;
  description?: string;
  generate_invitation?: boolean;
  invitation_expires_hours?: number;
}

class InvitationService {
  /**
   * Generate invitation code for a room
   */
  async generateInvitation(
    roomId: string,
    data: InvitationCodeCreate
  ): Promise<ApiResponse<InvitationCodeInfo>> {
    try {
      const response = await api.post<InvitationCodeInfo>(`/chats/rooms/${roomId}/invitation`, data);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "초대 코드 생성 실패",
        },
      };
    }
  }

  /**
   * Get invitation code information
   */
  async getInvitationInfo(code: string): Promise<ApiResponse<InvitationCodeInfo>> {
    try {
      const response = await api.get<InvitationCodeInfo>(`/chats/invitations/${code}`);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "초대 코드 정보 불러오기 실패",
        },
      };
    }
  }

  /**
   * Join room by invitation code
   */
  async joinByInvitation(code: string): Promise<ApiResponse<ChatRoom>> {
    try {
      const response = await api.post<ChatRoom>("/chats/rooms/join", {
        invitation_code: code,
      });
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "방 참가 실패",
        },
      };
    }
  }

  /**
   * Create room with friends
   */
  async createRoomWithFriends(data: FriendRoomCreate): Promise<ApiResponse<ChatRoom>> {
    try {
      const response = await api.post<ChatRoom>("/chats/rooms/friends", data);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "친구와 방 생성 실패",
        },
      };
    }
  }
}

export const invitationService = new InvitationService();
