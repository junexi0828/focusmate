import { BaseApiClient, ApiResponse } from '../../../lib/api/base';

// Team Types
export interface Team {
  team_id: string;
  team_name: string;
  team_type: 'general' | 'department' | 'lab' | 'club';
  verification_status: 'none' | 'pending' | 'verified' | 'rejected';
  leader_id: string;
  mini_game_enabled: boolean;
  invite_code?: string | null;
  affiliation_info?: {
    school?: string;
    department?: string;
    lab?: string;
    club?: string;
  } | null;
  created_at: string;
  updated_at: string;
  // Optional stats fields (populated from team stats API)
  current_rank?: number;
  total_sessions?: number;
  total_points?: number;
  total_focus_time?: number;
}

export interface TeamCreateRequest {
  team_name: string;
  team_type: 'general' | 'department' | 'lab' | 'club';
  mini_game_enabled?: boolean;
  affiliation_info?: {
    school?: string;
    department?: string;
    lab?: string;
    club?: string;
  };
}

export interface TeamUpdateRequest {
  team_name?: string;
  mini_game_enabled?: boolean;
}

// Team Member Types
export interface TeamMember {
  member_id: string;
  team_id: string;
  user_id: string;
  role: 'leader' | 'member';
  joined_at: string;
}

// Team Invitation Types
export interface TeamInvitation {
  invitation_id: string;
  team_id: string;
  email: string;
  invited_by: string;
  status: 'pending' | 'accepted' | 'rejected' | 'expired';
  created_at: string;
  expires_at: string;
  accepted_at?: string | null;
}

export interface TeamInvitationCreateRequest {
  email: string;
}

class RankingService extends BaseApiClient {
  // Team Management
  async createTeam(data: TeamCreateRequest): Promise<ApiResponse<Team>> {
    return this.request<Team>('/ranking/teams', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getTeam(teamId: string): Promise<ApiResponse<Team>> {
    return this.request<Team>(`/ranking/teams/${teamId}`);
  }

  async getMyTeams(): Promise<ApiResponse<Team[]>> {
    return this.request<Team[]>('/ranking/teams');
  }

  async updateTeam(
    teamId: string,
    data: TeamUpdateRequest
  ): Promise<ApiResponse<Team>> {
    return this.request<Team>(`/ranking/teams/${teamId}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    });
  }

  async deleteTeam(teamId: string): Promise<ApiResponse<void>> {
    return this.request<void>(`/ranking/teams/${teamId}`, {
      method: 'DELETE',
    });
  }

  // Team Member Management
  async getTeamMembers(teamId: string): Promise<ApiResponse<TeamMember[]>> {
    const response = await this.request<{ members: TeamMember[]; total: number }>(`/ranking/teams/${teamId}/members`);
    if (response.status === 'success' && response.data) {
      return { status: 'success', data: response.data.members } as ApiResponse<TeamMember[]>;
    }
    return { status: 'error', error: response.error } as ApiResponse<TeamMember[]>;
  }

  async removeMember(
    teamId: string,
    userId: string
  ): Promise<ApiResponse<void>> {
    return this.request<void>(`/ranking/teams/${teamId}/members/${userId}`, {
      method: 'DELETE',
    });
  }

  async leaveTeam(teamId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/ranking/teams/${teamId}/leave`, {
      method: 'POST',
    });
  }

  // Team Invitation Management
  async inviteMember(
    teamId: string,
    data: TeamInvitationCreateRequest
  ): Promise<ApiResponse<TeamInvitation>> {
    return this.request<TeamInvitation>(`/ranking/teams/${teamId}/invite`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async acceptInvitation(
    invitationId: string
  ): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(
      `/ranking/teams/invitations/${invitationId}/accept`,
      {
        method: 'POST',
      }
    );
  }

  async rejectInvitation(
    invitationId: string
  ): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(
      `/ranking/teams/invitations/${invitationId}/reject`,
      {
        method: 'POST',
      }
    );
  }

  async getMyInvitations(): Promise<ApiResponse<TeamInvitation[]>> {
    const response = await this.request<{ invitations: TeamInvitation[]; total: number }>('/ranking/invitations');
    if (response.status === 'success' && response.data) {
      return { status: 'success', data: response.data.invitations } as ApiResponse<TeamInvitation[]>;
    }
    return { status: 'success', data: [] } as ApiResponse<TeamInvitation[]>;
  }

  // Team Statistics
  async getTeamStats(teamId: string): Promise<ApiResponse<TeamStats>> {
    return this.request<TeamStats>(`/ranking/teams/${teamId}/stats`);
  }

  // Session History
  async getSessionHistory(
    teamId: string,
    options?: {
      userId?: string;
      limit?: number;
    }
  ): Promise<ApiResponse<SessionHistory[]>> {
    const params = new URLSearchParams();
    if (options?.userId) {
      params.append('user_id', options.userId);
    }
    if (options?.limit) {
      params.append('limit', options.limit.toString());
    }
    const queryString = params.toString();
    const url = `/ranking/teams/${teamId}/sessions${queryString ? `?${queryString}` : ''}`;
    return this.request<SessionHistory[]>(url);
  }

  // Mini-Game History
  async getTeamMiniGames(
    teamId: string,
    options?: {
      gameType?: string;
      limit?: number;
    }
  ): Promise<ApiResponse<MiniGameRecord[]>> {
    const params = new URLSearchParams();
    if (options?.gameType) {
      params.append('game_type', options.gameType);
    }
    if (options?.limit) {
      params.append('limit', options.limit.toString());
    }
    const queryString = params.toString();
    const url = `/ranking/teams/${teamId}/mini-games${queryString ? `?${queryString}` : ''}`;
    return this.request<MiniGameRecord[]>(url);
  }

  // Mini-Game Leaderboard
  async getMiniGameLeaderboard(
    gameType: string,
    limit?: number
  ): Promise<ApiResponse<MiniGameLeaderboardEntry[]>> {
    const params = new URLSearchParams();
    if (limit) {
      params.append('limit', limit.toString());
    }
    const queryString = params.toString();
    const url = `/ranking/mini-games/leaderboard/${gameType}${queryString ? `?${queryString}` : ''}`;
    return this.request<MiniGameLeaderboardEntry[]>(url);
  }

  // Hall of Fame
  async getHallOfFame(
    period: 'weekly' | 'monthly' | 'all' = 'all'
  ): Promise<ApiResponse<HallOfFameResponse>> {
    return this.request<HallOfFameResponse>(`/ranking/hall-of-fame?period=${period}`);
  }

  // Leaderboard
  async getLeaderboard(
    period: 'weekly' | 'monthly' | 'all_time' = 'weekly',
    limit: number = 50
  ): Promise<ApiResponse<LeaderboardResponse>> {
    const params = new URLSearchParams();
    params.append('period', period);
    params.append('limit', limit.toString());
    return this.request<LeaderboardResponse>(`/ranking/leaderboard?${params.toString()}`);
  }
}

export interface TeamStats {
  team_id: string;
  total_focus_time: number; // in minutes
  total_sessions: number;
  member_count: number;
  current_streak: number;
  mini_game_score?: number;
  member_breakdown?: Array<{
    user_id: string;
    role: string;
    joined_at: string;
    total_sessions: number;
    total_focus_time: number;
  }>;
}

export interface SessionHistory {
  session_id: string;
  team_id: string;
  user_id: string;
  duration_minutes: number;
  session_type: 'work' | 'break';
  success: boolean;
  completed_at: string;
}

export interface MiniGameRecord {
  game_id: string;
  team_id: string;
  user_id: string;
  game_type: string;
  score: number;
  success: boolean;
  completion_time?: number;
  game_data?: Record<string, any>;
  played_at: string;
}

export interface MiniGameLeaderboardEntry {
  team_id: string;
  team_name: string;
  best_score: number;
  games_played: number;
}

export interface HallOfFameEntry {
  team_id: string;
  team_name: string;
  team_type: string;
  total_focus_time: number;
  session_count: number;
  total_game_score: number;
  game_count: number;
  rank?: number;
}

export interface HallOfFameResponse {
  period: string;
  total_teams: number;
  teams: HallOfFameEntry[];
  top_focus_teams: HallOfFameEntry[];
  top_game_teams: HallOfFameEntry[];
}

export interface LeaderboardEntry {
  rank: number;
  team_id: string;
  team_name: string;
  team_type: string;
  score: number;
  rank_change: number;
  member_count?: number;
  average_score?: number;
  total_sessions?: number;
}

export interface LeaderboardResponse {
  ranking_type: string;
  period: string;
  updated_at: string;
  leaderboard: LeaderboardEntry[];
}

export const rankingService = new RankingService();

