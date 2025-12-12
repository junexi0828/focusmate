import { motion } from "framer-motion";
import { useState } from "react";
import { Flame } from "lucide-react";

interface StreakCalendarProps {
  data: Array<{
    date: string; // YYYY-MM-DD
    hours: number;
    sessions: number;
  }>;
  currentStreak: number;
  longestStreak: number;
}

export function StreakCalendar({
  data,
  currentStreak,
  longestStreak,
}: StreakCalendarProps) {
  const [hoveredDay, setHoveredDay] = useState<{
    date: string;
    hours: number;
    sessions: number;
  } | null>(null);

  // Generate last 12 weeks (84 days)
  const weeks: Array<Array<{ date: string; hours: number; sessions: number }>> = [];
  const today = new Date();
  const startDate = new Date(today);
  startDate.setDate(startDate.getDate() - 83); // 12 weeks ago

  // Adjust to Monday
  const dayOfWeek = startDate.getDay();
  const daysToMonday = dayOfWeek === 0 ? -6 : 1 - dayOfWeek;
  startDate.setDate(startDate.getDate() + daysToMonday);

  for (let week = 0; week < 12; week++) {
    const weekDays = [];
    for (let day = 0; day < 7; day++) {
      const currentDate = new Date(startDate);
      currentDate.setDate(currentDate.getDate() + week * 7 + day);
      const dateKey = currentDate.toISOString().split("T")[0];

      const dayData = data.find((d) => d.date === dateKey);
      weekDays.push({
        date: dateKey,
        hours: dayData?.hours || 0,
        sessions: dayData?.sessions || 0,
      });
    }
    weeks.push(weekDays);
  }

  const getColor = (hours: number) => {
    if (hours === 0) return "bg-muted";
    if (hours < 1) return "bg-primary/20";
    if (hours < 2) return "bg-primary/40";
    if (hours < 3) return "bg-primary/60";
    if (hours < 4) return "bg-primary/80";
    return "bg-primary";
  };

  const getLabel = (hours: number) => {
    if (hours === 0) return "활동 없음";
    if (hours < 1) return "낮음";
    if (hours < 2) return "보통";
    if (hours < 3) return "높음";
    if (hours < 4) return "매우 높음";
    return "최고";
  };

  const monthLabels = ["월", "화", "수", "목", "금", "토", "일"];

  return (
    <div className="space-y-4">
      {/* Streak Stats */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-2">
          <Flame className="h-5 w-5 text-orange-500" />
          <div>
            <p className="text-sm text-muted-foreground">현재 연속 기록</p>
            <p className="text-2xl font-bold">{currentStreak}일</p>
          </div>
        </div>
        <div className="border-l border-border pl-6">
          <p className="text-sm text-muted-foreground">최장 연속 기록</p>
          <p className="text-2xl font-bold text-primary">{longestStreak}일</p>
        </div>
      </div>

      {/* Calendar Grid */}
      <div className="relative">
        <div className="flex gap-1">
          {/* Day labels */}
          <div className="flex flex-col gap-1 text-xs text-muted-foreground pt-6 pr-2">
            {monthLabels.map((day, index) => (
              <div
                key={day}
                className="h-3 flex items-center justify-end"
                style={{ opacity: index % 2 === 0 ? 1 : 0 }}
              >
                {day}
              </div>
            ))}
          </div>

          {/* Weeks */}
          <div className="flex gap-1">
            {weeks.map((week, weekIndex) => (
              <div key={weekIndex} className="flex flex-col gap-1">
                {week.map((day, dayIndex) => (
                  <motion.div
                    key={day.date}
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{
                      delay: (weekIndex * 7 + dayIndex) * 0.01,
                      type: "spring",
                      stiffness: 300,
                    }}
                    whileHover={{ scale: 1.3, zIndex: 10 }}
                    className={`w-3 h-3 rounded-sm ${getColor(
                      day.hours
                    )} cursor-pointer transition-all relative`}
                    onMouseEnter={() => setHoveredDay(day)}
                    onMouseLeave={() => setHoveredDay(null)}
                  />
                ))}
              </div>
            ))}
          </div>
        </div>

        {/* Tooltip */}
        {hoveredDay && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute top-full left-1/2 transform -translate-x-1/2 mt-2 z-20"
          >
            <div className="bg-popover border border-border rounded-lg shadow-lg p-3 text-sm whitespace-nowrap">
              <p className="font-medium">
                {new Date(hoveredDay.date).toLocaleDateString("ko-KR", {
                  month: "long",
                  day: "numeric",
                  weekday: "short",
                })}
              </p>
              <p className="text-muted-foreground mt-1">
                {hoveredDay.hours > 0
                  ? `${hoveredDay.hours.toFixed(1)}시간 · ${hoveredDay.sessions}개 세션`
                  : "활동 없음"}
              </p>
              <p className="text-xs text-muted-foreground mt-1">
                {getLabel(hoveredDay.hours)}
              </p>
            </div>
          </motion.div>
        )}
      </div>

      {/* Legend */}
      <div className="flex items-center gap-2 text-xs text-muted-foreground">
        <span>적음</span>
        <div className="flex gap-1">
          <div className="w-3 h-3 rounded-sm bg-muted" />
          <div className="w-3 h-3 rounded-sm bg-primary/20" />
          <div className="w-3 h-3 rounded-sm bg-primary/40" />
          <div className="w-3 h-3 rounded-sm bg-primary/60" />
          <div className="w-3 h-3 rounded-sm bg-primary/80" />
          <div className="w-3 h-3 rounded-sm bg-primary" />
        </div>
        <span>많음</span>
      </div>
    </div>
  );
}
