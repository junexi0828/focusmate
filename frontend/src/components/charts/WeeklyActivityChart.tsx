import { motion } from "framer-motion";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { useState } from "react";

interface WeeklyActivityChartProps {
  data: Array<{
    day: string;
    hours: number;
    sessions: number;
  }>;
}

export function WeeklyActivityChart({ data }: WeeklyActivityChartProps) {
  const [activeIndex, setActiveIndex] = useState<number | null>(null);

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.1 }}
      className="w-full h-[300px]"
    >
      <ResponsiveContainer width="100%" height="100%">
        <BarChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
          onMouseMove={(state) => {
            if (state.isTooltipActive) {
              setActiveIndex(state.activeTooltipIndex ?? null);
            } else {
              setActiveIndex(null);
            }
          }}
          onMouseLeave={() => setActiveIndex(null)}
        >
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="hsl(var(--border))"
            opacity={0.3}
          />
          <XAxis
            dataKey="day"
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
          <Tooltip
            content={<CustomTooltip />}
            cursor={{ fill: "hsl(var(--accent))", opacity: 0.1 }}
          />
          <Bar
            dataKey="hours"
            radius={[8, 8, 0, 0]}
            animationDuration={1000}
            animationEasing="ease-in-out"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={
                  activeIndex === index
                    ? "hsl(var(--primary))"
                    : "hsl(var(--primary) / 0.6)"
                }
                style={{
                  transition: "fill 0.2s ease",
                }}
              />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </motion.div>
  );
}

function CustomTooltip({ active, payload }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-popover p-3 shadow-md">
        <p className="text-sm font-medium">{payload[0].payload.day}요일</p>
        <div className="mt-2 space-y-1">
          <p className="text-sm text-muted-foreground">
            집중 시간: <span className="font-semibold text-foreground">{payload[0].value}시간</span>
          </p>
          <p className="text-sm text-muted-foreground">
            세션: <span className="font-semibold text-foreground">{payload[0].payload.sessions}회</span>
          </p>
        </div>
      </div>
    );
  }
  return null;
}
