import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./ui/tabs";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";
import { StatsTimeRange } from "../types/stats";
import {
  calculateDailyStats,
  calculateWeeklyStats,
  calculateMonthlyStats,
} from "../utils/stats-calculator";
import { SessionRecord } from "../features/stats/services/statsService";
import { BarChart3 } from "lucide-react";

interface StatsChartProps {
  sessions: SessionRecord[];
}

export function StatsChart({ sessions }: StatsChartProps) {
  const [timeRange, setTimeRange] = useState<StatsTimeRange>("daily");

  const dailyStats = calculateDailyStats(sessions).slice(-7); // Last 7 days
  const weeklyStats = calculateWeeklyStats(sessions).slice(-4); // Last 4 weeks
  const monthlyStats = calculateMonthlyStats(sessions); // All months

  const getChartData = () => {
    switch (timeRange) {
      case "daily":
        return dailyStats.map((stat) => ({
          name: new Date(stat.date).toLocaleDateString("ko-KR", {
            month: "short",
            day: "numeric",
          }),
          "집중 시간": stat.focusTime,
          "휴식 시간": stat.breakTime,
        }));
      case "weekly":
        return weeklyStats.map((stat, index) => ({
          name: `${index + 1}주차`,
          "집중 시간": stat.focusTime,
          "휴식 시간": stat.breakTime,
        }));
      case "monthly":
        return monthlyStats.map((stat) => ({
          name: new Date(stat.month + "-01").toLocaleDateString("ko-KR", {
            year: "numeric",
            month: "short",
          }),
          "집중 시간": stat.focusTime,
          "휴식 시간": stat.breakTime,
        }));
      default:
        return [];
    }
  };

  const getTotalStats = () => {
    const data = timeRange === "daily" ? dailyStats : timeRange === "weekly" ? weeklyStats : monthlyStats;
    const totalFocus = data.reduce((sum, stat) => sum + stat.focusTime, 0);
    const totalBreak = data.reduce((sum, stat) => sum + stat.breakTime, 0);
    const totalSessions = data.reduce((sum, stat) => sum + stat.sessions, 0);

    return { totalFocus, totalBreak, totalSessions };
  };

  const { totalFocus, totalBreak, totalSessions } = getTotalStats();

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <BarChart3 className="w-5 h-5" />
          집중 시간 통계
        </CardTitle>
        <CardDescription>시간대별 집중 및 휴식 시간 분석</CardDescription>
      </CardHeader>
      <CardContent>
        <Tabs value={timeRange} onValueChange={(value) => setTimeRange(value as StatsTimeRange)}>
          <TabsList className="grid w-full grid-cols-3 mb-6">
            <TabsTrigger value="daily">일간</TabsTrigger>
            <TabsTrigger value="weekly">주간</TabsTrigger>
            <TabsTrigger value="monthly">월간</TabsTrigger>
          </TabsList>

          {/* Summary Stats */}
          <div className="grid grid-cols-3 gap-4 mb-6">
            <div className="p-4 rounded-lg bg-primary/10 border border-primary/20">
              <p className="text-sm text-muted-foreground">총 집중 시간</p>
              <p className="text-2xl text-primary mt-1">{totalFocus}분</p>
            </div>
            <div className="p-4 rounded-lg bg-secondary/10 border border-secondary/20">
              <p className="text-sm text-muted-foreground">총 휴식 시간</p>
              <p className="text-2xl text-secondary mt-1">{totalBreak}분</p>
            </div>
            <div className="p-4 rounded-lg bg-muted border">
              <p className="text-sm text-muted-foreground">완료 세션</p>
              <p className="text-2xl mt-1">{totalSessions}개</p>
            </div>
          </div>

          <TabsContent value="daily" className="mt-0">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getChartData()}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
                <Bar dataKey="집중 시간" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                <Bar dataKey="휴식 시간" fill="hsl(var(--secondary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </TabsContent>

          <TabsContent value="weekly" className="mt-0">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getChartData()}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
                <Bar dataKey="집중 시간" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                <Bar dataKey="휴식 시간" fill="hsl(var(--secondary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </TabsContent>

          <TabsContent value="monthly" className="mt-0">
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={getChartData()}>
                <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
                <XAxis dataKey="name" className="text-xs" />
                <YAxis className="text-xs" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: "hsl(var(--card))",
                    border: "1px solid hsl(var(--border))",
                    borderRadius: "0.5rem",
                  }}
                />
                <Legend />
                <Bar dataKey="집중 시간" fill="hsl(var(--primary))" radius={[4, 4, 0, 0]} />
                <Bar dataKey="휴식 시간" fill="hsl(var(--secondary))" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </TabsContent>
        </Tabs>
      </CardContent>
    </Card>
  );
}
