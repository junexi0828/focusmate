import { BaseApiClient, ApiResponse } from "../../../lib/api/base";

export interface Notification {
  id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  data?: Record<string, any>;
  is_read: boolean;
  created_at: string;
  read_at?: string;
}

export interface NotificationResponse extends Notification {}

export interface NotificationCreate {
  user_id: string;
  type: string;
  title: string;
  message: string;
  data?: Record<string, any>;
  email?: boolean;
  push?: boolean;
}

export class NotificationService extends BaseApiClient {
  async getNotifications(
    unreadOnly = false,
    limit = 50,
    offset = 0
  ): Promise<ApiResponse<NotificationResponse[]>> {
    const params = new URLSearchParams({
      unread_only: String(unreadOnly),
      limit: String(limit),
      offset: String(offset),
    });
    return this.request<NotificationResponse[]>(
      `/notifications/list?${params.toString()}`
    );
  }

  async getUnreadCount(): Promise<ApiResponse<{ unread_count: number }>> {
    return this.request<{ unread_count: number }>(
      "/notifications/unread-count"
    );
  }

  async markAsRead(notificationIds: string[]): Promise<ApiResponse<{ marked_count: number }>> {
    return this.request<{ marked_count: number }>("/notifications/mark-read", {
      method: "POST",
      body: JSON.stringify({ notification_ids: notificationIds }),
    });
  }

  async markAllAsRead(): Promise<ApiResponse<{ marked_count: number }>> {
    return this.request<{ marked_count: number }>(
      "/notifications/mark-all-read",
      {
        method: "POST",
      }
    );
  }

  async deleteNotification(notificationId: string): Promise<ApiResponse<void>> {
    return this.request<void>(`/notifications/${notificationId}`, {
      method: "DELETE",
    });
  }

  // Admin/System use mostly, but included for completeness
  async createNotification(
    data: NotificationCreate
  ): Promise<ApiResponse<NotificationResponse>> {
    return this.request<NotificationResponse>("/notifications/create", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
}

export const notificationService = new NotificationService();
