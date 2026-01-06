/**
 * Matching system main page with verification and pool management.
 */

import { useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  Shield,
  Users,
  Heart,
  CheckCircle,
  XCircle,
  Clock,
  TrendingUp,
} from "lucide-react";
import { matchingService } from "@/features/matching/services/matchingService";
import { verificationService } from "@/features/verification/services/verificationService";
import { PageTransition } from "@/components/PageTransition";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button-enhanced";
import { Input } from "@/components/ui/input";
import { EmptyState } from "@/components/EmptyState";
import { CreatePoolDialog } from "@/features/matching/components/CreatePoolDialog";
import type { MatchingPoolCreate } from "@/types/matching";
import { toast } from "sonner";

export default function Matching() {
  const [showPoolForm, setShowPoolForm] = useState(false);
  const queryClient = useQueryClient();

  // Fetch verification status
  const { data: verification, isLoading: verificationLoading } = useQuery({
    queryKey: ["verification-status"],
    queryFn: async () => {
      const res = await verificationService.getStatus();
      return res.data;
    },
    retry: false,
  });

  // Fetch my pool
  const { data: myPool } = useQuery({
    queryKey: ["my-pool"],
    queryFn: async () => {
      const res = await matchingService.getMyPool();
      return res.data;
    },
    enabled: verification?.status === "approved",
    retry: false,
  });

  // Fetch proposals (manual refresh recommended)
  const { data: proposals = [] } = useQuery({
    queryKey: ["my-proposals"],
    queryFn: async () => {
      const res = await matchingService.getMyProposals();
      return res.data || [];
    },
    enabled: verification?.status === "approved",
    refetchInterval: false, // Disabled: Proposals don't need real-time polling
    staleTime: 1000 * 60, // 1 minute
  });

  // Fetch stats
  const { data: stats } = useQuery({
    queryKey: ["pool-stats"],
    queryFn: async () => {
      const res = await matchingService.getPoolStatistics();
      return res.data;
    },
  });

  // Cancel pool mutation
  const cancelPoolMutation = useMutation({
    mutationFn: async (poolId: string) => {
      const res = await matchingService.cancelPool(poolId);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-pool"] });
      toast.success("풀이 취소되었습니다");
    },
  });

  // Create pool mutation
  const createPoolMutation = useMutation({
    mutationFn: async (data: MatchingPoolCreate) => {
      const res = await matchingService.createPool(data);
      if (res.status === 'error') throw new Error(res.error?.message);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-pool"] });
      queryClient.invalidateQueries({ queryKey: ["pool-stats"] });
      setShowPoolForm(false);
      toast.success("매칭 풀이 생성되었습니다!");
    },
    onError: (error: unknown) => {
      toast.error(error?.message || "풀 생성에 실패했습니다");
    },
  });

  // Respond to proposal mutation
  const respondMutation = useMutation({
    mutationFn: async ({
      proposalId,
      action,
    }: {
      proposalId: string;
      action: "accept" | "reject";
    }) => {
      const res = await matchingService.respondToProposal(proposalId, { action });
      if (res.status === 'error') throw new Error(res.error?.message);
      return res.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["my-proposals"] });
      queryClient.invalidateQueries({ queryKey: ["my-pool"] });
      toast.success("응답이 전송되었습니다");
    },
  });

  const isVerified = verification?.status === "approved";

  return (
    <PageTransition>
      <div className="min-h-full bg-gradient-to-br from-[#FCE7F5] via-[#E0F7FD] to-[#E0F7FD] dark:from-slate-900 dark:to-slate-800 py-8">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          {/* Header */}
          <div className="mb-8">
            <div className="flex items-center gap-3 mb-2">
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#F9A8D4] to-[#7ED6E8] flex items-center justify-center">
                <Heart className="w-6 h-6 text-white" />
              </div>
              <h1 className="text-3xl font-bold bg-gradient-to-r from-[#F9A8D4] to-[#7ED6E8] bg-clip-text text-transparent">
                매칭 시스템
              </h1>
            </div>
            <p className="text-slate-600 dark:text-slate-400">
              검증된 사용자들과 안전한 과팅 매칭을 시작하세요
            </p>
          </div>

          {/* Verification Status */}
          {!verificationLoading && (
            <Card className="p-6 mb-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <Shield className="w-8 h-8 text-blue-500" />
                  <div>
                    <h3 className="font-semibold text-lg">인증 상태</h3>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      {!verification ? (
                        "인증이 필요합니다"
                      ) : verification.status === "approved" ? (
                        <span className="text-green-600 flex items-center gap-1">
                          <CheckCircle className="w-4 h-4" />
                          인증 완료
                        </span>
                      ) : verification.status === "pending" ? (
                        <span className="text-yellow-600 flex items-center gap-1">
                          <Clock className="w-4 h-4" />
                          검토 중
                        </span>
                      ) : (
                        <span className="text-red-600 flex items-center gap-1">
                          <XCircle className="w-4 h-4" />
                          인증 거부됨
                        </span>
                      )}
                    </p>
                  </div>
                </div>
                {!verification && (
                  <Button
                    className="bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4]"
                    onClick={() => {
                      // Navigate to verification page
                      window.location.href = "/verification";
                    }}
                  >
                    인증 시작하기
                  </Button>
                )}
              </div>
            </Card>
          )}

          {/* Stats */}
          {stats && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
              <Card className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-blue-100 dark:bg-blue-900 flex items-center justify-center">
                    <Users className="w-5 h-5 text-blue-600 dark:text-blue-400" />
                  </div>
                  <div>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      대기 중
                    </p>
                    <p className="text-2xl font-bold">
                      {stats.total_waiting || 0}
                    </p>
                  </div>
                </div>
              </Card>
              <Card className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-green-100 dark:bg-green-900 flex items-center justify-center">
                    <Heart className="w-5 h-5 text-green-600 dark:text-green-400" />
                  </div>
                  <div>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      오늘 매칭
                    </p>
                    <p className="text-2xl font-bold">
                      {stats.total_matched || 0}
                    </p>
                  </div>
                </div>
              </Card>
              <Card className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
                    <TrendingUp className="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  </div>
                  <div>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      전체 풀
                    </p>
                    <p className="text-2xl font-bold">{stats.total_all || 0}</p>
                  </div>
                </div>
              </Card>
              <Card className="p-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-lg bg-[#FCE7F5] dark:bg-[#F9A8D4]/20 flex items-center justify-center">
                    <Shield className="w-5 h-5 text-[#F9A8D4] dark:text-[#F9A8D4]" />
                  </div>
                  <div>
                    <p className="text-sm text-slate-600 dark:text-slate-400">
                      인증 사용자
                    </p>
                    <p className="text-2xl font-bold">100%</p>
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Main Content */}
          {!isVerified ? (
            <EmptyState
              icon={Shield}
              title="인증이 필요합니다"
              description="매칭 시스템을 이용하려면 먼저 학생 인증을 완료해주세요"
              action={
                <Button
                  className="bg-gradient-to-r from-blue-600 to-purple-600"
                  onClick={() => {
                    // Navigate to verification page
                    window.location.href = "/verification";
                  }}
                >
                  인증 시작하기
                </Button>
              }
            />
          ) : (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* My Pool */}
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Users className="w-5 h-5" />내 매칭 풀
                </h2>

                {myPool ? (
                  <div className="space-y-4">
                    <div className="p-4 bg-gradient-to-br from-[#E0F7FD] to-[#FCE7F5] dark:from-[#7ED6E8]/20 dark:to-[#F9A8D4]/20 rounded-lg">
                      <div className="flex items-start justify-between mb-3">
                        <div>
                          <p className="font-medium text-lg">
                            {myPool.university}
                          </p>
                          <p className="text-sm text-slate-600 dark:text-slate-400">
                            {myPool.department} · {myPool.member_count}명
                          </p>
                        </div>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium ${
                            myPool.status === "waiting"
                              ? "bg-yellow-100 text-yellow-700"
                              : myPool.status === "matched"
                                ? "bg-green-100 text-green-700"
                                : "bg-slate-100 text-slate-700"
                          }`}
                        >
                          {myPool.status === "waiting"
                            ? "대기 중"
                            : myPool.status === "matched"
                              ? "매칭 완료"
                              : myPool.status}
                        </span>
                      </div>
                      <p className="text-sm text-slate-700 dark:text-slate-300 mb-3">
                        {myPool.description || "설명 없음"}
                      </p>
                      <div className="flex gap-2">
                        <span className="px-2 py-1 bg-white dark:bg-slate-800 rounded text-xs">
                          {myPool.matching_type === "blind"
                            ? "🎭 블라인드"
                            : "👀 공개"}
                        </span>
                        <span className="px-2 py-1 bg-white dark:bg-slate-800 rounded text-xs">
                          {myPool.age_range_min}-{myPool.age_range_max}세
                        </span>
                      </div>
                    </div>

                    {myPool.status === "waiting" && (
                      <Button
                        variant="outline"
                        className="w-full"
                        onClick={() =>
                          cancelPoolMutation.mutate(myPool.pool_id)
                        }
                        disabled={cancelPoolMutation.isPending}
                      >
                        풀 취소하기
                      </Button>
                    )}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Users className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                    <p className="text-slate-600 dark:text-slate-400 mb-4">
                      아직 매칭 풀이 없습니다
                    </p>
                    <Button
                      className="bg-gradient-to-r from-[#7ED6E8] to-[#F9A8D4]"
                      onClick={() => setShowPoolForm(true)}
                    >
                      풀 생성하기
                    </Button>
                  </div>
                )}
              </Card>

              {/* Proposals */}
              <Card className="p-6">
                <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                  <Heart className="w-5 h-5" />
                  매칭 제안
                </h2>

                {proposals.length === 0 ? (
                  <div className="text-center py-8">
                    <Heart className="w-12 h-12 mx-auto mb-3 text-slate-300" />
                    <p className="text-slate-600 dark:text-slate-400">
                      아직 매칭 제안이 없습니다
                    </p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {proposals.map((proposal) => (
                      <div
                        key={proposal.proposal_id}
                        className="p-4 border border-slate-200 dark:border-slate-700 rounded-lg"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <p className="font-medium">새로운 매칭 제안</p>
                            <p className="text-sm text-slate-600 dark:text-slate-400">
                              {new Date(
                                proposal.created_at
                              ).toLocaleDateString()}
                            </p>
                          </div>
                          <span
                            className={`px-2 py-1 rounded text-xs font-medium ${
                              proposal.final_status === "pending"
                                ? "bg-yellow-100 text-yellow-700"
                                : proposal.final_status === "matched"
                                  ? "bg-green-100 text-green-700"
                                  : "bg-red-100 text-red-700"
                            }`}
                          >
                            {proposal.final_status === "pending"
                              ? "대기 중"
                              : proposal.final_status === "matched"
                                ? "매칭 완료"
                                : "거절됨"}
                          </span>
                        </div>

                        {proposal.final_status === "pending" && (
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              className="flex-1 bg-gradient-to-r from-green-600 to-emerald-600"
                              onClick={() =>
                                respondMutation.mutate({
                                  proposalId: proposal.proposal_id,
                                  action: "accept",
                                })
                              }
                              disabled={respondMutation.isPending}
                            >
                              수락
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              className="flex-1"
                              onClick={() =>
                                respondMutation.mutate({
                                  proposalId: proposal.proposal_id,
                                  action: "reject",
                                })
                              }
                              disabled={respondMutation.isPending}
                            >
                              거절
                            </Button>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </Card>
            </div>
          )}
        </div>

        {/* Create Pool Dialog */}
        <CreatePoolDialog
          open={showPoolForm}
          onOpenChange={setShowPoolForm}
          onSubmit={async (data) => {
            await createPoolMutation.mutateAsync(data);
          }}
        />
      </div>
    </PageTransition>
  );
}
