import { motion } from "framer-motion";
import {
  Brush,
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
  enableZoom?: boolean;
}

export function MonthlyComparisonChart({
  data,
  enableZoom = true,
}: MonthlyComparisonChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="w-full h-[350px]"
    >
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={data}
          margin={{ top: 10, right: 10, left: 0, bottom: enableZoom ? 40 : 0 }}
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
          {enableZoom && (
            <Brush
              dataKey="month"
              height={30}
              stroke="hsl(var(--border))"
              fill="hsl(var(--muted))"
              travellerWidth={10}
              travellerProps={{
                style: {
                  fill: "hsl(var(--primary))",
                  stroke: "hsl(var(--primary))",
                },
              }}
              tickFormatter={(value) => value}
              tick={{
                fill: "hsl(var(--muted-foreground))",
                fontSize: 11,
                fontWeight: 400,
              }}
              startIndex={0}
              endIndex={data.length - 1}
            />
          )}
        </LineChart>
      </ResponsiveContainer>
    </motion.div>
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
