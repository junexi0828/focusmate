import { motion } from "motion/react";

export type TimerStatus = "idle" | "running" | "paused" | "completed";
export type SessionType = "focus" | "break";

interface TimerDisplayProps {
  minutes: number;
  seconds: number;
  status: TimerStatus;
  sessionType: SessionType;
  totalSeconds: number;
  remainingSeconds: number;
}

export function TimerDisplay({
  minutes,
  seconds,
  status,
  sessionType,
  totalSeconds,
  remainingSeconds,
}: TimerDisplayProps) {
  const getStatusColor = () => {
    switch (status) {
      case "idle":
        return "text-[#9ca3af]";
      case "running":
        return "text-[#4f46e5]";
      case "paused":
        return "text-[#f59e0b]";
      case "completed":
        return "text-[#10b981]";
      default:
        return "text-[#9ca3af]";
    }
  };

  const getStatusBgColor = () => {
    switch (status) {
      case "idle":
        return "bg-[#f9fafb]";
      case "running":
        return "bg-[#eef2ff]";
      case "paused":
        return "bg-[#fef3c7]";
      case "completed":
        return "bg-[#d1fae5]";
      default:
        return "bg-[#f9fafb]";
    }
  };

  const getStatusBorderColor = () => {
    switch (status) {
      case "idle":
        return "border-[#d1d5db]";
      case "running":
        return "border-[#4f46e5]";
      case "paused":
        return "border-[#f59e0b]";
      case "completed":
        return "border-[#10b981]";
      default:
        return "border-[#d1d5db]";
    }
  };

  const progress = totalSeconds > 0 ? (remainingSeconds / totalSeconds) * 100 : 100;
  const circumference = 2 * Math.PI * 140;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  const sessionText = sessionType === "focus" ? "Focus Time" : "Break Time";

  return (
    <div className="flex flex-col items-center justify-center gap-4">
      {/* Session Type Text Above Timer */}

      {/* Timer Circle */}
      <div className="relative w-80 h-80 flex items-center justify-center">
        {/* Background Circle */}
        <svg className="absolute inset-0 w-full h-full -rotate-90" viewBox="0 0 300 300">
          <circle
            cx="150"
            cy="150"
            r="140"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            className="text-muted/30"
          />
          {/* Progress Circle */}
          <motion.circle
            cx="150"
            cy="150"
            r="140"
            fill="none"
            stroke="currentColor"
            strokeWidth="8"
            strokeLinecap="round"
            strokeDasharray={circumference}
            strokeDashoffset={strokeDashoffset}
            className={getStatusColor()}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
          />
        </svg>

        {/* Timer Text */}
        <div className="relative flex flex-col items-center">
          <motion.div
            className={`text-7xl font-bold tabular-nums ${getStatusColor()} ${
              status === "running" ? "animate-pulse" : ""
            }`}
            role="timer"
            aria-live="polite"
          >
            {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
          </motion.div>
          <div className="mt-4 text-lg font-medium text-[#6b7280]">{sessionText}</div>
          <div className="mt-2 text-sm text-[#9ca3af] capitalize">
            {status === "idle"
              ? "Ready"
              : status === "running"
              ? "In Progress"
              : status === "paused"
              ? "Paused"
              : "Completed"}
          </div>
        </div>
      </div>
    </div>
  );
}
