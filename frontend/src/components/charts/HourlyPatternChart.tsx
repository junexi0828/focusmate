import { motion } from "framer-motion";
import {
  PolarAngleAxis,
  PolarGrid,
  PolarRadiusAxis,
  Radar,
  RadarChart,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface HourlyPatternChartProps {
  data: Array<{
    hour: string;
    sessions: number;
    avgDuration: number;
  }>;
  focusTime?: number[]; // Optional: direct focus time data from API
}

export function HourlyPatternChart({ data, focusTime }: HourlyPatternChartProps) {
  // Use focusTime if provided, otherwise use sessions from data
  const chartData = focusTime
    ? focusTime.map((time, hour) => ({
        hour: `${hour}`,
        sessions: Math.round(time / 25), // Approximate sessions (assuming 25min average)
        avgDuration: time > 0 ? Math.round(time / Math.max(1, Math.round(time / 25))) : 0,
        focusTime: time,
      }))
    : data;

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="w-full h-[400px]"
    >
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={chartData}>
          <PolarGrid stroke="hsl(var(--border))" />
          <PolarAngleAxis
            dataKey="hour"
            stroke="hsl(var(--muted-foreground))"
            fontSize={12}
            tickFormatter={(value) => `${value}시`}
          />
          <PolarRadiusAxis
            angle={90}
            domain={[0, "auto"]}
            stroke="hsl(var(--muted-foreground))"
            fontSize={10}
          />
          <Radar
            name={focusTime ? "집중 시간 (분)" : "세션 수"}
            dataKey={focusTime ? "focusTime" : "sessions"}
            stroke="hsl(var(--primary))"
            fill="hsl(var(--primary))"
            fillOpacity={0.3}
            animationDuration={1000}
            animationEasing="ease-out"
          />
          <Tooltip content={<CustomTooltip focusTime={!!focusTime} />} />
        </RadarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}

function CustomTooltip({ active, payload, focusTime }: any) {
  if (active && payload && payload.length) {
    const data = payload[0].payload;
    return (
      <div className="rounded-lg border bg-popover p-3 shadow-md">
        <p className="text-sm font-medium">{data.hour}시</p>
        <div className="mt-2 space-y-1">
          {focusTime ? (
            <>
              <p className="text-sm text-muted-foreground">
                집중 시간: <span className="font-semibold text-foreground">{data.focusTime}분</span>
              </p>
              <p className="text-sm text-muted-foreground">
                세션 수: <span className="font-semibold text-foreground">{data.sessions}회</span>
              </p>
            </>
          ) : (
            <>
              <p className="text-sm text-muted-foreground">
                세션 수: <span className="font-semibold text-foreground">{payload[0].value}회</span>
              </p>
              <p className="text-sm text-muted-foreground">
                평균 시간:{" "}
                <span className="font-semibold text-foreground">
                  {data.avgDuration}분
                </span>
              </p>
            </>
          )}
        </div>
      </div>
    );
  }
  return null;
}
