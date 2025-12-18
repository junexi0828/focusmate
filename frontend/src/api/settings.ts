/**
 * Settings API client functions
 */

import api from "./client";
import {
  UserSettings,
  UserSettingsUpdate,
  PasswordChangeRequest,
  EmailChangeRequest,
} from "../types/settings";

// Get my settings
export const getSettings = async (): Promise<UserSettings> => {
  const response = await api.get("/settings/");
  return response.data;
};

// Update my settings
export const updateSettings = async (
  data: UserSettingsUpdate
): Promise<UserSettings> => {
  const response = await api.put("/settings/", data);
  return response.data;
};

// Change password
export const changePassword = async (
  data: PasswordChangeRequest
): Promise<{ message: string }> => {
  const response = await api.post("/settings/password", data);
  return response.data;
};

// Change email
export const changeEmail = async (
  data: EmailChangeRequest
): Promise<{ message: string }> => {
  const response = await api.post("/settings/email", data);
  return response.data;
};
