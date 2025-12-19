import { useMemo } from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { MatchingStatsPage } from "../pages/MatchingStats";
import { authService } from "../features/auth/services/authService";
import { matchingApi } from "../api/matching";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { ArrowLeft } from "lucide-react";
import type { MatchingProposal, MatchingPool } from "../types/matching";

export const Route = createFileRoute("/matching/stats")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  loader: async () => {
    const user = authService.getCurrentUser();
    if (!user?.id) {
      throw redirect({ to: "/login" });
    }

    try {
      const stats = await matchingApi.getComprehensiveStats();
      return { stats };
    } catch (error: any) {
      console.error("Failed to load matching stats:", error);
      return { stats: null };
    }
  },
  component: MatchingStatsComponent,
});

function MatchingStatsComponent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const initialData = Route.useLoaderData();

  // 데모 모드 체크: 쿼리 캐시에서 데모 데이터 확인
  const demoProposals = queryClient.getQueryData<MatchingProposal[]>(["matching", "proposals"]) || [];
  const demoPool = queryClient.getQueryData<MatchingPool>(["matching", "myPool"]);
  const isDemo = demoProposals.some(p => p.proposal_id.startsWith("demo-")) ||
                 (demoPool && demoPool.pool_id.startsWith("demo-"));

  // 데모 모드 통계 생성 (실시간으로 업데이트되도록 useMemo 사용)
  const demoStats = useMemo(() => {
    if (!isDemo) return null;

    const matchedCount = demoProposals.filter(p => p.final_status === "matched").length;
    const pendingCount = demoProposals.filter(p => p.final_status === "pending").length;
    const rejectedCount = demoProposals.filter(p => p.final_status === "rejected").length;
    const totalProposals = demoProposals.length;

    return {
      pools: {
        total_waiting: demoPool ? 1 : 0,
        total_all: 1,
        total_matched: matchedCount,
        total_expired: 0,
        by_status: {
          waiting: demoPool ? 1 : 0,
          matched: matchedCount,
        },
        by_member_count: { "3": 1 },
        by_gender: { mixed: 1 },
        by_department: {},
        by_matching_type: { open: 1 },
        average_wait_time_hours: 2.5,
      },
      proposals: {
        total_proposals: totalProposals,
        by_status: {
          pending: pendingCount,
          matched: matchedCount,
          rejected: rejectedCount,
        },
        matched_count: matchedCount,
        success_rate: totalProposals > 0
          ? (matchedCount / totalProposals) * 100
          : 0,
        acceptance_rate: totalProposals > 0
          ? (demoProposals.filter(p => p.group_a_status === "accepted" || p.group_b_status === "accepted").length / totalProposals) * 100
          : 0,
        rejection_rate: totalProposals > 0
          ? (rejectedCount / totalProposals) * 100
          : 0,
        pending_count: pendingCount,
        average_matching_time_hours: 1.5,
        min_matching_time_hours: 0.5,
        max_matching_time_hours: 3.0,
        daily_matches: [],
        weekly_matches: [],
        monthly_matches: [],
      },
    };
  }, [isDemo, demoProposals, demoPool]);

  const { data: stats, isLoading } = useQuery({
    queryKey: ["matching", "comprehensive-stats"],
    queryFn: () => matchingApi.getComprehensiveStats(),
    initialData: initialData.stats,
    refetchInterval: 30000, // Refresh every 30 seconds
    enabled: !isDemo, // 데모 모드에서는 API 호출 안 함
  });

  const displayStats = isDemo ? demoStats : stats;

  if (isLoading && !displayStats) {
    return (
      <PageTransition>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-muted-foreground">통계를 불러오는 중...</div>
        </div>
      </PageTransition>
    );
  }

  if (!displayStats) {
    return (
      <PageTransition>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-muted-foreground">통계를 불러올 수 없습니다.</div>
        </div>
      </PageTransition>
    );
  }

  return (
    <PageTransition>
      <div className="space-y-6">
        {/* 뒤로가기 버튼 */}
        <Button
          variant="ghost"
          onClick={() => navigate({ to: "/matching" })}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          뒤로가기
        </Button>

        {/* 데모 모드 안내 */}
        {isDemo && (
          <div className="p-4 bg-pink-50 dark:bg-pink-950/20 border border-pink-200 dark:border-pink-800 rounded-lg">
            <p className="text-sm text-pink-700 dark:text-pink-300">
              🎮 데모 모드: 이 통계는 실제 데이터베이스와 연동되지 않습니다.
            </p>
          </div>
        )}

        <MatchingStatsPage stats={displayStats} />
      </div>
    </PageTransition>
  );
}

