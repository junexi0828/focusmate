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
  team_id: string;
  team_name: string;
  best_score: number;
  games_played: number;
}

// Submit mini game score
export const submitMiniGameScore = async (
  teamId: string,
  gameType: string,
  score: number,
  completionTime: number
): Promise<MiniGameScoreResponse> => {
  const response = await api.post("/api/v1/ranking/mini-games/submit", null, {
    params: {
      team_id: teamId,
      game_type: gameType,
      score: score,
      completion_time: completionTime,
    },
  });
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
  // Backend returns array directly, not wrapped in leaderboard property
  return Array.isArray(response.data) ? response.data : [];
};
