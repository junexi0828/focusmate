/**
 * Profile API client functions
 */

import api from "./client";
import { User } from "../types/user";

export interface UserProfileUpdate {
  username?: string;
  bio?: string;
  school?: string;
  profile_image?: string;
}

// Get user profile
export const getProfile = async (userId: string): Promise<User> => {
  const response = await api.get(`/auth/profile/${userId}`);
  return response.data;
};

// Update user profile
export const updateProfile = async (
  userId: string,
  data: UserProfileUpdate
): Promise<User> => {
  const response = await api.put(`/auth/profile/${userId}`, data);
  return response.data;
};

// Upload profile image
export const uploadProfileImage = async (
  userId: string,
  file: File
): Promise<{ profile_image: string }> => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post(
    `/auth/profile/${userId}/upload-image`,
    formData,
    {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    }
  );
  return response.data;
};
