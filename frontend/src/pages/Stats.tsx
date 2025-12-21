import { useState, useMemo } from "react";
import { motion } from "framer-motion";
import { Clock, Target, TrendingUp, Award, Flame, Settings } from "lucide-react";
import { DateRange } from "react-day-picker";
import { PageTransition, staggerContainer, staggerItem } from "../components/PageTransition";
import { Button } from "../components/ui/button-enhanced";
import { WeeklyActivityChart } from "../components/charts/WeeklyActivityChart";
import { ActivityHeatMap } from "../components/charts/ActivityHeatMap";
import { HourlyPatternChart } from "../components/charts/HourlyPatternChart";
import { MonthlyComparisonChart } from "../components/charts/MonthlyComparisonChart";
import { GoalProgressRing } from "../components/charts/GoalProgressRing";
import { ChartFilters } from "../components/ChartFilters";
import { GoalSettingModal } from "../components/GoalSettingModal";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { statsService } from "../features/stats/services/statsService";
import { achievementService } from "../features/achievements/services/achievementService";
import { calculateDailyStats } from "../utils/stats-calculator";
import { transformSessionRecordsForStats } from "../utils/api-transformers";
import { toast } from "sonner";
import type {
  UserStatsResponse,
  HourlyPatternResponse,
  MonthlyComparisonResponse,
  GoalAchievementResponse,
} from "../features/stats/services/statsService";

interface StatsPageProps {
  basicStats?: UserStatsResponse;
  hourlyPattern?: HourlyPatternResponse;
  monthlyComparison?: MonthlyComparisonResponse;
  weeklyGoal?: GoalAchievementResponse;
  monthlyGoal?: GoalAchievementResponse;
  yearlyGoal?: GoalAchievementResponse;
  userId: string;
}

export function StatsPage({
  basicStats,
  hourlyPattern,
  monthlyComparison,
  weeklyGoal,
  monthlyGoal,
  yearlyGoal,
  userId,
}: StatsPageProps) {
  const queryClient = useQueryClient();
  const [filters, setFilters] = useState<{
    sessionType: string[];
    dateRange?: DateRange;
  }>({ sessionType: ["all"] });
  const [isGoalModalOpen, setIsGoalModalOpen] = useState(false);

  // Fetch user goals
  const { data: userGoal } = useQuery({
    queryKey: ["user-goal", userId],
    queryFn: () => statsService.getGoal(),
    enabled: !!userId && !!localStorage.getItem("access_token"), // Only fetch when authenticated
    retry: false, // Don't retry if 404 (no goals set yet)
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });

  // Fetch user achievements progress
  const { data: achievementsData, isLoading: achievementsLoading } = useQuery({
    queryKey: ["user-achievements", userId],
    queryFn: async () => {
      try {
        const response = await achievementService.getUserAchievementProgress(userId);
        if (response.status === "error") {
          console.error("Achievement progress error:", response.error);
          return [];
        }
        // Transform backend response to match frontend interface
        const data = response.data || [];
        return data.map((item: any) => ({
          achievement_id: item.achievement?.id || item.achievement_id,
          achievement_name: item.achievement?.name || item.achievement_name,
          achievement_description: item.achievement?.description || item.achievement_description,
          achievement_icon: item.achievement?.icon || item.achievement_icon,
          achievement_category: item.achievement?.category || item.achievement_category,
          requirement_type: item.achievement?.requirement_type || item.requirement_type,
          requirement_value: item.achievement?.requirement_value || item.requirement_value,
          current_progress: item.progress || item.current_progress,
          is_unlocked: item.is_unlocked,
          progress_percentage: item.progress_percentage,
        }));
      } catch (error) {
        console.error("Failed to fetch achievements:", error);
        return [];
      }
    },
    enabled: !!userId,
    staleTime: 1000 * 60 * 5, // 5 minutes
    refetchOnWindowFocus: false,
  });

  // Save goal mutation
  const saveGoalMutation = useMutation({
    mutationFn: (data: { daily_goal_minutes: number; weekly_goal_sessions: number }) =>
      statsService.saveGoal(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["user-goal", userId] });
      queryClient.invalidateQueries({ queryKey: ["stats", "goal"] });
      toast.success("목표가 저장되었습니다");
      setIsGoalModalOpen(false);
    },
    onError: (error: any) => {
      toast.error(error?.message || "목표 저장에 실패했습니다");
    },
  });

  // 필터에 따른 통계 데이터 조회
  const { data: filteredStats } = useQuery({
    queryKey: [
      "stats",
      "filtered",
      userId,
      filters.dateRange?.from,
      filters.dateRange?.to,
    ],
    queryFn: async () => {
      if (filters.dateRange?.from && filters.dateRange?.to) {
        const startDate = filters.dateRange.from.toISOString().split("T")[0];
        const endDate = filters.dateRange.to.toISOString().split("T")[0];
        const response = await statsService.getUserStats(
          userId,
          undefined,
          startDate,
          endDate
        );
        if (response.status === "error") {
          throw new Error(response.error?.message || "Failed to load filtered stats");
        }
        return response.data!;
      }
      return basicStats;
    },
    enabled: !!basicStats,
    staleTime: 1000 * 60 * 2, // 2 minutes
    refetchOnWindowFocus: false,
  });

  const stats = filteredStats || basicStats;

  // 세션 타입 필터링 적용
  const filteredSessions = useMemo(() => {
    if (!stats?.sessions) return [];

    let sessions = stats.sessions;

    // 세션 타입 필터링
    if (filters.sessionType && filters.sessionType.length > 0 && !filters.sessionType.includes("all")) {
      sessions = sessions.filter((s) => {
        const sessionType = s.sessionType || "work";
        const duration = s.durationMinutes || 0;

        // 세션 타입 매칭
        if (filters.sessionType.includes("break") && sessionType === "break") {
          return true;
        }
        if (filters.sessionType.includes("pomodoro") && sessionType === "work" && duration >= 20 && duration <= 30) {
          return true;
        }
        if (filters.sessionType.includes("short") && sessionType === "work" && duration < 20) {
          return true;
        }
        if (filters.sessionType.includes("long") && sessionType === "work" && duration > 30) {
          return true;
        }
        return false;
      });
    }

    return sessions;
  }, [stats, filters.sessionType]);

  // 주간 활동 데이터 변환
  const weeklyStats = useMemo(() => {
    if (!filteredSessions || filteredSessions.length === 0) return [];

    const sessionsForStats = transformSessionRecordsForStats(filteredSessions);
    const dailyStats = calculateDailyStats(sessionsForStats);

    // 최근 7일 데이터
    const recentDays = dailyStats.slice(-7);
    const dayNames = ["일", "월", "화", "수", "목", "금", "토"];

    return recentDays.map((day) => {
      const date = new Date(day.date);
      const dayName = dayNames[date.getDay()];
      const daySessions = filteredSessions.filter((s) => {
        const sessionDate = new Date(s.completedAt).toISOString().split("T")[0];
        return sessionDate === day.date && s.sessionType === "work";
      });

      return {
        day: dayName,
        hours: roundToDecimal(day.focusTime / 60, 1),
        sessions: daySessions.length,
      };
    });
  }, [filteredSessions]);

  // 히트맵 데이터 변환 (최근 12주)
  const heatmapData = useMemo(() => {
    if (!filteredSessions || filteredSessions.length === 0) return [];

    const sessionsForStats = transformSessionRecordsForStats(filteredSessions);
    const dailyStats = calculateDailyStats(sessionsForStats);

    // 최근 12주 데이터 구성
    const weeks: Array<{ week: number; days: Array<{ day: string; hours: number }> }> = [];
    const dayNames = ["월", "화", "수", "목", "금", "토", "일"];

    for (let weekIndex = 0; weekIndex < 12; weekIndex++) {
      const weekStart = new Date();
      weekStart.setDate(weekStart.getDate() - (12 - weekIndex) * 7);
      weekStart.setDate(weekStart.getDate() - weekStart.getDay() + 1); // Monday

      const weekDays = dayNames.map((_, dayIndex) => {
        const dayDate = new Date(weekStart);
        dayDate.setDate(dayDate.getDate() + dayIndex);
        const dateKey = dayDate.toISOString().split("T")[0];

        const dayStat = dailyStats.find((d) => d.date === dateKey);
        const hours = dayStat ? roundToDecimal(dayStat.focusTime / 60, 1) : 0;

        return {
          day: `${weekIndex + 1}/${dayIndex + 1}`,
          hours,
        };
      });

      weeks.push({ week: weekIndex, days: weekDays });
    }

    return weeks;
  }, [filteredSessions]);

  // 시간대별 패턴 데이터 변환
  const hourlyData = useMemo(() => {
    if (!hourlyPattern?.hourly_focus_time) {
      return Array.from({ length: 24 }, (_, i) => ({
        hour: `${i}`,
        sessions: 0,
        avgDuration: 0,
      }));
    }

    return hourlyPattern.hourly_focus_time.map((_, hour) => {
      // 해당 시간대의 세션 수 계산
      const hourSessions = filteredSessions.filter((s) => {
        const sessionDate = new Date(s.completedAt);
        return (
          sessionDate.getHours() === hour &&
          s.sessionType === "work"
        );
      });

      const avgDuration =
        hourSessions.length > 0
          ? hourSessions.reduce(
              (sum, s) => sum + s.durationMinutes,
              0
            ) / hourSessions.length
          : 0;

      return {
        hour: `${hour}`,
        sessions: hourSessions.length,
        avgDuration: Math.round(avgDuration),
      };
    });
  }, [hourlyPattern, filteredSessions]);

  // 월별 비교 데이터 변환
  const monthlyData = useMemo(() => {
    if (!monthlyComparison?.monthly_data) return [];

    const currentYear = new Date().getFullYear();
    const lastYear = currentYear - 1;

    // 올해와 작년 데이터 분리
    const thisYearData = monthlyComparison.monthly_data.filter(
      (m) => m.month.startsWith(String(currentYear))
    );
    const lastYearData = monthlyComparison.monthly_data.filter(
      (m) => m.month.startsWith(String(lastYear))
    );

    // 월별로 매칭
    const monthNames = [
      "1월",
      "2월",
      "3월",
      "4월",
      "5월",
      "6월",
      "7월",
      "8월",
      "9월",
      "10월",
      "11월",
      "12월",
    ];

    return monthNames.map((monthName, index) => {
      const monthKey = `${currentYear}-${String(index + 1).padStart(2, "0")}`;
      const lastYearMonthKey = `${lastYear}-${String(index + 1).padStart(2, "0")}`;

      const thisYearMonth = thisYearData.find((m) => m.month === monthKey);
      const lastYearMonth = lastYearData.find((m) => m.month === lastYearMonthKey);

      return {
        month: monthName,
        thisYear: thisYearMonth ? roundToDecimal(thisYearMonth.focus_time_hours, 1) : 0,
        lastYear: lastYearMonth ? roundToDecimal(lastYearMonth.focus_time_hours, 1) : 0,
      };
    });
  }, [monthlyComparison]);

  // 헬퍼 함수
  function roundToDecimal(num: number, decimals: number): number {
    return Math.round(num * Math.pow(10, decimals)) / Math.pow(10, decimals);
  }

  // 아이콘 매핑 함수
  const getAchievementIcon = (iconName: string | null | undefined) => {
    if (!iconName || typeof iconName !== 'string') {
      return Award; // 기본값 반환
    }

    switch (iconName.toLowerCase()) {
      case "flame":
      case "streak":
        return Flame;
      case "target":
      case "focus":
        return Target;
      case "award":
      case "trophy":
      case "medal":
        return Award;
      case "trending-up":
      case "growth":
        return TrendingUp;
      case "clock":
      case "time":
        return Clock;
      default:
        return Award;
    }
  };

  const achievements = useMemo(() => {
    if (!achievementsData || achievementsData.length === 0) {
      // 데이터가 없는 경우 기본값 표시 (가이드용)
      return [
        {
          icon: Flame,
          title: "첫 걸음",
          description: "첫 집중 세션을 완료하세요",
          unlocked: false,
        },
      ];
    }

    return achievementsData.map((a: any) => ({
      icon: getAchievementIcon(a.achievement_icon),
      title: a.achievement_name || "업적",
      description: a.achievement_description || "설명 없음",
      unlocked: a.is_unlocked || false,
    }));
  }, [achievementsData]);

  return (
    <PageTransition className="space-y-6">
      {/* Header with Filters */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">통계</h1>
          <p className="text-muted-foreground mt-1">
            당신의 집중 패턴을 분석해보세요
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            onClick={() => setIsGoalModalOpen(true)}
            className="flex items-center gap-2"
          >
            <Settings className="w-4 h-4" />
            목표 설정
          </Button>
          <ChartFilters onFilterChange={setFilters} />
        </div>
      </div>

      {/* Weekly Overview */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="grid gap-4 md:grid-cols-3"
      >
        <StatCard
          icon={Clock}
          label="이번 주 총 시간"
          value={
            filteredSessions.length > 0
              ? `${roundToDecimal(
                  filteredSessions
                    .filter((s) => s.sessionType === "work")
                    .reduce(
                      (sum, s) =>
                        sum + s.durationMinutes,
                      0
                    ) / 60,
                  1
                )}h`
              : "0h"
          }
          change={
            filteredSessions.length > 0
              ? `${filteredSessions.filter((s) => s.sessionType === "work").length}개 세션`
              : "데이터 없음"
          }
          trend={filteredSessions.length > 0 ? "up" : "neutral"}
        />
        <StatCard
          icon={Target}
          label="완료한 세션"
          value={filteredSessions.filter((s) => s.sessionType === "work").length.toString()}
          change={
            filteredSessions.length > 0
              ? `평균 ${Math.round(
                  filteredSessions
                    .filter((s) => s.sessionType === "work")
                    .reduce(
                      (sum, s) =>
                        sum + s.durationMinutes,
                      0
                    ) /
                    Math.max(
                      1,
                      filteredSessions.filter((s) => s.sessionType === "work").length
                    )
                )}분`
              : "시작해보세요"
          }
          trend={filteredSessions.length > 0 ? "up" : "neutral"}
        />
        <StatCard
          icon={TrendingUp}
          label="일일 평균"
          value={
            filteredSessions.length > 0
              ? `${roundToDecimal(
                    filteredSessions
                    .filter((s) => s.sessionType === "work")
                    .reduce(
                      (sum, s) =>
                        sum + s.durationMinutes,
                      0
                    ) /
                    Math.max(
                      1,
                      filteredSessions.filter((s) => s.sessionType === "work").length
                    ) /
                    60,
                  1
                )}h`
              : "0h"
          }
          change={
            filteredSessions.length > 0
              ? `${filteredSessions.filter((s) => s.sessionType === "work").length}개 세션`
              : "데이터 없음"
          }
          trend={filteredSessions.length > 0 ? "up" : "neutral"}
        />
      </motion.div>

      {/* Goal Progress */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15 }}
        className="grid gap-6 md:grid-cols-3"
      >
        <div className="rounded-xl border border-border bg-card p-6">
          <h3 className="text-lg font-semibold mb-4">주간 목표</h3>
          {weeklyGoal ? (
            <GoalProgressRing
              current={roundToDecimal(weeklyGoal.current_value / 60, 1)}
              goal={weeklyGoal.goal_value / 60}
              label="주간 목표"
            />
          ) : (
            <div className="h-[250px] flex items-center justify-center text-muted-foreground">
              데이터 로딩 중...
            </div>
          )}
        </div>
        <div className="rounded-xl border border-border bg-card p-6">
          <h3 className="text-lg font-semibold mb-4">월간 목표</h3>
          {monthlyGoal ? (
            <GoalProgressRing
              current={roundToDecimal(monthlyGoal.current_value / 60, 1)}
              goal={monthlyGoal.goal_value / 60}
              label="월간 목표"
            />
          ) : (
            <div className="h-[250px] flex items-center justify-center text-muted-foreground">
              데이터 로딩 중...
            </div>
          )}
        </div>
        <div className="rounded-xl border border-border bg-card p-6">
          <h3 className="text-lg font-semibold mb-4">연간 목표</h3>
          {yearlyGoal ? (
            <GoalProgressRing
              current={roundToDecimal(yearlyGoal.current_value / 60, 1)}
              goal={yearlyGoal.goal_value / 60}
              label="연간 목표"
            />
          ) : (
            <div className="h-[250px] flex items-center justify-center text-muted-foreground">
              데이터 로딩 중...
            </div>
          )}
        </div>
      </motion.div>

      {/* Weekly Chart */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.2 }}
        className="rounded-xl border border-border bg-card p-6"
      >
        <h3 className="text-lg font-semibold mb-4">주간 활동</h3>
        {weeklyStats.length > 0 ? (
          <WeeklyActivityChart data={weeklyStats} />
        ) : (
          <div className="h-[300px] flex items-center justify-center text-muted-foreground">
            데이터가 없습니다
          </div>
        )}
      </motion.div>

      {/* Advanced Charts Grid */}
      <div className="grid gap-6 lg:grid-cols-2">
        {/* Hourly Pattern */}
        <div className="rounded-xl border border-border bg-card p-6">
          <h3 className="text-lg font-semibold mb-2">시간대별 집중 패턴</h3>
          <p className="text-sm text-muted-foreground mb-4">
            하루 중 가장 집중이 잘 되는 시간대를 확인하세요
            {hourlyPattern?.peak_hour !== null && hourlyPattern?.peak_hour !== undefined && (
              <span className="ml-2 text-primary font-medium">
                (최적 시간: {hourlyPattern.peak_hour}시)
              </span>
            )}
          </p>
          {hourlyPattern?.hourly_focus_time ? (
            <HourlyPatternChart
              data={hourlyData}
            />
          ) : hourlyData.length > 0 && hourlyData.some((h) => h.sessions > 0) ? (
            <HourlyPatternChart data={hourlyData} />
          ) : (
            <div className="h-[400px] flex items-center justify-center text-muted-foreground">
              데이터가 없습니다
            </div>
          )}
        </div>

        {/* Monthly Comparison */}
        <div className="rounded-xl border border-border bg-card p-6">
          <h3 className="text-lg font-semibold mb-2">월별 비교</h3>
          <p className="text-sm text-muted-foreground mb-4">
            작년 대비 올해의 집중 시간 변화
          </p>
          {monthlyData.length > 0 ? (
            <MonthlyComparisonChart data={monthlyData} />
          ) : (
            <div className="h-[350px] flex items-center justify-center text-muted-foreground">
              데이터가 없습니다
            </div>
          )}
        </div>
      </div>

      {/* Activity Heatmap */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.3 }}
        className="rounded-xl border border-border bg-card p-6"
      >
        <h3 className="text-lg font-semibold mb-4">활동 히트맵</h3>
        <p className="text-sm text-muted-foreground mb-4">
          지난 12주간의 일일 집중 시간
        </p>
        {heatmapData.length > 0 ? (
          <ActivityHeatMap data={heatmapData} />
        ) : (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            데이터가 없습니다
          </div>
        )}
      </motion.div>

      {/* Achievements */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="rounded-xl border border-border bg-card p-6"
      >
        <h3 className="text-lg font-semibold mb-4">업적</h3>
        {achievementsLoading ? (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            업적을 불러오는 중...
          </div>
        ) : achievements.length === 0 ? (
          <div className="h-[200px] flex items-center justify-center text-muted-foreground">
            아직 업적이 없습니다
          </div>
        ) : (
          <motion.div
            variants={staggerContainer}
            initial="initial"
            animate="animate"
            className="grid gap-4 md:grid-cols-3"
          >
            {achievements.map((achievement, index) => (
              <AchievementCard key={index} {...achievement} />
            ))}
          </motion.div>
        )}
      </motion.div>

      {/* Goal Setting Modal */}
      <GoalSettingModal
        isOpen={isGoalModalOpen}
        onClose={() => setIsGoalModalOpen(false)}
        onSave={async (goal) => {
          // Convert hours to minutes for daily goal
          const dailyGoalMinutes = Math.round((goal.targetHours * 60) / (goal.type === "weekly" ? 7 : goal.type === "monthly" ? 30 : 365));
          const weeklyGoalSessions = goal.type === "weekly" ? Math.round(goal.targetHours / 2) : 5;

          await saveGoalMutation.mutateAsync({
            daily_goal_minutes: dailyGoalMinutes,
            weekly_goal_sessions: weeklyGoalSessions,
          });
        }}
        currentGoal={
          userGoal?.data
            ? {
                type: "weekly" as const,
                targetHours: Math.round((userGoal.data.daily_goal_minutes * 7) / 60),
              }
            : undefined
        }
      />
    </PageTransition>
  );
}

interface StatCardProps {
  icon: typeof Clock;
  label: string;
  value: string;
  change: string;
  trend: "up" | "down" | "neutral";
}

function StatCard({ icon: Icon, label, value, change, trend }: StatCardProps) {
  return (
    <div className="rounded-xl border border-border bg-card p-6 hover:border-primary/50 transition-colors">
      <div className="flex items-center justify-between mb-2">
        <span className="text-sm text-muted-foreground">{label}</span>
        <Icon className="h-4 w-4 text-primary" />
      </div>
      <div className="text-2xl font-bold">{value}</div>
      <div
        className={`text-xs mt-1 ${
          trend === "up"
            ? "text-green-600 dark:text-green-400"
            : trend === "down"
            ? "text-red-600 dark:text-red-400"
            : "text-muted-foreground"
        }`}
      >
        {change}
      </div>
    </div>
  );
}

interface AchievementCardProps {
  icon: typeof Flame;
  title: string;
  description: string;
  unlocked: boolean;
}

function AchievementCard({
  icon: Icon,
  title,
  description,
  unlocked,
}: AchievementCardProps) {
  return (
    <motion.div
      variants={staggerItem}
      whileHover={{ scale: unlocked ? 1.02 : 1 }}
      className={`rounded-lg border p-4 transition-all ${
        unlocked
          ? "border-primary/50 bg-primary/5"
          : "border-border bg-muted/30 opacity-60"
      }`}
    >
      <div
        className={`inline-flex p-2 rounded-lg mb-2 ${
          unlocked ? "bg-primary/20" : "bg-muted"
        }`}
      >
        <Icon className={`h-5 w-5 ${unlocked ? "text-primary" : "text-muted-foreground"}`} />
      </div>
      <h4 className="font-semibold text-sm mb-1">{title}</h4>
      <p className="text-xs text-muted-foreground">{description}</p>
    </motion.div>
  );
}
