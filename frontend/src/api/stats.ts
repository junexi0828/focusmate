/**
 * Stats API client functions
 */

import { api } from "./client";

// Types
export interface UserGoal {
  id: string;
  user_id: string;
  daily_goal_minutes: number;
  weekly_goal_sessions: number;
  created_at: string;
  updated_at: string;
}

export interface UserGoalCreate {
  daily_goal_minutes: number;
  weekly_goal_sessions: number;
}

export interface ManualSession {
  id: string;
  user_id: string;
  duration_minutes: number;
  session_type: "focus" | "break";
  completed_at: string;
  created_at: string;
}

export interface ManualSessionCreate {
  duration_minutes: number;
  session_type: "focus" | "break";
  completed_at: string;
}

// User Goals API
export const saveUserGoal = async (goal: UserGoalCreate): Promise<UserGoal> => {
  const response = await api.post("/stats/goals", goal);
  return response.data;
};

export const getUserGoal = async (): Promise<UserGoal> => {
  const response = await api.get("/stats/goals");
  return response.data;
};

// Manual Sessions API
export const saveManualSession = async (
  session: ManualSessionCreate
): Promise<ManualSession> => {
  const response = await api.post("/stats/sessions", session);
  return response.data;
};

export const getManualSessions = async (
  limit: number = 100
): Promise<ManualSession[]> => {
  const response = await api.get("/stats/sessions", {
    params: { limit },
  });
  return response.data;
};
