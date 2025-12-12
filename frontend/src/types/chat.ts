/**
 * TypeScript types for unified chat system.
 */

export type ChatRoomType = "direct" | "team" | "matching";
export type DisplayMode = "open" | "blind";
export type MessageType = "text" | "image" | "file" | "system";

export interface ChatRoom {
  room_id: string;
  room_type: ChatRoomType;
  room_name: string | null;
  description: string | null;
  metadata: Record<string, any> | null;
  display_mode: DisplayMode | null;
  is_active: boolean;
  is_archived: boolean;
  created_at: string;
  last_message_at: string | null;
  unread_count: number;
}

export interface ChatMember {
  member_id: string;
  user_id: string;
  role: string;
  display_name: string | null;
  anonymous_name: string | null;
  group_label: string | null;
  member_index: number | null;
  is_active: boolean;
  is_muted: boolean;
  last_read_at: string | null;
  unread_count: number;
  joined_at: string;
}

export interface ChatMessage {
  message_id: string;
  room_id: string;
  sender_id: string;
  message_type: MessageType;
  content: string;
  attachments: string[] | null;
  parent_message_id: string | null;
  thread_count: number;
  reactions: any[];
  is_edited: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
}

export interface DirectChatCreate {
  recipient_id: string;
}

export interface TeamChatCreate {
  team_id: string;
  room_name: string;
  description?: string;
}

export interface MessageCreate {
  content: string;
  message_type?: MessageType;
  attachments?: string[];
  parent_message_id?: string;
}

export interface WebSocketMessage {
  type:
    | "message"
    | "message_updated"
    | "message_deleted"
    | "typing"
    | "joined"
    | "left";
  message?: ChatMessage;
  message_id?: string;
  user_id?: string;
  room_id?: string;
}
