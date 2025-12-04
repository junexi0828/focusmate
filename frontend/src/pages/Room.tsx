import React, { useState } from "react";
import { Button } from "../components/ui/button";
import { TimerDisplay } from "../features/timer/components/TimerDisplay";
import { TimerControls } from "../features/timer/components/TimerControls";
import {
  ParticipantList,
  Participant,
} from "../features/participants/components/ParticipantListOriginal";
import { RoomSettingsDialog } from "../features/room/components/RoomSettingsDialog";
import { useTimer } from "../features/timer/hooks/useTimer";
import { LogOut, Copy, Check } from "lucide-react";
import { toast } from "sonner";

interface RoomPageProps {
  roomName: string;
  roomId: string;
  initialFocusTime: number;
  initialBreakTime: number;
  onLeaveRoom: () => void;
}

export function RoomPage({
  roomName,
  roomId,
  initialFocusTime,
  initialBreakTime,
  onLeaveRoom,
}: RoomPageProps) {
  const [focusTime, setFocusTime] = useState(initialFocusTime);
  const [breakTime, setBreakTime] = useState(initialBreakTime);
  const [autoStart, setAutoStart] = useState(false);
  const [copied, setCopied] = useState(false);

  // Mock participants
  const [participants] = useState<Participant[]>([
    { id: "1", name: "김철수", isHost: true },
    { id: "2", name: "이영희", isHost: false },
    { id: "3", name: "박민수", isHost: false },
  ]);

  const currentUser = participants[0]; // Mock current user as host

  const {
    minutes,
    seconds,
    status,
    sessionType,
    totalSeconds,
    remainingSeconds,
    startTimer,
    pauseTimer,
    resetTimer,
    switchSession,
  } = useTimer({
    focusTime,
    breakTime,
    onSessionComplete: (completedSessionType) => {
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification(
          completedSessionType === "focus" ? "집중 시간 완료!" : "휴식 종료!",
          {
            body:
              completedSessionType === "focus"
                ? "잘하셨습니다! 이제 휴식을 취하세요."
                : "다시 집중할 시간입니다!",
            icon: "/favicon.ico",
          }
        );
      }
      toast.success(
        completedSessionType === "focus" ? "집중 시간 완료!" : "휴식 종료!",
        {
          description:
            completedSessionType === "focus"
              ? "잘하셨습니다! 이제 휴식을 취하세요."
              : "다시 집중할 시간입니다!",
        }
      );

      if (autoStart) {
        setTimeout(() => {
          switchSession();
          startTimer();
        }, 3000);
      }
    },
  });

  const handleUpdateSettings = (
    newFocusTime: number,
    newBreakTime: number,
    newAutoStart: boolean
  ) => {
    setFocusTime(newFocusTime);
    setBreakTime(newBreakTime);
    setAutoStart(newAutoStart);
    toast.success("설정이 업데이트되었습니다");
  };

  const handleDeleteRoom = () => {
    toast.success("방이 삭제되었습니다");
    setTimeout(() => {
      onLeaveRoom();
    }, 1000);
  };

  const handleCopyRoomId = async () => {
    try {
      await navigator.clipboard.writeText(roomId);
      setCopied(true);
      toast.success("방 ID가 복사되었습니다");
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      toast.error("복사에 실패했습니다");
    }
  };

  // Request notification permission on mount
  useState(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
  });

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="flex-1 min-w-0">
              <h1 className="truncate">{roomName}</h1>
              <div className="flex items-center gap-2 mt-1">
                <p className="text-sm text-muted-foreground">방 ID: {roomId}</p>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2"
                  onClick={handleCopyRoomId}
                >
                  {copied ? (
                    <Check className="w-3 h-3" />
                  ) : (
                    <Copy className="w-3 h-3" />
                  )}
                </Button>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <RoomSettingsDialog
                isHost={currentUser.isHost}
                focusTime={focusTime}
                breakTime={breakTime}
                autoStart={autoStart}
                onUpdateSettings={handleUpdateSettings}
                onDeleteRoom={handleDeleteRoom}
              />
              <Button variant="outline" onClick={onLeaveRoom}>
                <LogOut className="w-4 h-4 mr-2" />
                나가기
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-[1fr_350px] gap-8">
          {/* Timer Section */}
          <div className="flex flex-col items-center justify-center gap-8">
            <TimerDisplay
              minutes={minutes}
              seconds={seconds}
              status={status}
              sessionType={sessionType}
              totalSeconds={totalSeconds}
              remainingSeconds={remainingSeconds}
            />
            <TimerControls
              status={status}
              onStart={startTimer}
              onPause={pauseTimer}
              onReset={resetTimer}
            />

            {status === "completed" && (
              <Button
                variant="secondary"
                onClick={switchSession}
                className="mt-4"
              >
                {sessionType === "focus" ? "휴식 시작" : "집중 시작"}
              </Button>
            )}
          </div>

          {/* Participant List */}
          <div className="lg:block hidden">
            <ParticipantList participants={participants} />
          </div>
        </div>

        {/* Mobile Participant List */}
        <div className="lg:hidden mt-8">
          <ParticipantList participants={participants} />
        </div>
      </main>
    </div>
  );
}

export default RoomPage;
