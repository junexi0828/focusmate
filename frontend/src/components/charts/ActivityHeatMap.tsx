import { motion } from "framer-motion";
import { staggerContainer, staggerItem } from "../PageTransition";

interface ActivityHeatMapProps {
  data: Array<{
    week: number;
    days: Array<{
      day: string;
      hours: number;
    }>;
  }>;
}

export function ActivityHeatMap({ data }: ActivityHeatMapProps) {
  const getColor = (hours: number) => {
    if (hours === 0) return "bg-muted";
    if (hours < 2) return "bg-primary/20";
    if (hours < 4) return "bg-primary/40";
    if (hours < 6) return "bg-primary/60";
    return "bg-primary";
  };

  const getLabel = (hours: number) => {
    if (hours === 0) return "활동 없음";
    if (hours < 2) return "낮음";
    if (hours < 4) return "보통";
    if (hours < 6) return "높음";
    return "매우 높음";
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="w-full"
    >
      <div className="flex items-start gap-2">
        {/* Day labels */}
        <div className="flex flex-col gap-1 text-xs text-muted-foreground pt-6">
          {["월", "화", "수", "목", "금", "토", "일"].map((day) => (
            <div key={day} className="h-4 flex items-center">
              {day}
            </div>
          ))}
        </div>

        {/* Heatmap grid */}
        <motion.div
          variants={staggerContainer}
          initial="initial"
          animate="animate"
          className="flex-1 overflow-x-auto"
        >
          <div className="flex gap-1">
            {data.map((week, weekIndex) => (
              <div key={weekIndex} className="flex flex-col gap-1">
                {week.days.map((dayData, dayIndex) => (
                  <motion.div
                    key={`${weekIndex}-${dayIndex}`}
                    variants={staggerItem}
                    whileHover={{ scale: 1.2, zIndex: 10 }}
                    className={`w-4 h-4 rounded-sm ${getColor(
                      dayData.hours
                    )} cursor-pointer relative group transition-all`}
                  >
                    {/* Tooltip */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-20">
                      <div className="bg-popover text-popover-foreground text-xs px-2 py-1 rounded shadow-md whitespace-nowrap">
                        <p className="font-medium">{dayData.day}</p>
                        <p className="text-muted-foreground">
                          {dayData.hours}시간 · {getLabel(dayData.hours)}
                        </p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      {/* Legend */}
      <div className="flex items-center gap-2 mt-4 text-xs text-muted-foreground">
        <span>적음</span>
        <div className="flex gap-1">
          <div className="w-3 h-3 rounded-sm bg-muted" />
          <div className="w-3 h-3 rounded-sm bg-primary/20" />
          <div className="w-3 h-3 rounded-sm bg-primary/40" />
          <div className="w-3 h-3 rounded-sm bg-primary/60" />
          <div className="w-3 h-3 rounded-sm bg-primary" />
        </div>
        <span>많음</span>
      </div>
    </motion.div>
  );
}
