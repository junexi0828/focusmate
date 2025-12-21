import { motion } from "framer-motion";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts";

interface SessionDistributionChartProps {
  data: Array<{
    name: string;
    value: number;
    color: string;
  }>;
}

export function SessionDistributionChart({
  data,
}: SessionDistributionChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0);

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="w-full"
    >
      <div className="flex flex-col md:flex-row items-center gap-6">
        {/* Chart */}
        <div className="w-full md:w-1/2 min-h-[300px] h-[300px] md:h-[350px]">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={60}
                outerRadius={90}
                paddingAngle={2}
                dataKey="value"
                animationDuration={1000}
                animationEasing="ease-out"
              >
                {data.map((entry, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={entry.color}
                    stroke="hsl(var(--background))"
                    strokeWidth={2}
                  />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip total={total} />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="w-full md:w-1/2 space-y-3">
          {data.map((item, index) => (
            <motion.div
              key={item.name}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 + index * 0.05 }}
              className="flex items-center justify-between p-3 rounded-lg hover:bg-accent transition-colors"
            >
              <div className="flex items-center gap-3">
                <div
                  className="w-3 h-3 rounded-full"
                  style={{ backgroundColor: item.color }}
                />
                <span className="text-sm font-medium">{item.name}</span>
              </div>
              <div className="text-right">
                <p className="text-sm font-semibold">{item.value}회</p>
                <p className="text-xs text-muted-foreground">
                  {((item.value / total) * 100).toFixed(1)}%
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </motion.div>
  );
}

function CustomTooltip({ active, payload, total }: any) {
  if (active && payload && payload.length) {
    const percentage = ((payload[0].value / total) * 100).toFixed(1);
    return (
      <div className="rounded-lg border bg-popover p-3 shadow-md">
        <p className="text-sm font-medium">{payload[0].name}</p>
        <div className="mt-2 space-y-1">
          <p className="text-sm text-muted-foreground">
            세션: <span className="font-semibold text-foreground">{payload[0].value}회</span>
          </p>
          <p className="text-sm text-muted-foreground">
            비율: <span className="font-semibold text-foreground">{percentage}%</span>
          </p>
        </div>
      </div>
    );
  }
  return null;
}
