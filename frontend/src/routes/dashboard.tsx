import React from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { DashboardPage } from "../pages/Dashboard";
import { PageTransition } from "../components/PageTransition";
import { authService } from "../features/auth/services/authService";
import { statsService } from "../features/stats/services/statsService";

export const Route = createFileRoute("/dashboard")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      throw redirect({ to: "/login" });
    }
  },
  loaderDeps: () => ({
    userId: authService.getCurrentUser()?.id || "",
    days: 7, // Dashboard는 최근 7일 데이터 사용
  }),
  loader: async ({ deps }) => {
    if (!deps.userId) {
      throw new Error("User not authenticated");
    }
    const response = await statsService.getUserStats(deps.userId, deps.days);
    if (response.status === "error") {
      throw new Error(response.error?.message || "Failed to load dashboard stats");
    }
    return response.data!;
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



