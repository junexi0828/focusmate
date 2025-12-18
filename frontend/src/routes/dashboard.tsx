import React from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { DashboardPage } from "../pages/Dashboard";
import { PageTransition } from "../components/PageTransition";
import { authService } from "../features/auth/services/authService";
import { statsService } from "../features/stats/services/statsService";
import { ErrorDisplay } from "../components/ErrorDisplay";
import { toast } from "sonner";

export const Route = createFileRoute("/dashboard")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  loaderDeps: () => ({
    userId: authService.getCurrentUser()?.id || "",
    days: 7, // Dashboard는 최근 7일 데이터 사용
  }),
  loader: async ({ deps }) => {
    if (!deps.userId) {
      console.error("[Dashboard] No user ID available");
      throw new Error("User not authenticated");
    }

    console.log("[Dashboard] Loading stats for user:", deps.userId);
    const response = await statsService.getUserStats(deps.userId, deps.days);

    if (response.status === "error") {
      console.error("[Dashboard] Stats API error:", response.error);
      throw new Error(response.error?.message || "Failed to load dashboard stats");
    }

    console.log("[Dashboard] Stats loaded successfully:", response.data);
    return response.data!;
  },
  errorComponent: ({ error }) => {
    const isAuthError = error?.message?.includes("authenticated");

    if (isAuthError) {
      return (
        <PageTransition>
          <div className="min-h-screen bg-muted/30 flex items-center justify-center">
            <div className="text-center space-y-4 p-8 bg-card rounded-lg shadow-lg max-w-md">
              <h2 className="text-2xl font-bold">대시보드</h2>
              <p className="text-muted-foreground">
                대시보드 기능을 사용하려면 로그인이 필요합니다
              </p>
              <button
                onClick={() => window.location.href = "/login"}
                className="px-6 py-2 bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors font-medium"
              >
                로그인하기
              </button>
            </div>
          </div>
        </PageTransition>
      );
    }

    return (
      <PageTransition>
        <div className="container mx-auto p-6">
          <ErrorDisplay
            error={error as Error}
            title="대시보드 로드 실패"
            onRetry={() => window.location.reload()}
          />
        </div>
      </PageTransition>
    );
  },
  component: DashboardComponent,
});

function DashboardComponent() {
  const user = authService.getCurrentUser();
  const initialStats = Route.useLoaderData();

  // TanStack Query로 데이터 캐싱 및 실시간 업데이트
  const { data, isLoading, error } = useQuery({
    queryKey: ["dashboard", "stats", user?.id, 7],
    queryFn: async () => {
      if (!user?.id) throw new Error("User not authenticated");
      const response = await statsService.getUserStats(user.id, 7);
      if (response.status === "error") {
        throw new Error(response.error?.message || "Failed to load dashboard stats");
      }
      return response.data!;
    },
    initialData: initialStats,
    staleTime: 1000 * 60, // 1분간 캐시 유지
    refetchOnWindowFocus: true, // 창 포커스 시 자동 리패치
  });

  return (
    <PageTransition>
      <DashboardPage stats={data} isLoading={isLoading} error={error} />
    </PageTransition>
  );
}



