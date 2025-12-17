export interface UserSettings {
  id: string;
  user_id: string;
  theme: 'light' | 'dark' | 'system';
  language: string;
  notification_email: boolean;
  notification_push: boolean;
  notification_session: boolean;
  notification_achievement: boolean;
  notification_message: boolean;
  do_not_disturb_start?: string;
  do_not_disturb_end?: string;
  session_reminder: boolean;
  custom_settings?: Record<string, any>;
}

export interface UserSettingsUpdate {
  theme?: 'light' | 'dark' | 'system';
  language?: string;
  notification_email?: boolean;
  notification_push?: boolean;
  notification_session?: boolean;
  notification_achievement?: boolean;
  notification_message?: boolean;
  do_not_disturb_start?: string;
  do_not_disturb_end?: string;
  session_reminder?: boolean;
  custom_settings?: Record<string, any>;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export interface EmailChangeRequest {
  new_email: string;
  password: string;
}
