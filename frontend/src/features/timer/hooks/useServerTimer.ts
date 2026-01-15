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
  const lastToastRef = useRef<Record<string, number>>({});
  const lastSyncRef = useRef<number>(0);

  const notifyOnce = useCallback((key: string, message: string, intervalMs = 8000) => {
    const now = Date.now();
    if (now - (lastToastRef.current[key] || 0) < intervalMs) {
      return;
    }
    lastToastRef.current[key] = now;
    toast.error(message);
  }, []);

  // target_timestamp로부터 남은 시간(초) 계산
  const calculateRemainingSeconds = useCallback((targetTimestamp?: string): number => {
    if (!targetTimestamp) return 0;
    const target = new Date(targetTimestamp).getTime();
    const now = Date.now();
    const remaining = Math.max(0, Math.floor((target - now) / 1000));
    return remaining;
  }, []);

  // 서버로부터 타이머 상태 업데이트
  const updateTimerState = useCallback((newState: TimerState) => {
    setTimerState(newState);
  }, []);

  const syncTimerState = useCallback(
    async (force = false) => {
      const now = Date.now();
      if (!force && now - lastSyncRef.current < 5000) {
        return;
      }
      lastSyncRef.current = now;
      const response = await timerService.getTimer(roomId);
      if (response.status === "success" && response.data) {
        updateTimerState(response.data);
      }
    },
    [roomId, updateTimerState]
  );

  // target_timestamp를 기반으로 타이머 카운트다운 시작
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

  // 타이머 제어 함수
  const startTimer = useCallback(
    async (sessionType: SessionType = "work") => {
      // 현재 상태 확인 - RUNNING이면 시작하지 않음
      if (timerState?.status === "running") {
        notifyOnce("timer_running", "타이머가 이미 실행 중입니다");
        await syncTimerState();
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
            notifyOnce("timer_running", "타이머가 이미 실행 중입니다");
            await syncTimerState();
          } else {
            notifyOnce("timer_start_failed", errorMessage);
            await syncTimerState();
          }
        }
      } catch (error) {
        console.error("Failed to start timer:", error);
        notifyOnce("timer_start_network", "네트워크 오류가 발생했습니다");
        await syncTimerState();
      } finally {
        setIsLoading(false);
      }
    },
    [roomId, updateTimerState, timerState?.status, notifyOnce, syncTimerState]
  );

  const pauseTimer = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await timerService.pauseTimer(roomId);
      if (response.status === "success" && response.data) {
        updateTimerState(response.data);
        toast.success("타이머가 일시정지되었습니다");
      } else {
        notifyOnce(
          "timer_pause_failed",
          response.error?.message || "타이머 일시정지에 실패했습니다"
        );
        await syncTimerState();
      }
    } catch (error) {
      console.error("Failed to pause timer:", error);
      notifyOnce("timer_pause_network", "네트워크 오류가 발생했습니다");
      await syncTimerState();
    } finally {
      setIsLoading(false);
    }
  }, [roomId, updateTimerState, notifyOnce, syncTimerState]);

  const resumeTimer = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await timerService.resumeTimer(roomId);
      if (response.status === "success" && response.data) {
        updateTimerState(response.data);
        toast.success("타이머가 재개되었습니다");
      } else {
        notifyOnce(
          "timer_resume_failed",
          response.error?.message || "타이머 재개에 실패했습니다"
        );
        await syncTimerState();
      }
    } catch (error) {
      console.error("Failed to resume timer:", error);
      notifyOnce("timer_resume_network", "네트워크 오류가 발생했습니다");
      await syncTimerState();
    } finally {
      setIsLoading(false);
    }
  }, [roomId, updateTimerState, notifyOnce, syncTimerState]);

  const resetTimer = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await timerService.resetTimer(roomId);
      if (response.status === "success" && response.data) {
        updateTimerState(response.data);
        toast.success("타이머가 리셋되었습니다");
      } else {
        notifyOnce(
          "timer_reset_failed",
          response.error?.message || "타이머 리셋에 실패했습니다"
        );
        await syncTimerState();
      }
    } catch (error) {
      console.error("Failed to reset timer:", error);
      notifyOnce("timer_reset_network", "네트워크 오류가 발생했습니다");
      await syncTimerState();
    } finally {
      setIsLoading(false);
    }
  }, [roomId, updateTimerState, notifyOnce, syncTimerState]);

  const completeSession = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await timerService.completeTimer(roomId);
      if (response.status === "success" && response.data) {
        updateTimerState(response.data);
        toast.success("세션이 완료되었습니다");
        return response.data;
      } else {
        notifyOnce(
          "timer_complete_failed",
          response.error?.message || "세션 완료 처리에 실패했습니다"
        );
        await syncTimerState();
        return null;
      }
    } catch (error) {
      console.error("Failed to complete session:", error);
      notifyOnce("timer_complete_network", "네트워크 오류가 발생했습니다");
      await syncTimerState();
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [roomId, updateTimerState, notifyOnce, syncTimerState]);

  // 시간 오차 방지 및 누락된 업데이트 확인을 위한 주기적 동기화
  useEffect(() => {
    if (!roomId) return;
    if (syncIntervalRef.current) {
      clearInterval(syncIntervalRef.current);
    }
    syncIntervalRef.current = setInterval(() => {
      void syncTimerState();
    }, 30000);

    return () => {
      if (syncIntervalRef.current) {
        clearInterval(syncIntervalRef.current);
      }
    };
  }, [roomId, syncTimerState]);

  // 표시용 값 계산
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

  // UI 표시를 위해 "work"를 "focus"로 변환
  const displaySessionType: "focus" | "break" =
    sessionType === "work" ? "focus" : "break";

  // 진행률 표시를 위한 전체 시간(초) 계산
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
    completeSession,
    updateTimerState,
  };
}
