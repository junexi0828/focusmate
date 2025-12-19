/**
 * 서버 사이드 타이머 훅
 * 서버의 타이머 상태를 기반으로 클라이언트 타이머를 동기화
 */

import { useState, useEffect, useCallback, useRef } from "react";
import { TimerState } from "../types/timer.types";
import { timerService } from "../services/timerService";
import { toast } from "sonner";

export type TimerStatus = "idle" | "running" | "paused" | "completed";
export type SessionType = "work" | "break";

interface UseServerTimerProps {
  roomId: string;
  initialTimerState?: TimerState;
  onSessionComplete?: (sessionType: SessionType) => void;
}

export function useServerTimer({
  roomId,
  initialTimerState,
  onSessionComplete,
}: UseServerTimerProps) {
  const [timerState, setTimerState] = useState<TimerState | null>(
    initialTimerState || null
  );
  const [isLoading, setIsLoading] = useState(false);
  const syncIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const countdownIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Calculate remaining seconds from target_timestamp
  const calculateRemainingSeconds = useCallback((targetTimestamp?: string): number => {
    if (!targetTimestamp) return 0;
    const target = new Date(targetTimestamp).getTime();
    const now = Date.now();
    const remaining = Math.max(0, Math.floor((target - now) / 1000));
    return remaining;
  }, []);

  // Update timer state from server
  const updateTimerState = useCallback((newState: TimerState) => {
    setTimerState(newState);
  }, []);

  // Start timer countdown based on target_timestamp
  useEffect(() => {
    if (timerState?.status === "running" && timerState.target_timestamp) {
      // Clear existing interval
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
      }

      // Update every second
      countdownIntervalRef.current = setInterval(() => {
        const remaining = calculateRemainingSeconds(timerState.target_timestamp);

        if (remaining <= 0) {
          // Timer completed
          setTimerState((prev) => {
            if (prev) {
              return {
                ...prev,
                status: "completed",
                remaining_seconds: 0,
              };
            }
            return prev;
          });

          if (countdownIntervalRef.current) {
            clearInterval(countdownIntervalRef.current);
          }

          // Trigger completion callback
          if (onSessionComplete) {
            onSessionComplete(timerState.session_type);
          }
        } else {
          // Update remaining seconds
          setTimerState((prev) => {
            if (prev) {
              return {
                ...prev,
                remaining_seconds: remaining,
              };
            }
            return prev;
          });
        }
      }, 1000);
    } else {
      // Clear interval when not running
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
      }
    }

    return () => {
      if (countdownIntervalRef.current) {
        clearInterval(countdownIntervalRef.current);
      }
    };
  }, [timerState?.status, timerState?.target_timestamp, timerState?.session_type, calculateRemainingSeconds, onSessionComplete]);

  // Timer control functions
  const startTimer = useCallback(
    async (sessionType: SessionType = "work") => {
      // 현재 상태 확인 - RUNNING이면 시작하지 않음
      if (timerState?.status === "running") {
        toast.error("타이머가 이미 실행 중입니다");
        return;
      }

      setIsLoading(true);
      try {
        const response = await timerService.startTimer(roomId, sessionType);
        if (response.status === "success" && response.data) {
          updateTimerState(response.data);
          toast.success("타이머가 시작되었습니다");
        } else {
          const errorMessage =
            response.error?.message || "타이머 시작에 실패했습니다";
          if (response.error?.code === "TIMER_ALREADY_RUNNING") {
            toast.error("타이머가 이미 실행 중입니다");
          } else {
            toast.error(errorMessage);
          }
        }
      } catch (error) {
        console.error("Failed to start timer:", error);
        toast.error("네트워크 오류가 발생했습니다");
      } finally {
        setIsLoading(false);
      }
    },
    [roomId, updateTimerState, timerState?.status]
  );

  const pauseTimer = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await timerService.pauseTimer(roomId);
      if (response.status === "success" && response.data) {
        updateTimerState(response.data);
        toast.success("타이머가 일시정지되었습니다");
      } else {
        toast.error(
          response.error?.message || "타이머 일시정지에 실패했습니다"
        );
      }
    } catch (error) {
      console.error("Failed to pause timer:", error);
      toast.error("네트워크 오류가 발생했습니다");
    } finally {
      setIsLoading(false);
    }
  }, [roomId, updateTimerState]);

  const resumeTimer = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await timerService.resumeTimer(roomId);
      if (response.status === "success" && response.data) {
        updateTimerState(response.data);
        toast.success("타이머가 재개되었습니다");
      } else {
        toast.error(response.error?.message || "타이머 재개에 실패했습니다");
      }
    } catch (error) {
      console.error("Failed to resume timer:", error);
      toast.error("네트워크 오류가 발생했습니다");
    } finally {
      setIsLoading(false);
    }
  }, [roomId, updateTimerState]);

  const resetTimer = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await timerService.resetTimer(roomId);
      if (response.status === "success" && response.data) {
        updateTimerState(response.data);
        toast.success("타이머가 리셋되었습니다");
      } else {
        toast.error(response.error?.message || "타이머 리셋에 실패했습니다");
      }
    } catch (error) {
      console.error("Failed to reset timer:", error);
      toast.error("네트워크 오류가 발생했습니다");
    } finally {
      setIsLoading(false);
    }
  }, [roomId, updateTimerState]);

  // Calculate display values
  const remainingSeconds = timerState
    ? timerState.status === "running"
      ? calculateRemainingSeconds(timerState.target_timestamp)
      : timerState.remaining_seconds
    : 0;

  const minutes = Math.floor(remainingSeconds / 60);
  const seconds = remainingSeconds % 60;

  const status: TimerStatus = timerState?.status || "idle";
  const sessionType: SessionType =
    timerState?.session_type === "work" ? "work" : "break";

  // For display purposes, convert "work" to "focus"
  const displaySessionType: "focus" | "break" =
    sessionType === "work" ? "focus" : "break";

  // Calculate total seconds for progress
  const totalSeconds = timerState
    ? sessionType === "work"
      ? (timerState as any).work_duration || 1500
      : (timerState as any).break_duration || 300
    : 0;

  return {
    minutes,
    seconds,
    status,
    sessionType,
    displaySessionType, // For UI components that use "focus" | "break"
    totalSeconds,
    remainingSeconds,
    isLoading,
    timerState,
    startTimer,
    pauseTimer,
    resumeTimer,
    resetTimer,
    updateTimerState,
  };
}

