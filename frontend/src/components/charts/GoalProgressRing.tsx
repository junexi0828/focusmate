import { motion } from "framer-motion";
import { Cell, Pie, PieChart, ResponsiveContainer } from "recharts";
import { getProgressColor } from "../../utils/chart-colors";

interface GoalProgressRingProps {
  current: number;
  goal: number;
  label: string;
  unit?: string;
}

export function GoalProgressRing({
  current,
  goal,
  label,
  unit = "시간",
}: GoalProgressRingProps) {
  const percentage = Math.min((current / goal) * 100, 100);
  const remaining = Math.max(goal - current, 0);

  const data = [
    { name: "완료", value: current },
    { name: "남음", value: remaining },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.5, type: "spring", stiffness: 200 }}
      className="relative"
    >
      <div className="w-full h-[250px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={data}
              cx="50%"
              cy="50%"
              innerRadius={70}
              outerRadius={90}
              startAngle={90}
              endAngle={-270}
              paddingAngle={0}
              dataKey="value"
              animationDuration={1000}
              animationEasing="ease-out"
            >
              <Cell fill={getProgressColor(percentage)} />
              <Cell fill="hsl(0, 0%, 90%)" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>

      {/* Center Text */}
      <div className="absolute inset-0 flex flex-col items-center justify-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ delay: 0.3, type: "spring", stiffness: 200 }}
          className="text-center"
        >
          <p className="text-4xl font-bold">{percentage.toFixed(0)}%</p>
          <p className="text-sm text-muted-foreground mt-1">{label}</p>
          <div className="mt-3 space-y-1">
            <p className="text-xs text-muted-foreground">
              현재: <span className="font-semibold text-foreground">{current}{unit}</span>
            </p>
            <p className="text-xs text-muted-foreground">
              목표: <span className="font-semibold text-foreground">{goal}{unit}</span>
            </p>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
