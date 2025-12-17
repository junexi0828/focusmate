export interface Notification {
  notification_id: string;
  user_id: string;
  type: string;
  title: string;
  message: string;
  data?: Record<string, any>;
  is_read: boolean;
  read_at?: string;
  created_at: string;
  updated_at: string;
}

export interface NotificationCreate {
  user_id: string;
  type: string;
  title: string;
  message: string;
  data?: Record<string, any>;
}
