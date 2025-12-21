import { motion } from "framer-motion";
import { useMemo } from "react";
import { TrendingUp, TrendingDown, Award, BarChart3 } from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface MonthlyComparisonChartProps {
  data: Array<{
    month: string;
    thisYear: number;
    lastYear: number;
  }>;
}

export function MonthlyComparisonChart({ data }: MonthlyComparisonChartProps) {
  // 통계 계산
  const stats = useMemo(() => {
    const thisYearTotal = data.reduce((sum, item) => sum + item.thisYear, 0);
    const lastYearTotal = data.reduce((sum, item) => sum + item.lastYear, 0);
    const thisYearAvg = thisYearTotal / data.length;
    const growthRate =
      lastYearTotal > 0
        ? ((thisYearTotal - lastYearTotal) / lastYearTotal) * 100
        : thisYearTotal > 0
          ? 100
          : 0;

    const bestMonth = data.reduce(
      (best, current) => (current.thisYear > best.thisYear ? current : best),
      data[0] || { month: "", thisYear: 0, lastYear: 0 }
    );

    return {
      thisYearTotal: thisYearTotal.toFixed(1),
      lastYearTotal: lastYearTotal.toFixed(1),
      thisYearAvg: thisYearAvg.toFixed(1),
      growthRate: growthRate.toFixed(1),
      bestMonth: bestMonth.month,
      bestMonthHours: bestMonth.thisYear.toFixed(1),
    };
  }, [data]);

  return (
    <div className="w-full space-y-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.3 }}
        className="w-full h-[350px]"
      >
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={data}
            margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="hsl(var(--border))"
              opacity={0.3}
            />
            <XAxis
              dataKey="month"
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickLine={false}
              axisLine={false}
            />
            <YAxis
              stroke="hsl(var(--muted-foreground))"
              fontSize={12}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => `${value}h`}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              wrapperStyle={{
                paddingTop: "20px",
                fontSize: "12px",
              }}
              iconType="line"
            />
            <Line
              type="monotone"
              dataKey="thisYear"
              name="올해"
              stroke="hsl(142, 65%, 70%)"
              strokeWidth={2}
              dot={{ fill: "hsl(142, 65%, 70%)", r: 4 }}
              activeDot={{ r: 6 }}
              animationDuration={1000}
              animationEasing="ease-in-out"
            />
            <Line
              type="monotone"
              dataKey="lastYear"
              name="작년"
              stroke="hsl(210, 70%, 75%)"
              strokeWidth={2}
              strokeDasharray="5 5"
              dot={{ fill: "hsl(210, 70%, 75%)", r: 4 }}
              activeDot={{ r: 6 }}
              animationDuration={1000}
              animationEasing="ease-in-out"
            />
          </LineChart>
        </ResponsiveContainer>
      </motion.div>

      {/* 통계 정보 카드 */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4, delay: 0.5 }}
        className="grid grid-cols-2 md:grid-cols-4 gap-3"
      >
        <div className="rounded-lg border border-border bg-card p-3">
          <div className="flex items-center gap-2 mb-1">
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">올해 총 집중</span>
          </div>
          <p className="text-lg font-semibold">{stats.thisYearTotal}h</p>
        </div>

        <div className="rounded-lg border border-border bg-card p-3">
          <div className="flex items-center gap-2 mb-1">
            {parseFloat(stats.growthRate) >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
            <span className="text-xs text-muted-foreground">작년 대비</span>
          </div>
          <p
            className={`text-lg font-semibold ${parseFloat(stats.growthRate) >= 0 ? "text-green-500" : "text-red-500"}`}
          >
            {parseFloat(stats.growthRate) >= 0 ? "+" : ""}
            {stats.growthRate}%
          </p>
        </div>

        <div className="rounded-lg border border-border bg-card p-3">
          <div className="flex items-center gap-2 mb-1">
            <BarChart3 className="h-4 w-4 text-muted-foreground" />
            <span className="text-xs text-muted-foreground">월평균 집중</span>
          </div>
          <p className="text-lg font-semibold">{stats.thisYearAvg}h</p>
        </div>

        <div className="rounded-lg border border-border bg-card p-3">
          <div className="flex items-center gap-2 mb-1">
            <Award className="h-4 w-4 text-amber-500" />
            <span className="text-xs text-muted-foreground">최고 집중 월</span>
          </div>
          <p className="text-lg font-semibold">{stats.bestMonth}</p>
          <p className="text-xs text-muted-foreground">
            {stats.bestMonthHours}h
          </p>
        </div>
      </motion.div>
    </div>
  );
}

function CustomTooltip({ active, payload }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-popover p-3 shadow-md">
        <p className="text-sm font-medium mb-2">{payload[0].payload.month}</p>
        <div className="space-y-1">
          {payload.map((entry: any, index: number) => (
            <p key={index} className="text-sm text-muted-foreground">
              {entry.name}:{" "}
              <span className="font-semibold text-foreground">
                {entry.value}시간
              </span>
            </p>
          ))}
        </div>
      </div>
    );
  }
  return null;
}
