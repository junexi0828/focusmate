import { useState, useEffect, useCallback, useRef } from "react";
import { TimerStatus, SessionType } from "../components/Timer";

interface UseTimerProps {
  focusTime: number; // in minutes
  breakTime: number; // in minutes
  onSessionComplete?: (sessionType: SessionType) => void;
}

export function useTimer({ focusTime, breakTime, onSessionComplete }: UseTimerProps) {
  const [sessionType, setSessionType] = useState<SessionType>("focus");
  const [status, setStatus] = useState<TimerStatus>("idle");
  const [timeLeft, setTimeLeft] = useState(focusTime * 60); // in seconds
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  const totalSeconds = sessionType === "focus" ? focusTime * 60 : breakTime * 60;

  const clearTimer = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  const startTimer = useCallback(() => {
    if (status === "completed") {
      // Reset to focus session when starting from completed state
      setSessionType("focus");
      setTimeLeft(focusTime * 60);
    }
    setStatus("running");
  }, [status, focusTime]);

  const pauseTimer = useCallback(() => {
    setStatus("paused");
    clearTimer();
  }, [clearTimer]);

  const resetTimer = useCallback(() => {
    clearTimer();
    setStatus("idle");
    setSessionType("focus");
    setTimeLeft(focusTime * 60);
  }, [clearTimer, focusTime]);

  const switchSession = useCallback(() => {
    const newSessionType = sessionType === "focus" ? "break" : "focus";
    setSessionType(newSessionType);
    const newTime = newSessionType === "focus" ? focusTime * 60 : breakTime * 60;
    setTimeLeft(newTime);
    setStatus("idle");
  }, [sessionType, focusTime, breakTime]);

  // Timer countdown effect
  useEffect(() => {
    if (status === "running") {
      intervalRef.current = setInterval(() => {
        setTimeLeft((prev) => {
          if (prev <= 1) {
            clearTimer();
            setStatus("completed");
            onSessionComplete?.(sessionType);
            return 0;
          }
          return prev - 1;
        });
      }, 1000);
    } else {
      clearTimer();
    }

    return () => clearTimer();
  }, [status, sessionType, clearTimer, onSessionComplete]);

  const minutes = Math.floor(timeLeft / 60);
  const seconds = timeLeft % 60;

  return {
    minutes,
    seconds,
    status,
    sessionType,
    totalSeconds,
    remainingSeconds: timeLeft,
    startTimer,
    pauseTimer,
    resetTimer,
    switchSession,
  };
}
