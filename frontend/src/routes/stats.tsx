import React from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { StatsPage } from "../pages/Stats";
import { authService } from "../features/auth/services/authService";
import { statsService } from "../features/stats/services/statsService";
import { PageTransition } from "../components/PageTransition";

export const Route = createFileRoute("/stats")({
  beforeLoad: () => {
    const user = authService.getCurrentUser();
    if (!user) {
      throw redirect({ to: "/login" });
    }
  },
  component: StatsComponent,
});

function StatsComponent() {
  const user = authService.getCurrentUser();

  if (!user?.id) {
    return (
      <div className="min-h-screen bg-muted/30 flex items-center justify-center">
        <div className="text-center">
          <p className="text-destructive">로그인이 필요합니다</p>
        </div>
      </div>
    );
  }

  return (
    <PageTransition>
      <StatsPageWithData userId={user.id} />
    </PageTransition>
  );
}

function StatsPageWithData({ userId }: { userId: string }) {
  const user = authService.getCurrentUser();
  const isAdmin = authService.isAdmin();

  // 기본 통계 데이터 (최근 7일)
  // Admin can access even with no data
  const { data: basicStats, isLoading: isLoadingBasic } = useQuery({
    queryKey: ["stats", "basic", userId, 7],
    queryFn: async () => {
      const response = await statsService.getUserStats(userId, 7);
      if (response.status === "error") {
        // Admin can proceed with empty data
        if (isAdmin) {
          return {
            total_focus_time: 0,
            total_sessions: 0,
            average_session: 0,
            sessions: [],
          };
        }
        throw new Error(response.error?.message || "Failed to load stats");
      }
      return response.data!;
    },
    staleTime: 1000 * 60, // 1 minute
  });

  // 시간대별 패턴 (최근 30일)
  const { data: hourlyPattern, isLoading: isLoadingHourly } = useQuery({
    queryKey: ["stats", "hourly-pattern", userId, 30],
    queryFn: async () => {
      const response = await statsService.getHourlyPattern(userId, 30);
      if (response.status === "error") {
        // Admin can proceed with empty data
        if (isAdmin) {
          return {
            hourly_focus_time: Array(24).fill(0),
            total_days: 0,
            peak_hour: null,
          };
        }
        throw new Error(
          response.error?.message || "Failed to load hourly pattern"
        );
      }
      return response.data!;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // 월별 비교 (최근 12개월)
  const { data: monthlyComparison, isLoading: isLoadingMonthly } = useQuery({
    queryKey: ["stats", "monthly-comparison", userId, 12],
    queryFn: async () => {
      const response = await statsService.getMonthlyComparison(userId, 12);
      if (response.status === "error") {
        // Admin can proceed with empty data
        if (isAdmin) {
          return {
            monthly_data: [],
            total_months: 0,
          };
        }
        throw new Error(
          response.error?.message || "Failed to load monthly comparison"
        );
      }
      return response.data!;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  // 목표 달성률 (주간, 월간, 연간)
  const { data: weeklyGoal, isLoading: isLoadingWeeklyGoal } = useQuery({
    queryKey: ["stats", "goal", userId, "focus_time", 30, "week"],
    queryFn: async () => {
      const response = await statsService.getGoalAchievement(
        userId,
        "focus_time",
        30,
        "week"
      );
      if (response.status === "error") {
        throw new Error(
          response.error?.message || "Failed to load weekly goal"
        );
      }
      return response.data!;
    },
    staleTime: 1000 * 60, // 1 minute
  });

  const { data: monthlyGoal, isLoading: isLoadingMonthlyGoal } = useQuery({
    queryKey: ["stats", "goal", userId, "focus_time", 120, "month"],
    queryFn: async () => {
      const response = await statsService.getGoalAchievement(
        userId,
        "focus_time",
        120,
        "month"
      );
      if (response.status === "error") {
        // Admin can proceed with empty data
        if (isAdmin) {
          return {
            goal_type: "focus_time",
            goal_value: 120,
            current_value: 0,
            achievement_rate: 0,
            period: "month",
            is_achieved: false,
            remaining: 120,
          };
        }
        throw new Error(
          response.error?.message || "Failed to load monthly goal"
        );
      }
      return response.data!;
    },
    staleTime: 1000 * 60, // 1 minute
  });

  const { data: yearlyGoal, isLoading: isLoadingYearlyGoal } = useQuery({
    queryKey: ["stats", "goal", userId, "focus_time", 1000, "month"],
    queryFn: async () => {
      // 연간 목표는 월간 API를 사용하되 더 큰 목표값 사용
      const response = await statsService.getGoalAchievement(
        userId,
        "focus_time",
        1000,
        "month"
      );
      if (response.status === "error") {
        throw new Error(
          response.error?.message || "Failed to load yearly goal"
        );
      }
      return response.data!;
    },
    staleTime: 1000 * 60, // 1 minute
  });

  const isLoading =
    isLoadingBasic ||
    isLoadingHourly ||
    isLoadingMonthly ||
    isLoadingWeeklyGoal ||
    isLoadingMonthlyGoal ||
    isLoadingYearlyGoal;

  if (isLoading) {
    return (
      <div className="min-h-screen bg-muted/30 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <StatsPage
      basicStats={basicStats}
      hourlyPattern={hourlyPattern}
      monthlyComparison={monthlyComparison}
      weeklyGoal={weeklyGoal}
      monthlyGoal={monthlyGoal}
      yearlyGoal={yearlyGoal}
      userId={userId}
    />
  );
}
