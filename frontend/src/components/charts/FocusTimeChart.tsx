import { motion } from "framer-motion";
import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

interface FocusTimeChartProps {
  data: Array<{
    date: string;
    hours: number;
    sessions: number;
  }>;
}

export function FocusTimeChart({ data }: FocusTimeChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="w-full h-[300px]"
    >
      <ResponsiveContainer width="100%" height="100%">
        <AreaChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: 0 }}
        >
          <defs>
            <linearGradient id="colorHours" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(25, 80%, 72%)" stopOpacity={0.4} />
              <stop offset="95%" stopColor="hsl(25, 80%, 72%)" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid
            strokeDasharray="3 3"
            stroke="hsl(var(--border))"
            opacity={0.3}
          />
          <XAxis
            dataKey="date"
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
            cursor={{ stroke: "hsl(var(--primary))", strokeWidth: 1 }}
          />
          <Area
            type="monotone"
            dataKey="hours"
            stroke="hsl(25, 80%, 72%)"
            strokeWidth={2}
            fill="url(#colorHours)"
            animationDuration={1000}
            animationEasing="ease-in-out"
          />
        </AreaChart>
      </ResponsiveContainer>
    </motion.div>
  );
}

function CustomTooltip({ active, payload }: any) {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-popover p-3 shadow-md">
        <p className="text-sm font-medium">{payload[0].payload.date}</p>
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
