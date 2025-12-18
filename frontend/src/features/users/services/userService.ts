/**
 * User Service
 * Handles user search and profile operations
 */

import { api } from "../../../api/client";
import type { ApiResponse } from "../../../types/api";

export interface UserSearchResult {
  id: string;
  username: string;
  email: string;
  bio: string | null;
  profile_image: string | null;
}

export interface UserSearchResponse {
  users: UserSearchResult[];
  total: number;
}

export interface UserProfile {
  id: string;
  username: string;
  email: string;
  bio: string | null;
  school: string | null;
  profile_image: string | null;
  is_verified: boolean;
  total_focus_time: number;
  total_sessions: number;
}

class UserService {
  /**
   * Search users by username or email
   */
  async searchUsers(query: string, limit: number = 10): Promise<ApiResponse<UserSearchResponse>> {
    try {
      const response = await api.get<UserSearchResponse>("/users/search", {
        params: { query, limit },
      });
      return { status: "success", data: response.data };
    } catch (error: any) {
      // Handle FastAPI validation errors
      let errorMessage = "사용자 검색 실패";

      if (error.response?.data?.detail) {
        const detail = error.response.data.detail;
        // If detail is an array (validation errors), extract messages
        if (Array.isArray(detail)) {
          errorMessage = detail.map((err: any) => err.msg || err.message).join(", ");
        } else if (typeof detail === 'string') {
          errorMessage = detail;
        }
      }

      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: errorMessage,
        },
      };
    }
  }

  /**
   * Get current user's profile with ID
   */
  async getMyProfile(): Promise<ApiResponse<UserProfile>> {
    try {
      const response = await api.get<UserProfile>("/users/me");
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "프로필 조회 실패",
        },
      };
    }
  }
}

export const userService = new UserService();
