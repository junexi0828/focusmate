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
    // Note: This endpoint might need to be added to backend
    // For now, we'll get members from team response
    const teamResponse = await this.getTeam(teamId);
    if (teamResponse.status === 'error') {
      return teamResponse as ApiResponse<TeamMember[]>;
    }
    // TODO: Add dedicated endpoint for members
    return { status: 'success', data: [] } as ApiResponse<TeamMember[]>;
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
    // TODO: Add endpoint for getting user's invitations
    return { status: 'success', data: [] } as ApiResponse<TeamInvitation[]>;
  }
}

export const rankingService = new RankingService();

