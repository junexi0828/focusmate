import { motion } from "framer-motion";

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
        return "text-muted-foreground";
      case "running":
        return "text-primary";
      case "paused":
        return "text-warning";
      case "completed":
        return "text-secondary";
      default:
        return "text-muted-foreground";
    }
  };

  const getStatusBgColor = () => {
    switch (status) {
      case "idle":
        return "bg-muted";
      case "running":
        return "bg-primary/10";
      case "paused":
        return "bg-warning/10";
      case "completed":
        return "bg-secondary/10";
      default:
        return "bg-muted";
    }
  };

  const progress = totalSeconds > 0 ? (remainingSeconds / totalSeconds) * 100 : 100;
  const circumference = 2 * Math.PI * 140;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  const sessionText = sessionType === "focus" ? "집중 시간" : "휴식 시간";

  return (
    <div className="flex flex-col items-center justify-center gap-8">
      {/* Session Type Badge */}
      <div
        className={`px-4 py-2 rounded-full ${getStatusBgColor()} ${getStatusColor()} transition-colors duration-300`}
      >
        <span className="font-medium">{sessionText}</span>
      </div>

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
            className={`text-7xl tabular-nums tracking-tight ${getStatusColor()}`}
            animate={status === "running" ? { scale: [1, 1.02, 1] } : {}}
            transition={{ duration: 1, repeat: status === "running" ? Infinity : 0 }}
          >
            {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
          </motion.div>
          <div className="text-sm text-muted-foreground mt-2 capitalize">
            {status === "idle"
              ? "준비"
              : status === "running"
              ? "진행 중"
              : status === "paused"
              ? "일시정지"
              : "완료"}
          </div>
        </div>
      </div>

      {/* Completion Animation */}
      {status === "completed" && (
        <motion.div
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          className="text-center"
        >
          <div className="text-2xl">🎉</div>
          <p className="text-sm text-muted-foreground mt-2">
            {sessionType === "focus" ? "집중 시간 완료!" : "휴식 완료!"}
          </p>
        </motion.div>
      )}
    </div>
  );
}

