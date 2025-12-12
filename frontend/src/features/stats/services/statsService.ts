import { BaseApiClient, ApiResponse } from '../../../lib/api/base';

export interface SessionRecord {
  session_id: string;
  user_id: string;
  room_id: string;
  session_type: 'work' | 'break';
  duration_minutes: number;
  completed_at: string;
  room_name?: string;
  // Backward compatibility
  id?: string;
  type?: string;
  duration?: number;
}

export interface UserStatsResponse {
  total_focus_time: number;
  total_sessions: number;
  average_session: number;
  sessions: SessionRecord[];
}

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
  ): Promise<ApiResponse<UserStatsResponse>> {
    const params = new URLSearchParams();
    if (days !== undefined) {
      params.append('days', days.toString());
    }
    if (startDate && endDate) {
      params.append('start_date', startDate);
      params.append('end_date', endDate);
    }

    const queryString = params.toString();
    return this.request<UserStatsResponse>(
      `/stats/user/${userId}${queryString ? `?${queryString}` : ''}`
    );
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
}

export const statsService = new StatsService();

