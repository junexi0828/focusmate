import { BaseApiClient, ApiResponse } from "../../../lib/api/base";
import type {
  MatchingPoolCreate,
  MatchingPool,
  MatchingPoolStats,
  MatchingProposal,
  ProposalAction,
  ComprehensiveMatchingStats
} from "../../../types/matching"; // Use central types

export class MatchingService extends BaseApiClient {
  async createPool(
    data: MatchingPoolCreate
  ): Promise<ApiResponse<MatchingPool>> {
    return this.request<MatchingPool>("/matching/pools", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getMyPool(): Promise<ApiResponse<MatchingPool | null>> {
    return this.request<MatchingPool | null>("/matching/pools/my");
  }

  async getPoolStatistics(): Promise<ApiResponse<MatchingPoolStats>> {
    return this.request<MatchingPoolStats>("/matching/pools/stats");
  }

  async getPool(poolId: string): Promise<ApiResponse<MatchingPool>> {
    return this.request<MatchingPool>(`/matching/pools/${poolId}`);
  }

  async cancelPool(poolId: string): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>(`/matching/pools/${poolId}`, {
      method: "DELETE",
    });
  }

  async getComprehensiveStatistics(): Promise<ApiResponse<ComprehensiveMatchingStats>> {
    return this.request<ComprehensiveMatchingStats>(
      "/matching/stats/comprehensive"
    );
  }

  // Proposal Methods
  async getMyProposals(): Promise<ApiResponse<MatchingProposal[]>> {
    return this.request<MatchingProposal[]>("/matching/proposals/my");
  }

  async getProposal(proposalId: string, includePools: boolean = false): Promise<ApiResponse<MatchingProposal>> {
    const query = includePools ? "?include_pools=true" : "";
    return this.request<MatchingProposal>(`/matching/proposals/${proposalId}${query}`);
  }

  async respondToProposal(proposalId: string, action: ProposalAction): Promise<ApiResponse<MatchingProposal>> {
    return this.request<MatchingProposal>(`/matching/proposals/${proposalId}/respond`, {
      method: "POST",
      body: JSON.stringify(action),
    });
  }
}

export const matchingService = new MatchingService();
