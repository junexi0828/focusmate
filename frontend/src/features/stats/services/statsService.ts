import { BaseApiClient, ApiResponse } from '../../../lib/api/base';
import {
  SessionRecordResponse,
  UserStatsResponseBackend,
  transformSessionRecord,
  transformUserStatsResponse,
  SessionRecord,
  UserStatsResponseFrontend,
} from '../../../utils/api-transformers';

/**
 * @deprecated 백엔드 응답 타입입니다. transformUserStatsResponse를 사용하세요.
 */
export type { SessionRecordResponse, UserStatsResponseBackend };

/**
 * 프론트엔드에서 사용하는 세션 레코드 타입 (camelCase)
 */
export type { SessionRecord, UserStatsResponseFrontend as UserStatsResponse };

export interface HourlyPatternResponse {
  hourly_focus_time: number[]; // 24 hours (0-23)
  total_days: number;
  peak_hour: number | null;
}

export interface MonthlyComparisonResponse {
  monthly_data: Array<{
    month: string; // YYYY-MM format
    focus_time_minutes: number;
    focus_time_hours: number;
    sessions: number;
    break_time_minutes: number;
    average_session: number;
  }>;
  total_months: number;
}

export interface GoalAchievementResponse {
  goal_type: 'focus_time' | 'sessions';
  goal_value: number;
  current_value: number;
  achievement_rate: number; // 0-100
  period: 'day' | 'week' | 'month';
  is_achieved: boolean;
  remaining: number;
}

class StatsService extends BaseApiClient {
  async getUserStats(
    userId: string,
    days?: number,
    startDate?: string,
    endDate?: string
  ): Promise<ApiResponse<UserStatsResponseFrontend>> {
    const params = new URLSearchParams();
    if (days !== undefined) {
      params.append('days', days.toString());
    }
    if (startDate && endDate) {
      params.append('start_date', startDate);
      params.append('end_date', endDate);
    }

    const queryString = params.toString();
    const response = await this.request<UserStatsResponseBackend>(
      `/stats/user/${userId}${queryString ? `?${queryString}` : ''}`
    );

    // 변환 레이어 적용
    if (response.status === 'success' && response.data) {
      return {
        ...response,
        data: transformUserStatsResponse(response.data),
      };
    }

    return response as ApiResponse<UserStatsResponseFrontend>;
  }

  async getHourlyPattern(
    userId: string,
    days: number = 30
  ): Promise<ApiResponse<HourlyPatternResponse>> {
    return this.request<HourlyPatternResponse>(
      `/stats/user/${userId}/hourly-pattern?days=${days}`
    );
  }

  async getMonthlyComparison(
    userId: string,
    months: number = 6
  ): Promise<ApiResponse<MonthlyComparisonResponse>> {
    return this.request<MonthlyComparisonResponse>(
      `/stats/user/${userId}/monthly-comparison?months=${months}`
    );
  }

  async getGoalAchievement(
    userId: string,
    goalType: 'focus_time' | 'sessions',
    goalValue: number,
    period: 'day' | 'week' | 'month' = 'week'
  ): Promise<ApiResponse<GoalAchievementResponse>> {
    return this.request<GoalAchievementResponse>(
      `/stats/user/${userId}/goal-achievement?goal_type=${goalType}&goal_value=${goalValue}&period=${period}`
    );
  }

  async recordSession(data: {
    user_id: string;
    room_id: string;
    session_type: 'work' | 'break';
    duration_minutes: number;
  }): Promise<ApiResponse<{ status: string; session_id: string }>> {
    return this.request('/stats/session', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async saveGoal(data: {
    daily_goal_minutes: number;
    weekly_goal_sessions: number;
  }): Promise<ApiResponse<UserGoalResponse>> {
    return this.request<UserGoalResponse>('/stats/goals', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getGoal(): Promise<ApiResponse<UserGoalResponse>> {
    return this.request<UserGoalResponse>('/stats/goals');
  }
}

export interface UserGoalResponse {
  id: string;
  user_id: string;
  daily_goal_minutes: number;
  weekly_goal_sessions: number;
  created_at: string;
  updated_at: string;
}

export const statsService = new StatsService();

