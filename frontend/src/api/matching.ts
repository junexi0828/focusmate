/**
 * API client for matching system.
 */

import { api } from "./client";
import type {
  UserVerification,
  VerificationSubmit,
  MatchingPool,
  MatchingPoolCreate,
  MatchingProposal,
  ProposalAction,
} from "@/types/matching";

export const matchingApi = {
  // Verification
  submitVerification: async (data: VerificationSubmit) => {
    const response = await api.post<UserVerification>(
      "/verification/submit",
      data
    );
    return response.data;
  },

  getVerificationStatus: async () => {
    const response = await api.get<UserVerification>("/verification/status");
    return response.data;
  },

  uploadVerificationFile: async (file: File) => {
    const formData = new FormData();
    formData.append("files", file);
    const response = await api.post<{
      uploaded_files: string[];
      count: number;
      encrypted: boolean;
    }>("/verification/upload", formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
    return response.data;
  },

  // Matching Pools
  createPool: async (data: MatchingPoolCreate) => {
    const response = await api.post<MatchingPool>("/matching/pools", data);
    return response.data;
  },

  getMyPool: async () => {
    const response = await api.get<MatchingPool | null>("/matching/pools/my");
    return response.data;
  },

  getPool: async (poolId: string) => {
    const response = await api.get<MatchingPool>(`/matching/pools/${poolId}`);
    return response.data;
  },

  cancelPool: async (poolId: string) => {
    const response = await api.delete(`/matching/pools/${poolId}`);
    return response.data;
  },

        getPoolStats: async () => {
          const response = await api.get<{
            total_waiting: number;
            total_all: number;
            total_matched: number;
            total_expired: number;
            by_status: Record<string, number>;
            by_member_count: Record<string, number>;
            by_gender: Record<string, number>;
            by_department: Record<string, number>;
            by_matching_type: Record<string, number>;
            average_wait_time_hours: number;
          }>("/matching/pools/stats");
          return response.data;
        },

        getComprehensiveStats: async () => {
          const response = await api.get<{
            pools: {
              total_waiting: number;
              total_all: number;
              total_matched: number;
              total_expired: number;
              by_status: Record<string, number>;
              by_member_count: Record<string, number>;
              by_gender: Record<string, number>;
              by_department: Record<string, number>;
              by_matching_type: Record<string, number>;
              average_wait_time_hours: number;
            };
            proposals: {
              total_proposals: number;
              by_status: Record<string, number>;
              matched_count: number;
              success_rate: number;
              acceptance_rate: number;
              rejection_rate: number;
              pending_count: number;
              average_matching_time_hours: number;
              min_matching_time_hours: number;
              max_matching_time_hours: number;
              daily_matches: Array<{ date: string; count: number }>;
              weekly_matches: Array<{ week: string; count: number }>;
              monthly_matches: Array<{ month: string; count: number }>;
            };
          }>("/matching/stats/comprehensive");
          return response.data;
        },

  // Proposals
  getMyProposals: async () => {
    const response = await api.get<MatchingProposal[]>(
      "/matching/proposals/my"
    );
    return response.data;
  },

  getProposal: async (proposalId: string, includePools: boolean = false) => {
    const query = includePools ? "?include_pools=true" : "";
    const response = await api.get<MatchingProposal>(
      `/matching/proposals/${proposalId}${query}`
    );
    return response.data;
  },

  respondToProposal: async (proposalId: string, action: ProposalAction) => {
    const response = await api.post<MatchingProposal>(
      `/matching/proposals/${proposalId}/respond`,
      action
    );
    return response.data;
  },
};
