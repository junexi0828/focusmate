/**
 * Notifications API client functions
 */

import api from "./client";
import { Notification } from "../types/notification";

// Get my notifications
export const getNotifications = async (
  unreadOnly: boolean = false,
  limit: number = 50,
  offset: number = 0
): Promise<Notification[]> => {
  const response = await api.get("/notifications", {
    params: { unread_only: unreadOnly, limit, offset },
  });
  return response.data;
};

// Get unread count
export const getUnreadCount = async (): Promise<number> => {
  const response = await api.get("/notifications/unread-count");
  return response.data.unread_count;
};

// Mark notifications as read
export const markAsRead = async (
  notificationIds: string[]
): Promise<{ marked_count: number }> => {
  const response = await api.post("/notifications/mark-read", {
    notification_ids: notificationIds,
  });
  return response.data;
};

// Mark all as read
export const markAllAsRead = async (): Promise<{ marked_count: number }> => {
  const response = await api.post("/notifications/mark-all-read");
  return response.data;
};

// Delete notification
export const deleteNotification = async (
  notificationId: string
): Promise<void> => {
  await api.delete(`/notifications/${notificationId}`);
};
