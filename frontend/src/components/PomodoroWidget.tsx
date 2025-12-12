import { motion, AnimatePresence } from "framer-motion";
import { Play, Pause, RotateCcw, Coffee } from "lucide-react";
import { useState, useEffect } from "react";
import { Button } from "./ui/button-enhanced";

interface PomodoroWidgetProps {
  onSessionComplete?: (duration: number, type: "work" | "break") => void;
}

export function PomodoroWidget({ onSessionComplete }: PomodoroWidgetProps) {
  const [mode, setMode] = useState<"work" | "break">("work");
  const [timeLeft, setTimeLeft] = useState(25 * 60); // 25 minutes in seconds
  const [isRunning, setIsRunning] = useState(false);
  const [totalTime, setTotalTime] = useState(25 * 60);

  const presets = {
    work: [15, 25, 50],
    break: [5, 10, 15],
  };

  useEffect(() => {
    let interval: NodeJS.Timeout;

    if (isRunning && timeLeft > 0) {
      interval = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            setIsRunning(false);
            onSessionComplete?.(totalTime / 60, mode);
            // Auto switch to break/work
            const newMode = mode === "work" ? "break" : "work";
            const newTime = newMode === "work" ? 25 * 60 : 5 * 60;
            setMode(newMode);
            setTimeLeft(newTime);
            setTotalTime(newTime);
            return newTime;
          }
          return prev - 1;
        });
      }, 1000);
    }

    return () => clearInterval(interval);
  }, [isRunning, timeLeft, mode, totalTime, onSessionComplete]);

  const progress = ((totalTime - timeLeft) / totalTime) * 100;
  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  const handleReset = () => {
    setIsRunning(false);
    const newTime = mode === "work" ? 25 * 60 : 5 * 60;
    setTimeLeft(newTime);
    setTotalTime(newTime);
  };

  const handlePresetChange = (minutes: number) => {
    setIsRunning(false);
    const newTime = minutes * 60;
    setTimeLeft(newTime);
    setTotalTime(newTime);
  };

  const handleModeSwitch = () => {
    const newMode = mode === "work" ? "break" : "work";
    setMode(newMode);
    setIsRunning(false);
    const newTime = newMode === "work" ? 25 * 60 : 5 * 60;
    setTimeLeft(newTime);
    setTotalTime(newTime);
  };

  return (
    <div className="rounded-xl border border-border bg-card p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">포모도로 타이머</h3>
        <button
          onClick={handleModeSwitch}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-accent hover:bg-accent/80 transition-colors text-sm"
        >
          {mode === "work" ? (
            <>
              <Coffee className="h-4 w-4" />
              휴식으로 전환
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              집중으로 전환
            </>
          )}
        </button>
      </div>

      {/* Circular Progress */}
      <div className="relative w-64 h-64 mx-auto mb-6">
        <svg className="w-full h-full transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="128"
            cy="128"
            r="110"
            stroke="hsl(var(--muted))"
            strokeWidth="12"
            fill="none"
          />
          {/* Progress circle */}
          <motion.circle
            cx="128"
            cy="128"
            r="110"
            stroke={mode === "work" ? "hsl(var(--primary))" : "hsl(var(--chart-2))"}
            strokeWidth="12"
            fill="none"
            strokeLinecap="round"
            initial={{ strokeDasharray: "0 691" }}
            animate={{
              strokeDasharray: `${(progress / 100) * 691} 691`,
            }}
            transition={{ duration: 0.5 }}
          />
        </svg>

        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <AnimatePresence mode="wait">
            <motion.div
              key={`${minutes}:${seconds}`}
              initial={{ scale: 0.8, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.8, opacity: 0 }}
              className="text-center"
            >
              <p className="text-5xl font-bold tabular-nums">
                {String(minutes).padStart(2, "0")}:{String(seconds).padStart(2, "0")}
              </p>
              <p className="text-sm text-muted-foreground mt-2">
                {mode === "work" ? "집중 시간" : "휴식 시간"}
              </p>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-3 mb-6">
        <Button
          variant={isRunning ? "outline" : "primary"}
          size="md"
          onClick={() => setIsRunning(!isRunning)}
          className="gap-2"
        >
          {isRunning ? (
            <>
              <Pause className="h-4 w-4" />
              일시정지
            </>
          ) : (
            <>
              <Play className="h-4 w-4" />
              시작
            </>
          )}
        </Button>
        <Button
          variant="outline"
          size="md"
          onClick={handleReset}
          className="gap-2"
        >
          <RotateCcw className="h-4 w-4" />
          초기화
        </Button>
      </div>

      {/* Presets */}
      <div className="space-y-2">
        <p className="text-sm text-muted-foreground">빠른 설정</p>
        <div className="flex gap-2">
          {presets[mode].map((preset) => (
            <button
              key={preset}
              onClick={() => handlePresetChange(preset)}
              disabled={isRunning}
              className={`flex-1 px-3 py-2 text-sm rounded-lg border transition-colors ${
                totalTime === preset * 60
                  ? "bg-primary/10 text-primary border-primary/50"
                  : "bg-background border-border hover:bg-accent"
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {preset}분
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
