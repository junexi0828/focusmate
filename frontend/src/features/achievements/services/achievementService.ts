import { BaseApiClient, ApiResponse } from "../../../lib/api/base";

export interface Achievement {
  id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  requirement_type: string;
  requirement_value: number;
  points: number;
  created_at: string;
}

export interface UserAchievement {
  id: string;
  user_id: string;
  achievement_id: string;
  unlocked_at: string;
  progress: number;
  achievement?: Achievement;
}

export interface AchievementProgress {
  achievement_id: string;
  achievement_name: string;
  achievement_description: string;
  achievement_icon: string;
  achievement_category: string;
  requirement_type: string;
  requirement_value: number;
  current_progress: number;
  is_unlocked: boolean;
  unlocked_at?: string;
  progress_percentage: number;
}

class AchievementService extends BaseApiClient {
  async getUserAchievements(userId: string): Promise<ApiResponse<UserAchievement[]>> {
    return this.request<UserAchievement[]>(`/achievements/user/${userId}`);
  }

  async getUserAchievementProgress(
    userId: string
  ): Promise<ApiResponse<AchievementProgress[]>> {
    return this.request<AchievementProgress[]>(`/achievements/user/${userId}/progress`);
  }

  async getAllAchievements(): Promise<ApiResponse<Achievement[]>> {
    return this.request<Achievement[]>(`/achievements`);
  }

  async getAchievementsByCategory(
    category: string
  ): Promise<ApiResponse<Achievement[]>> {
    return this.request<Achievement[]>(`/achievements/category/${category}`);
  }

  async checkAndUnlockAchievements(
    userId: string
  ): Promise<ApiResponse<UserAchievement[]>> {
    return this.request<UserAchievement[]>(`/achievements/user/${userId}/check`, {
      method: "POST",
    });
  }
}

export const achievementService = new AchievementService();

