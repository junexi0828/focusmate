/**
 * Messaging Service
 * Handles 1:1 messaging and conversations
 */

import { api } from "../../../api/client";
import type { ApiResponse } from "../../../types/api";

export interface Conversation {
  id: string;
  user1_id: string;
  user2_id: string;
  last_message_at: string | null;
  user1_unread_count: number;
  user2_unread_count: number;
  created_at: string;
  updated_at: string;

  // Additional fields from API
  other_user_id?: string;
  other_user_username?: string;
  other_user_profile_image?: string | null;
  last_message_content?: string | null;
  last_message_sender_id?: string | null;
}

export interface Message {
  id: string;
  conversation_id: string;
  sender_id: string;
  receiver_id: string;
  content: string;
  is_read: boolean;
  read_at: string | null;
  created_at: string;
  updated_at: string;

  // Additional fields
  sender_username?: string;
  receiver_username?: string;
}

export interface ConversationDetailResponse {
  conversation: Conversation;
  messages: Message[];
  total_messages: number;
  has_more: boolean;
}

export interface SendMessageRequest {
  receiver_id: string;
  content: string;
}

class MessagingService {
  /**
   * Send a message to another user
   */
  async sendMessage(senderId: string, data: SendMessageRequest): Promise<ApiResponse<Message>> {
    try {
      const response = await api.post<Message>(`/messages/send?sender_id=${senderId}`, data);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "메시지 전송에 실패했습니다",
        },
      };
    }
  }

  /**
   * Get all conversations for a user
   */
  async getConversations(userId: string): Promise<ApiResponse<Conversation[]>> {
    try {
      const response = await api.get<Conversation[]>(`/messages/conversations?user_id=${userId}`);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "대화 목록 불러오기 실패",
        },
      };
    }
  }

  /**
   * Get conversation details with messages
   */
  async getConversationDetail(
    conversationId: string,
    userId: string,
    limit: number = 50,
    offset: number = 0
  ): Promise<ApiResponse<ConversationDetailResponse>> {
    try {
      const response = await api.get<ConversationDetailResponse>(
        `/messages/conversations/${conversationId}?user_id=${userId}&limit=${limit}&offset=${offset}`
      );
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "대화 내용 불러오기 실패",
        },
      };
    }
  }

  /**
   * Mark messages as read
   */
  async markMessagesAsRead(
    conversationId: string,
    userId: string,
    messageIds: string[]
  ): Promise<ApiResponse<{ marked_count: number; new_unread_count: number }>> {
    try {
      const response = await api.post<{ marked_count: number; new_unread_count: number }>(
        `/messages/conversations/${conversationId}/read?user_id=${userId}`,
        { message_ids: messageIds }
      );
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "읽음 처리 실패",
        },
      };
    }
  }

  /**
   * Get total unread message count
   */
  async getUnreadCount(userId: string): Promise<ApiResponse<{ user_id: string; unread_count: number }>> {
    try {
      const response = await api.get<{ user_id: string; unread_count: number }>(
        `/messages/unread-count?user_id=${userId}`
      );
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          code: error.response?.status || 500,
          message: error.response?.data?.detail || "읽지 않은 메시지 수 불러오기 실패",
        },
      };
    }
  }
}

export const messagingService = new MessagingService();
