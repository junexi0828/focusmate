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

  // Matching Pools
  createPool: async (data: MatchingPoolCreate) => {
    const response = await api.post<MatchingPool>("/matching/pools", data);
    return response.data;
  },

  getMyPool: async () => {
    const response = await api.get<MatchingPool>("/matching/pools/my");
    return response.data;
  },

  cancelPool: async (poolId: string) => {
    const response = await api.delete(`/matching/pools/${poolId}`);
    return response.data;
  },

  getPoolStats: async () => {
    const response = await api.get<{
      total_pools: number;
      waiting_pools: number;
      matched_today: number;
      by_gender: Record<string, number>;
      by_university: Record<string, number>;
    }>("/matching/pools/stats");
    return response.data;
  },

  // Proposals
  getMyProposals: async () => {
    const response = await api.get<MatchingProposal[]>(
      "/matching/proposals/my"
    );
    return response.data;
  },

  getProposal: async (proposalId: string) => {
    const response = await api.get<MatchingProposal>(
      `/matching/proposals/${proposalId}`
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
