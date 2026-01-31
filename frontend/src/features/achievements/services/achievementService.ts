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
    const response = await this.request<any[]>(`/achievements/user/${userId}/progress`);

    if (response.status === "success" && response.data) {
      // Transform the nested backend response to the flattened frontend interface
      const transformedData: AchievementProgress[] = response.data.map((item: any) => ({
        achievement_id: item.achievement.id,
        achievement_name: item.achievement.name,
        achievement_description: item.achievement.description,
        achievement_icon: item.achievement.icon,
        achievement_category: item.achievement.category,
        requirement_type: item.achievement.requirement_type,
        requirement_value: item.achievement.requirement_value,
        current_progress: item.progress,
        is_unlocked: item.is_unlocked,
        unlocked_at: item.unlocked_at,
        progress_percentage: item.progress_percentage
      }));

      return {
        ...response,
        data: transformedData
      };
    }

    return response as unknown as ApiResponse<AchievementProgress[]>;
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

