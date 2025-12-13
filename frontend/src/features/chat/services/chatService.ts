import { BaseApiClient, ApiResponse } from "../../../lib/api/base";

export interface ChatRoom {
  room_id: string;
  room_type: "direct" | "team" | "matching";
  room_name: string | null;
  description: string | null;
  metadata?: Record<string, any>;
  display_mode?: "open" | "blind";
  is_active: boolean;
  is_archived: boolean;
  created_at: string;
  last_message_at: string | null;
  last_message_content?: string | null;
  last_message_sender_id?: string | null;
  unread_count: number;
}

export interface ChatRoomListResponse {
  rooms: ChatRoom[];
  total: number;
}

export interface Message {
  message_id: string;
  room_id: string;
  sender_id: string;
  message_type: "text" | "image" | "file" | "system";
  content: string;
  attachments?: string[] | null;
  parent_message_id?: string | null;
  thread_count: number;
  reactions: any[];
  is_edited: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface MessageListResponse {
  messages: Message[];
  total: number;
  has_more: boolean;
}

export interface MessageCreate {
  content: string;
  message_type?: "text" | "image" | "file" | "system";
  attachments?: string[] | null;
  parent_message_id?: string | null;
}

export interface ChatMember {
  member_id: string;
  user_id: string;
  role: string;
  display_name?: string | null;
  anonymous_name?: string | null;
  group_label?: string | null;
  member_index?: number | null;
  is_active: boolean;
  is_muted: boolean;
  last_read_at?: string | null;
  unread_count: number;
  joined_at: string;
}

class ChatService extends BaseApiClient {
  async getRooms(roomType?: "direct" | "team" | "matching"): Promise<ApiResponse<ChatRoomListResponse>> {
    const query = roomType ? `?room_type=${roomType}` : "";
    return this.request<ChatRoomListResponse>(`/chats/rooms${query}`);
  }

  async getRoom(roomId: string): Promise<ApiResponse<ChatRoom>> {
    return this.request<ChatRoom>(`/chats/rooms/${roomId}`);
  }

  async getRoomMembers(roomId: string): Promise<ApiResponse<ChatMember[]>> {
    return this.request<ChatMember[]>(`/chats/rooms/${roomId}/members`);
  }

  async getMessages(
    roomId: string,
    limit: number = 50,
    beforeMessageId?: string
  ): Promise<ApiResponse<MessageListResponse>> {
    const params = new URLSearchParams();
    params.append("limit", String(limit));
    if (beforeMessageId) {
      params.append("before_message_id", beforeMessageId);
    }
    return this.request<MessageListResponse>(`/chats/rooms/${roomId}/messages?${params.toString()}`);
  }

  async sendMessage(roomId: string, data: MessageCreate): Promise<ApiResponse<Message>> {
    return this.request<Message>(`/chats/rooms/${roomId}/messages`, {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async updateMessage(
    roomId: string,
    messageId: string,
    content: string
  ): Promise<ApiResponse<Message>> {
    return this.request<Message>(`/chats/rooms/${roomId}/messages/${messageId}`, {
      method: "PATCH",
      body: JSON.stringify({ content }),
    });
  }

  async deleteMessage(roomId: string, messageId: string): Promise<ApiResponse<Message>> {
    return this.request<Message>(`/chats/rooms/${roomId}/messages/${messageId}`, {
      method: "DELETE",
    });
  }

  async markAsRead(roomId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/chats/rooms/${roomId}/read`, {
      method: "POST",
    });
  }

  async getUnreadCount(): Promise<ApiResponse<{ count: number }>> {
    return this.request<{ count: number }>(`/chats/unread-count`);
  }

  async createDirectChat(recipientId: string): Promise<ApiResponse<ChatRoom>> {
    return this.request<ChatRoom>(`/chats/rooms/direct`, {
      method: "POST",
      body: JSON.stringify({ recipient_id: recipientId }),
    });
  }

  async createTeamChat(teamId: string, roomName: string, description?: string): Promise<ApiResponse<ChatRoom>> {
    return this.request<ChatRoom>(`/chats/rooms/team`, {
      method: "POST",
      body: JSON.stringify({
        team_id: teamId,
        room_name: roomName,
        description,
      }),
    });
  }

  async uploadFiles(roomId: string, files: File[]): Promise<ApiResponse<{ uploaded: number; files: Array<{ path: string; url: string }> }>> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    const token = localStorage.getItem("access_token");
    const env = (import.meta as any).env;
    const apiBaseUrl = env?.VITE_API_BASE_URL || "http://localhost:8000/api/v1";

    const response = await fetch(`${apiBaseUrl}/chats/rooms/${roomId}/upload`, {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({ detail: "File upload failed" }));
      return {
        status: "error",
        error: { message: error.detail || "File upload failed" },
      } as ApiResponse<{ uploaded: number; files: Array<{ path: string; url: string }> }>;
    }

    const data = await response.json();
    return {
      status: "success",
      data,
    } as ApiResponse<{ uploaded: number; files: Array<{ path: string; url: string }> }>;
  }
}

export const chatService = new ChatService();

