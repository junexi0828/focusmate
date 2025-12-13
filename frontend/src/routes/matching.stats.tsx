import React from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { MatchingStatsPage } from "../pages/MatchingStats";
import { authService } from "../features/auth/services/authService";
import { matchingApi } from "../api/matching";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";

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
  const initialData = Route.useLoaderData();

  const { data: stats, isLoading } = useQuery({
    queryKey: ["matching", "comprehensive-stats"],
    queryFn: () => matchingApi.getComprehensiveStats(),
    initialData: initialData.stats,
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  if (isLoading && !stats) {
    return (
      <PageTransition>
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-muted-foreground">통계를 불러오는 중...</div>
        </div>
      </PageTransition>
    );
  }

  if (!stats) {
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
      <MatchingStatsPage stats={stats} />
    </PageTransition>
  );
}

