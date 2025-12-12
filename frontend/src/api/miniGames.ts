/**
 * Mini Games API client functions
 */

import api from "./client";

// Types
export interface MiniGameScore {
  game_type: string;
  score: number;
  completed_at: string;
}

export interface MiniGameScoreResponse {
  id: string;
  user_id: string;
  game_type: string;
  score: number;
  completed_at: string;
  created_at: string;
}

export interface LeaderboardEntry {
  user_id: string;
  username: string;
  score: number;
  rank: number;
  completed_at: string;
}

// Submit mini game score
export const submitMiniGameScore = async (
  scoreData: MiniGameScore
): Promise<MiniGameScoreResponse> => {
  const response = await api.post("/api/v1/ranking/mini-games/start", scoreData);
  return response.data;
};

// Get mini game leaderboard
export const getMiniGameLeaderboard = async (
  gameType: string,
  limit: number = 10
): Promise<LeaderboardEntry[]> => {
  const response = await api.get(`/api/v1/ranking/mini-games/leaderboard/${gameType}`, {
    params: { limit },
  });
  return response.data.leaderboard || [];
};
