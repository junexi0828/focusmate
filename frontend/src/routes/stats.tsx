import { createFileRoute, redirect } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { StatsPage } from "../pages/Stats";
import { authService } from "../features/auth/services/authService";
import { statsService } from "../features/stats/services/statsService";
import { PageTransition } from "../components/PageTransition";
import { StatsPageSkeleton } from "../components/ui/stats-skeleton";
import { ErrorDisplay } from "../components/ErrorDisplay";
import { toast } from "sonner";

export const Route = createFileRoute("/stats")({
  beforeLoad: () => {
    const user = authService.getCurrentUser();
    if (!user) {
      console.log("[Stats] No user found, redirecting to login");
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
    console.log("[Stats] User authenticated:", user.id);
  },
  component: StatsComponent,
});

function StatsComponent() {
  const user = authService.getCurrentUser();

  return (
    <PageTransition>
      <StatsPageWithData userId={user!.id} />
    </PageTransition>
  );
}

function StatsPageWithData({ userId }: { userId: string }) {
  const isAdmin = authService.isAdmin();

  // 기본 통계 데이터 (최근 7일)
  // Admin can access even with no data
  const { data: basicStats, isLoading: isLoadingBasic, error: basicError } = useQuery({
    queryKey: ["stats", "basic", userId, 7],
    queryFn: async () => {
      console.log("[Stats] Loading basic stats for user:", userId);
      const response = await statsService.getUserStats(userId, 7);
      if (response.status === "error") {
        console.error("[Stats] Basic stats error:", response.error);
        // Admin can proceed with empty data
        if (isAdmin) {
          console.log("[Stats] Admin user, returning empty data");
          return {
            totalFocusTime: 0,
            totalSessions: 0,
            averageSession: 0,
            sessions: [],
          };
        }
        throw new Error(response.error?.message || "Failed to load stats");
      }
      console.log("[Stats] Basic stats loaded:", response.data);
      return response.data!;
    },
    staleTime: 1000 * 60, // 1 minute
  });

  // 시간대별 패턴 (최근 30일)
  const { data: hourlyPattern, isLoading: isLoadingHourly } = useQuery({
    queryKey: ["stats", "hourly-pattern", userId, 30],
    queryFn: async () => {
      // Get timezone offset in hours
      const offsetHours = Math.round(new Date().getTimezoneOffset() / -60);
      const response = await statsService.getHourlyPattern(userId, 30, offsetHours);
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

  // 유저 목표 정보 조회
  const { data: userGoal } = useQuery({
    queryKey: ["user-goal", userId],
    queryFn: () => statsService.getGoal(),
    enabled: !!userId,
  });

  // 목표 달성률 (주간, 월간, 연간)
  const { data: weeklyGoal, isLoading: isLoadingWeeklyGoal } = useQuery({
    queryKey: ["stats", "goal", userId, "focus_time", userGoal?.data?.daily_goal_minutes, "week"],
    queryFn: async () => {
      const targetMinutes = userGoal?.data?.daily_goal_minutes ? userGoal.data.daily_goal_minutes * 7 : 120 * 7;
      const response = await statsService.getGoalAchievement(
        userId,
        "focus_time",
        targetMinutes,
        "week"
      );
      if (response.status === "error") {
        throw new Error(
          response.error?.message || "Failed to load weekly goal"
        );
      }
      return response.data!;
    },
    enabled: !!userId,
    staleTime: 1000 * 60, // 1 minute
  });

  const { data: monthlyGoal, isLoading: isLoadingMonthlyGoal } = useQuery({
    queryKey: ["stats", "goal", userId, "focus_time", userGoal?.data?.daily_goal_minutes, "month"],
    queryFn: async () => {
      const targetMinutes = userGoal?.data?.daily_goal_minutes ? userGoal.data.daily_goal_minutes * 30 : 120 * 30;
      const response = await statsService.getGoalAchievement(
        userId,
        "focus_time",
        targetMinutes,
        "month"
      );
      if (response.status === "error") {
        // Admin can proceed with empty data
        if (isAdmin) {
          return {
            goal_type: "focus_time",
            goal_value: targetMinutes,
            current_value: 0,
            achievement_rate: 0,
            period: "month",
            is_achieved: false,
            remaining: targetMinutes,
          } as any;
        }
        throw new Error(
          response.error?.message || "Failed to load monthly goal"
        );
      }
      return response.data!;
    },
    enabled: !!userId,
    staleTime: 1000 * 60, // 1 minute
  });

  const { data: yearlyGoal, isLoading: isLoadingYearlyGoal } = useQuery({
    queryKey: ["stats", "goal", userId, "focus_time", userGoal?.data?.daily_goal_minutes, "year"],
    queryFn: async () => {
      const targetMinutes = userGoal?.data?.daily_goal_minutes ? userGoal.data.daily_goal_minutes * 365 : 120 * 365;
      // 연간 목표는 월간 API를 사용하되 더 큰 목표값 사용
      const response = await statsService.getGoalAchievement(
        userId,
        "focus_time",
        targetMinutes,
        "month"
      );
      if (response.status === "error") {
        throw new Error(
          response.error?.message || "Failed to load yearly goal"
        );
      }
      return response.data!;
    },
    enabled: !!userId,
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
      <PageTransition>
        <StatsPageSkeleton />
      </PageTransition>
    );
  }

  // Show error if basic stats failed and user is not admin
  if (basicError && !isAdmin) {
    return (
      <PageTransition>
        <div className="container mx-auto p-6">
          <ErrorDisplay
            error={basicError as Error}
            title="통계 데이터 로드 실패"
            onRetry={() => window.location.reload()}
          />
        </div>
      </PageTransition>
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
