/**
 * Chat API client functions
 */

import { api } from "./client";
import type {
  ChatRoom,
  ChatMessage,
  DirectChatCreate,
  TeamChatCreate,
  MessageCreate,
} from "@/types/chat";

// Get unread message count
export const getUnreadMessageCount = async (): Promise<number> => {
  const response = await api.get("/chats/unread-count");
  return response.data.count;
};

export const chatApi = {
  // Room operations
  getRooms: async (roomType?: string) => {
    const params = roomType ? { room_type: roomType } : {};
    const response = await api.get<{ rooms: ChatRoom[]; total: number }>(
      "/chats/rooms",
      { params }
    );
    return response.data;
  },

  getRoom: async (roomId: string) => {
    const response = await api.get<ChatRoom>(`/chats/rooms/${roomId}`);
    return response.data;
  },

  createDirectChat: async (data: DirectChatCreate) => {
    const response = await api.post<ChatRoom>("/chats/rooms/direct", data);
    return response.data;
  },

  createTeamChat: async (data: TeamChatCreate) => {
    const response = await api.post<ChatRoom>("/chats/rooms/team", data);
    return response.data;
  },

  // Message operations
  getMessages: async (
    roomId: string,
    limit: number = 50,
    beforeMessageId?: string
  ) => {
    const params: any = { limit };
    if (beforeMessageId) {
      params.before_message_id = beforeMessageId;
    }
    const response = await api.get<{
      messages: ChatMessage[];
      total: number;
      has_more: boolean;
    }>(`/chats/rooms/${roomId}/messages`, { params });
    return response.data;
  },

  sendMessage: async (roomId: string, data: MessageCreate) => {
    const response = await api.post<ChatMessage>(
      `/chats/rooms/${roomId}/messages`,
      data
    );
    return response.data;
  },

  updateMessage: async (roomId: string, messageId: string, content: string) => {
    const response = await api.patch<ChatMessage>(
      `/chats/rooms/${roomId}/messages/${messageId}`,
      { content }
    );
    return response.data;
  },

  deleteMessage: async (roomId: string, messageId: string) => {
    const response = await api.delete<ChatMessage>(
      `/chats/rooms/${roomId}/messages/${messageId}`
    );
    return response.data;
  },

  markAsRead: async (roomId: string) => {
    const response = await api.post(`/chats/rooms/${roomId}/read`);
    return response.data;
  },
};
