import React, { useMemo, useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  Clock,
  Target,
  TrendingUp,
  Zap,
  AlertCircle,
  Download,
  Settings,
  Share2,
} from "lucide-react";
import { staggerContainer, staggerItem } from "../components/PageTransition";
import { FocusTimeChart } from "../components/charts/FocusTimeChart";
import { SessionDistributionChart } from "../components/charts/SessionDistributionChart";
import { Button } from "../components/ui/button-enhanced";
import { PomodoroWidget } from "../components/PomodoroWidget";
import { StreakCalendar } from "../components/StreakCalendar";
import { GoalSettingModal } from "../components/GoalSettingModal";
import { SharingModal } from "../components/SharingCard";
import { UserStatsResponse } from "../features/stats/services/statsService";
import { calculateDailyStats } from "../utils/stats-calculator";
import { DataExporter } from "../utils/dataExporter";
import { CelebrationSystem } from "../utils/celebrationSystem";

interface DashboardPageProps {
  stats?: UserStatsResponse;
  isLoading?: boolean;
  error?: Error | null;
}

export function DashboardPage({ stats, isLoading, error }: DashboardPageProps) {
  const [isGoalModalOpen, setIsGoalModalOpen] = useState(false);
  const [isSharingModalOpen, setIsSharingModalOpen] = useState(false);
  const [sharingCardData, setSharingCardData] = useState<any>(null);

  // 통계 데이터 변환
  const dashboardStats = useMemo(() => {
    if (!stats) return null;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    const todaySessions = stats.sessions.filter((session) => {
      const sessionDate = new Date(session.completed_at);
      sessionDate.setHours(0, 0, 0, 0);
      return (
        sessionDate.getTime() === today.getTime() &&
        session.session_type === "work"
      );
    });

    const todayFocusTime = todaySessions.reduce(
      (sum, session) => sum + session.duration_minutes,
      0
    );

    const todaySessionsCount = todaySessions.length;

    // 연속 기록 계산
    const sortedSessions = [...stats.sessions]
      .filter((s) => s.session_type === "work")
      .sort(
        (a, b) =>
          new Date(b.completed_at).getTime() -
          new Date(a.completed_at).getTime()
      );

    let consecutiveDays = 0;
    const checkedDates = new Set<string>();

    for (const session of sortedSessions) {
      const sessionDate = new Date(session.completed_at)
        .toISOString()
        .split("T")[0];
      if (!checkedDates.has(sessionDate)) {
        checkedDates.add(sessionDate);
        const daysDiff = Math.floor(
          (today.getTime() - new Date(sessionDate).getTime()) /
            (1000 * 60 * 60 * 24)
        );
        if (daysDiff === consecutiveDays) {
          consecutiveDays++;
        } else {
          break;
        }
      }
    }

    const weeklyAverageHours = stats.average_session / 60;

    const formatTime = (minutes: number) => {
      const hours = Math.floor(minutes / 60);
      const mins = minutes % 60;
      if (hours > 0) {
        return `${hours}h ${mins}m`;
      }
      return `${mins}m`;
    };

    return [
      {
        title: "오늘 집중 시간",
        value: formatTime(todayFocusTime),
        change: todayFocusTime > 0 ? "오늘의 집중" : "아직 없음",
        trend: todayFocusTime > 0 ? ("up" as const) : ("neutral" as const),
        icon: Clock,
      },
      {
        title: "완료한 세션",
        value: todaySessionsCount.toString(),
        change: todaySessionsCount > 0 ? "목표 달성" : "시작해보세요",
        trend: todaySessionsCount > 0 ? ("up" as const) : ("neutral" as const),
        icon: Target,
      },
      {
        title: "현재 연속 기록",
        value: `${consecutiveDays}일`,
        change: consecutiveDays > 0 ? "계속 유지하세요!" : "오늘부터 시작",
        trend: consecutiveDays > 0 ? ("up" as const) : ("neutral" as const),
        icon: Zap,
      },
      {
        title: "주간 평균",
        value: `${weeklyAverageHours.toFixed(1)}h`,
        change:
          stats.total_sessions > 0
            ? `${stats.total_sessions}개 세션`
            : "데이터 없음",
        trend: stats.total_sessions > 0 ? ("up" as const) : ("neutral" as const),
        icon: TrendingUp,
      },
    ];
  }, [stats]);

  // 차트 데이터 변환
  const chartData = useMemo(() => {
    if (!stats || !stats.sessions.length) return null;

    const dailyStats = calculateDailyStats(
      stats.sessions.map((s) => ({
        id: s.session_id,
        date: new Date(s.completed_at),
        duration: s.duration_minutes,
        type: s.session_type === "work" ? ("focus" as const) : ("break" as const),
        completed: true,
        room_name: s.room_name,
      }))
    );

    const recentDays = dailyStats.slice(-7);

    const focusTimeData = recentDays.map((day) => {
      const date = new Date(day.date);
      const daySessions = stats.sessions.filter((s) => {
        const sessionDate = new Date(s.completed_at);
        return (
          sessionDate.toISOString().split("T")[0] ===
            date.toISOString().split("T")[0] && s.session_type === "work"
        );
      });

      return {
        date: `${date.getMonth() + 1}/${date.getDate()}`,
        hours: day.focusTime / 60,
        sessions: daySessions.length,
      };
    });

    const sessionDurations = stats.sessions
      .filter((s) => s.session_type === "work")
      .map((s) => s.duration_minutes);

    const distribution: Record<string, number> = {
      "포모도로 (25분)": 0,
      "단기 집중 (15분)": 0,
      "장기 집중 (50분)": 0,
    };

    sessionDurations.forEach((duration) => {
      if (duration >= 20 && duration <= 30) {
        distribution["포모도로 (25분)"]++;
      } else if (duration < 20) {
        distribution["단기 집중 (15분)"]++;
      } else {
        distribution["장기 집중 (50분)"]++;
      }
    });

    const breakCount = stats.sessions.filter(
      (s) => s.session_type === "break"
    ).length;

    const sessionDistribution = [
      {
        name: "포모도로 (25분)",
        value: distribution["포모도로 (25분)"],
        color: "hsl(var(--chart-1))",
      },
      {
        name: "단기 집중 (15분)",
        value: distribution["단기 집중 (15분)"],
        color: "hsl(var(--chart-2))",
      },
      {
        name: "장기 집중 (50분)",
        value: distribution["장기 집중 (50분)"],
        color: "hsl(var(--chart-3))",
      },
      {
        name: "휴식",
        value: breakCount,
        color: "hsl(var(--chart-4))",
      },
    ].filter((item) => item.value > 0);

    return { focusTimeData, sessionDistribution };
  }, [stats]);

  // Streak calendar data
  const streakData = useMemo(() => {
    if (!stats) return [];

    const dailyStats = calculateDailyStats(
      stats.sessions.map((s) => ({
        id: s.session_id,
        date: new Date(s.completed_at),
        duration: s.duration_minutes,
        type: s.session_type === "work" ? ("focus" as const) : ("break" as const),
        completed: true,
        room_name: s.room_name,
      }))
    );

    return dailyStats.map((day) => ({
      date: day.date,
      hours: day.focusTime / 60,
      sessions: stats.sessions.filter(
        (s) =>
          new Date(s.completed_at).toISOString().split("T")[0] === day.date &&
          s.session_type === "work"
      ).length,
    }));
  }, [stats]);

  // Export handlers
  const handleExportCSV = () => {
    if (!stats) return;

    const exportData = {
      sessions: stats.sessions.map((s) => ({
        date: new Date(s.completed_at).toLocaleDateString("ko-KR"),
        duration: s.duration_minutes,
        type: s.session_type,
        roomName: s.room_name,
      })),
      stats: {
        totalFocusTime: stats.total_focus_time,
        totalSessions: stats.total_sessions,
        averageSession: stats.average_session,
      },
    };

    DataExporter.exportToCSV(exportData);
  };

  const handleExportPDF = () => {
    if (!stats) return;

    const exportData = {
      sessions: stats.sessions.map((s) => ({
        date: new Date(s.completed_at).toLocaleDateString("ko-KR"),
        duration: s.duration_minutes,
        type: s.session_type,
        roomName: s.room_name,
      })),
      stats: {
        totalFocusTime: stats.total_focus_time,
        totalSessions: stats.total_sessions,
        averageSession: stats.average_session,
      },
    };

    DataExporter.exportToPDF(exportData);
  };

  const handleGoalSave = (goal: {
    type: "weekly" | "monthly" | "yearly";
    targetHours: number;
  }) => {
    // TODO: Save goal to backend
    console.log("Goal saved:", goal);
    CelebrationSystem.celebrate();
  };

  const handleSessionComplete = (duration: number, type: "work" | "break") => {
    // TODO: Save session to backend
    console.log("Session completed:", duration, type);
    if (type === "work") {
      CelebrationSystem.firstSession();
    }
  };

  const handleShare = (type: "weekly" | "streak") => {
    if (!stats) return;

    if (type === "weekly") {
      setSharingCardData({
        type: "weekly",
        data: {
          title: "이번 주 집중 시간",
          value: `${(stats.total_focus_time / 60).toFixed(1)}시간`,
          subtitle: `${stats.total_sessions}개의 세션 완료`,
          icon: <Clock className="h-12 w-12" />,
        },
      });
    } else {
      const consecutiveDays = dashboardStats?.[2]?.value || "0일";
      setSharingCardData({
        type: "streak",
        data: {
          title: "연속 기록",
          value: consecutiveDays,
          subtitle: "매일 꾸준히 집중하고 있어요!",
          icon: <Zap className="h-12 w-12" />,
        },
      });
    }

    setIsSharingModalOpen(true);
  };

  // 로딩 상태
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">대시보드</h1>
            <p className="text-muted-foreground mt-1">데이터를 불러오는 중...</p>
          </div>
        </div>
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {[1, 2, 3, 4].map((i) => (
            <div
              key={i}
              className="p-6 rounded-xl border border-border bg-card animate-pulse"
            >
              <div className="h-4 bg-muted rounded w-1/2 mb-3" />
              <div className="h-8 bg-muted rounded w-1/3 mb-2" />
              <div className="h-3 bg-muted rounded w-1/2" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  // 에러 상태
  if (error) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">대시보드</h1>
            <p className="text-muted-foreground mt-1">오류가 발생했습니다</p>
          </div>
        </div>
        <div className="rounded-xl border border-destructive bg-destructive/10 p-6 flex items-center gap-4">
          <AlertCircle className="w-6 h-6 text-destructive flex-shrink-0" />
          <div>
            <p className="font-semibold text-destructive">
              데이터를 불러올 수 없습니다
            </p>
            <p className="text-sm text-muted-foreground mt-1">
              {error instanceof Error
                ? error.message
                : "알 수 없는 오류가 발생했습니다"}
            </p>
          </div>
        </div>
      </div>
    );
  }

  // 데이터가 없는 경우
  if (!stats || !dashboardStats || !chartData) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold tracking-tight">대시보드</h1>
            <p className="text-muted-foreground mt-1">아직 데이터가 없습니다</p>
          </div>
        </div>
        <div className="rounded-xl border border-border bg-card p-12 text-center">
          <Target className="w-12 h-12 mx-auto mb-4 text-muted-foreground" />
          <p className="text-lg font-semibold mb-2">
            아직 집중 세션이 없습니다
          </p>
          <p className="text-sm text-muted-foreground mb-6">
            첫 번째 포모도로 세션을 시작해보세요!
          </p>
          <Button variant="primary" size="md">
            집중 시작
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl font-bold tracking-tight">대시보드</h1>
          <p className="text-muted-foreground mt-1">
            오늘도 생산적인 하루 되세요!
          </p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setIsGoalModalOpen(true)}
            className="gap-2"
          >
            <Settings className="h-4 w-4" />
            목표 설정
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={() => handleShare("weekly")}
            className="gap-2"
          >
            <Share2 className="h-4 w-4" />
            공유
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportCSV}
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            CSV
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={handleExportPDF}
            className="gap-2"
          >
            <Download className="h-4 w-4" />
            PDF
          </Button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <motion.div
        variants={staggerContainer}
        initial="initial"
        animate="animate"
        className="grid gap-4 md:grid-cols-2 lg:grid-cols-4"
      >
        {dashboardStats.map((stat, index) => (
          <StatCard key={index} {...stat} index={index} />
        ))}
      </motion.div>

      {/* Main Content Grid */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Left Column - Charts */}
        <div className="lg:col-span-2 space-y-6">
          {/* Charts Grid */}
          <div className="grid gap-6 lg:grid-cols-2">
            {/* Focus Time Chart */}
            {chartData.focusTimeData.length > 0 && (
              <div className="rounded-xl border border-border bg-card p-6">
                <h3 className="text-lg font-semibold mb-4">주간 집중 시간</h3>
                <FocusTimeChart data={chartData.focusTimeData} />
              </div>
            )}

            {/* Session Distribution */}
            {chartData.sessionDistribution.length > 0 && (
              <div className="rounded-xl border border-border bg-card p-6">
                <h3 className="text-lg font-semibold mb-4">세션 분포</h3>
                <SessionDistributionChart data={chartData.sessionDistribution} />
              </div>
            )}
          </div>

          {/* Streak Calendar */}
          <div className="rounded-xl border border-border bg-card p-6">
            <h3 className="text-lg font-semibold mb-4">활동 기록</h3>
            <StreakCalendar
              data={streakData}
              currentStreak={
                parseInt(dashboardStats[2].value.replace("일", "")) || 0
              }
              longestStreak={
                parseInt(dashboardStats[2].value.replace("일", "")) || 0
              }
            />
          </div>
        </div>

        {/* Right Column - Pomodoro Widget */}
        <div>
          <PomodoroWidget onSessionComplete={handleSessionComplete} />
        </div>
      </div>

      {/* Modals */}
      <GoalSettingModal
        isOpen={isGoalModalOpen}
        onClose={() => setIsGoalModalOpen(false)}
        onSave={handleGoalSave}
      />

      {sharingCardData && (
        <SharingModal
          isOpen={isSharingModalOpen}
          onClose={() => setIsSharingModalOpen(false)}
          card={sharingCardData}
        />
      )}
    </div>
  );
}

interface StatCardProps {
  title: string;
  value: string;
  change: string;
  trend: "up" | "down" | "neutral";
  icon: typeof Clock;
  index: number;
}

function StatCard({
  title,
  value,
  change,
  trend,
  icon: Icon,
  index,
}: StatCardProps) {
  return (
    <motion.div
      variants={staggerItem}
      whileHover={{ scale: 1.02, y: -2 }}
      className="p-6 rounded-xl border border-border bg-card hover:border-primary/50 transition-all cursor-pointer"
    >
      <div className="flex items-center justify-between mb-3">
        <span className="text-sm text-muted-foreground">{title}</span>
        <div className="p-2 rounded-lg bg-primary/10">
          <Icon className="h-4 w-4 text-primary" />
        </div>
      </div>
      <div className="text-3xl font-bold mb-1">{value}</div>
      <div
        className={`text-xs ${
          trend === "up"
            ? "text-green-600 dark:text-green-400"
            : trend === "down"
            ? "text-red-600 dark:text-red-400"
            : "text-muted-foreground"
        }`}
      >
        {change}
      </div>
    </motion.div>
  );
}
