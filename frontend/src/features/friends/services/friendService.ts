/**
 * Friend Service
 * Handles friend-related API calls
 */

import { api } from "../../../api/client";
import type { ApiResponse } from "../../../types/api";

export interface FriendRequest {
  id: string;
  sender_id: string;
  receiver_id: string;
  status: "pending" | "accepted" | "rejected";
  created_at: string;
  responded_at: string | null;
  sender_username?: string;
  sender_profile_image?: string | null;
  receiver_username?: string;
  receiver_profile_image?: string | null;
}

export interface Friend {
  id: string;
  user_id: string;
  friend_id: string;
  created_at: string;
  is_blocked: boolean;
  friend_username: string;
  friend_email?: string | null;
  friend_profile_image?: string | null;
  friend_bio?: string | null;
  friend_is_online: boolean;
}

export interface FriendListResponse {
  friends: Friend[];
  total: number;
}

class FriendService {
  /**
   * Send a friend request
   */
  async sendFriendRequest(receiverId: string): Promise<ApiResponse<FriendRequest>> {
    try {
      const response = await api.post<FriendRequest>("/friends/requests", {
        receiver_id: receiverId,
      });
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "친구 요청 전송에 실패했습니다",
        },
      };
    }
  }

  /**
   * Get received friend requests
   */
  async getReceivedRequests(pendingOnly: boolean = false): Promise<ApiResponse<FriendRequest[]>> {
    try {
      const response = await api.get<FriendRequest[]>("/friends/requests/received", {
        params: { pending_only: pendingOnly },
      });
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "친구 요청 목록 불러오기 실패",
        },
      };
    }
  }

  /**
   * Get sent friend requests
   */
  async getSentRequests(): Promise<ApiResponse<FriendRequest[]>> {
    try {
      const response = await api.get<FriendRequest[]>("/friends/requests/sent");
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "보낸 친구 요청 목록 불러오기 실패",
        },
      };
    }
  }

  /**
   * Accept a friend request
   */
  async acceptFriendRequest(requestId: string): Promise<ApiResponse<FriendRequest>> {
    try {
      const response = await api.post<FriendRequest>(`/friends/requests/${requestId}/accept`);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "친구 요청 수락에 실패했습니다",
        },
      };
    }
  }

  /**
   * Reject a friend request
   */
  async rejectFriendRequest(requestId: string): Promise<ApiResponse<FriendRequest>> {
    try {
      const response = await api.post<FriendRequest>(`/friends/requests/${requestId}/reject`);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "친구 요청 거절에 실패했습니다",
        },
      };
    }
  }

  /**
   * Cancel a sent friend request
   */
  async cancelFriendRequest(requestId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await api.delete<{ message: string }>(`/friends/requests/${requestId}`);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "친구 요청 취소에 실패했습니다",
        },
      };
    }
  }

  /**
   * Get friends list
   */
  async getFriends(): Promise<ApiResponse<FriendListResponse>> {
    try {
      const response = await api.get<FriendListResponse>("/friends/");
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "친구 목록 불러오기 실패",
        },
      };
    }
  }

  /**
   * Remove a friend
   */
  async removeFriend(friendId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await api.delete<{ message: string }>(`/friends/${friendId}`);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "친구 삭제에 실패했습니다",
        },
      };
    }
  }

  /**
   * Block a friend
   */
  async blockFriend(friendId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await api.post<{ message: string }>(`/friends/${friendId}/block`);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "친구 차단에 실패했습니다",
        },
      };
    }
  }

  /**
   * Unblock a friend
   */
  async unblockFriend(friendId: string): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await api.post<{ message: string }>(`/friends/${friendId}/unblock`);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "친구 차단 해제에 실패했습니다",
        },
      };
    }
  }
}

export const friendService = new FriendService();
