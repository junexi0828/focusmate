import { BaseApiClient, ApiResponse } from "../../../lib/api/base";

export interface UserSettingsResponse {
  user_id: string;
  theme: "light" | "dark" | "system";
  notifications_enabled: boolean;
  email_notifications: boolean;
  push_notifications: boolean;
  language: string;
  timezone: string;
  focus_timer_default_minutes: number;
  break_timer_default_minutes: number;
  auto_start_break: boolean;
  auto_start_focus: boolean;
}

export interface UserSettingsUpdate {
  theme?: "light" | "dark" | "system";
  notifications_enabled?: boolean;
  email_notifications?: boolean;
  push_notifications?: boolean;
  language?: string;
  timezone?: string;
  focus_timer_default_minutes?: number;
  break_timer_default_minutes?: number;
  auto_start_break?: boolean;
  auto_start_focus?: boolean;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface EmailChangeRequest {
  new_email: string;
  password: string;
}

export class SettingsService extends BaseApiClient {
  async getSettings(): Promise<ApiResponse<UserSettingsResponse>> {
    return this.request<UserSettingsResponse>("/settings/");
  }

  async updateSettings(
    data: UserSettingsUpdate
  ): Promise<ApiResponse<UserSettingsResponse>> {
    return this.request<UserSettingsResponse>("/settings/", {
      method: "PUT",
      body: JSON.stringify(data),
    });
  }

  async changePassword(
    data: PasswordChangeRequest
  ): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>("/settings/password", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async changeEmail(
    data: EmailChangeRequest
  ): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>("/settings/email", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
}

export const settingsService = new SettingsService();
