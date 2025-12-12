import React from "react";
import { StatCard } from "./StatCard";
import { Target, Clock, Award, TrendingUp } from "lucide-react";

interface StatsDashboardProps {
  totalFocusTime: number;
  totalSessions: number;
  averageSessionTime: number;
  totalBreakTime?: number;
}

export function StatsDashboard({
  totalFocusTime,
  totalSessions,
  averageSessionTime,
  totalBreakTime = 0,
}: StatsDashboardProps) {
  const formatTime = (minutes: number) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    if (hours > 0) {
      return `${hours}시간 ${mins}분`;
    }
    return `${mins}분`;
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
      <StatCard
        title="총 집중 시간"
        value={formatTime(totalFocusTime)}
        icon={Target}
        variant="primary"
        trend={{ value: 12, isPositive: true }}
      />
      <StatCard
        title="완료한 세션"
        value={`${totalSessions}개`}
        icon={Award}
        variant="secondary"
        trend={{ value: 8, isPositive: true }}
      />
      <StatCard
        title="평균 세션 시간"
        value={formatTime(averageSessionTime)}
        icon={Clock}
        variant="default"
      />
      <StatCard
        title="총 휴식 시간"
        value={formatTime(totalBreakTime)}
        icon={TrendingUp}
        variant="muted"
      />
    </div>
  );
}

