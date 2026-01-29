import React, { useState, useEffect, useRef } from "react";
import { useParams } from "@tanstack/react-router";
import { GlassCard } from "../components/ui/glass-card";
import { Button } from "../components/ui/button";
import { TimerDisplay } from "../features/timer/components/TimerDisplay";
import { TimerControls } from "../features/timer/components/TimerControls";
import { ParticipantList } from "../features/participants/components/ParticipantListOriginal";
import { RoomSettingsDialog } from "../features/room/components/RoomSettingsDialog";
import { LogOut, Copy, Check, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { roomService } from "../features/room/services/roomService";
// import { Room } from "../features/room/types/room.types"; // Handled by context

import { RoomPageSkeleton } from "../components/ui/room-skeleton";
import { WebSocketStatus } from "../components/WebSocketStatus";
import { WebSocketConnectionBanner } from "../components/WebSocketConnectionBanner";
// import { RoomChatMessage } from "../types/room-chat";
import { useRoomContext } from "../contexts/RoomContext";
import { wsClient } from "../lib/websocket";
import { timerService } from "../features/timer/services/timerService";
import { authService } from "../features/auth/services/authService";

type QuickSignalIcon = {
  type: "emoji" | "custom";
  value: string;
  fallback: string;
};

type QuickSignal = {
  id: string;
  label: string;
  text: string;
  icon: QuickSignalIcon;
};

const QUICK_SIGNALS: QuickSignal[] = [
  {
    id: "greet",
    label: "인사",
    text: "들어왔어요! 집중 구경하러 왔습니다.",
    icon: { type: "emoji", value: "👋", fallback: "👋" },
  },
  {
    id: "start",
    label: "시작",
    text: "타이머 ON! 잡담 금지, 집중 개시!",
    icon: { type: "emoji", value: "🏁", fallback: "🏁" },
  },
  {
    id: "progress",
    label: "진행",
    text: "진행중이에요. 집중력 풀가동!",
    icon: { type: "emoji", value: "⏱", fallback: "⏱" },
  },
  {
    id: "focus",
    label: "집중",
    text: "집중 모드! 오늘도 뇌근육 운동!",
    icon: { type: "emoji", value: "💪", fallback: "💪" },
  },
  {
    id: "brain-check",
    label: "뇌점검",
    text: "뇌 회전수 체크 완료. 정상입니다!",
    icon: { type: "emoji", value: "🧠", fallback: "🧠" },
  },
  {
    id: "done",
    label: "완료",
    text: "완료! 뇌에 불 켜고 나왔어요.",
    icon: { type: "emoji", value: "✅", fallback: "✅" },
  },
  {
    id: "cheer",
    label: "수고",
    text: "수고했어요! 집중력 만렙 도전 성공!",
    icon: { type: "emoji", value: "🙌", fallback: "🙌" },
  },
];

interface RoomPageProps {
  onLeaveRoom: () => void;
}

export function RoomPage({ onLeaveRoom }: RoomPageProps) {
  const { roomId } = useParams({ from: "/room/$roomId" });

  const {
      roomId: currentRoomId,
      room,
      isLoading,
      isLoadingParticipants,
      listParticipants,
      participantCount,
      maxParticipants,
      currentParticipantId,
      isHost,
      timer,
      joinRoom,
      leaveRoom,
      isConnected: wsConnected,
      isConnecting: wsConnecting,
      connectionError: wsError,
      reconnectAttempts,
      chatMessages,
      sendChatMessage,
  } = useRoomContext();

  const [focusTime, setFocusTime] = useState(25);
  const [breakTime, setBreakTime] = useState(5);
  const [autoStart, setAutoStart] = useState(false);
  const [removeOnLeave, setRemoveOnLeave] = useState(false);
  const [copied, setCopied] = useState(false);
  const [chatInput, setChatInput] = useState("");
  const chatScrollRef = useRef<HTMLDivElement | null>(null);
  const CHAT_MAX_LENGTH = 300;

  // Initial Join Logic
  useEffect(() => {
    if (!roomId) {
      toast.error("방 ID가 없습니다");
      onLeaveRoom();
      return;
    }

    if (roomId && roomId !== currentRoomId) {
      // joinRoom will automatically handle leaving previous room if needed
      joinRoom(roomId);
    }
  }, [roomId, currentRoomId, joinRoom, onLeaveRoom]);

  // Sync Room Settings to Local State for Dialog
  useEffect(() => {
    if (room) {
        setFocusTime(room.work_duration);
        setBreakTime(room.break_duration);
        setAutoStart(room.auto_start_break);
        setRemoveOnLeave(room.remove_on_leave ?? false);
    }
  }, [room]);

  // Chat Scroll
  useEffect(() => {
    if (!chatScrollRef.current) return;
    chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
  }, [chatMessages]);

  // Leave room on unmount disabled to support Global Timer
  // User must explicitly leave via the Exit button
  useEffect(() => {
    // No cleanup needed
  }, []);

  const getQuickSignalIcon = (signal: QuickSignal): string => {
    return signal.icon.type === "emoji" ? signal.icon.value : signal.icon.fallback;
  };

  const handleCopyInviteLink = async () => {
    try {
      await navigator.clipboard.writeText(window.location.href);
      setCopied(true);
      toast.success("초대 링크가 복사되었습니다");
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      toast.error("링크 복사에 실패했습니다");
    }
  };

  const handleDeleteRoom = async () => {
    if (!currentRoomId) return;
    if (!confirm("정말 방을 삭제하시겠습니까?")) return;

    try {
      const response = await roomService.deleteRoom(currentRoomId);
      if (response.status === "success") {
        toast.success("방이 삭제되었습니다");
        setTimeout(() => {
          onLeaveRoom();
          leaveRoom();
        }, 1000);
      } else {
        if (response.error?.code === "FORBIDDEN" || response.error?.code === "ROOM_HOST_REQUIRED") {
          toast.error("방장만 방을 삭제할 수 있습니다");
        } else {
          toast.error(response.error?.message || "방 삭제에 실패했습니다");
        }
      }
    } catch (error) {
      console.error("Failed to delete room:", error);
      toast.error("네트워크 오류가 발생했습니다");
    }
  };

  const handleLeaveRoom = async () => {
    if (confirm("방에서 나가시겠습니까?")) {
        await leaveRoom();
        onLeaveRoom();
    }
  };

  const handleSendMessage = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!chatInput.trim() || !currentParticipantId || !currentRoomId) return;

    const content = chatInput.trim();

    // Send via Context (validation handled in context)
    sendChatMessage(content);
    setChatInput("");
  };

  const handleQuickSignal = (signal: QuickSignal) => {
      if (!currentParticipantId || !currentRoomId) return;
      const icon = getQuickSignalIcon(signal);
      const content = `${icon} ${signal.text}`.trim();

      // Send immediately
      sendChatMessage(content);
  };

  const handleUpdateSettings = async (
    newFocusTime: number,
    newBreakTime: number,
    newAutoStart: boolean,
    newRemoveOnLeave: boolean
  ) => {
    if (!currentRoomId) return;

    try {
      const response = await roomService.updateRoomSettings(currentRoomId, {
        work_duration: newFocusTime * 60,
        break_duration: newBreakTime * 60,
        auto_start_break: newAutoStart,
        remove_on_leave: newRemoveOnLeave,
      });

      if (response.status === "success" && response.data) {
        setFocusTime(newFocusTime);
        setBreakTime(newBreakTime);
        setAutoStart(newAutoStart);
        setRemoveOnLeave(newRemoveOnLeave);

        // Reload timer state to reflect duration changes
        if (currentRoomId) {
          try {
            const timerResponse = await timerService.getTimer(currentRoomId);
            if (timerResponse.status === "success" && timerResponse.data) {
              timer.updateTimerState(timerResponse.data);
            }
          } catch (error) {
            console.error("Failed to reload timer state:", error);
          }
        }

        toast.success("설정이 업데이트되었습니다");
      } else {
        if (response.error?.code === "FORBIDDEN" || response.error?.code === "ROOM_HOST_REQUIRED") {
          toast.error("방장만 방 설정을 변경할 수 있습니다");
        } else {
          toast.error(response.error?.message || "설정 업데이트에 실패했습니다");
        }
      }
    } catch (error) {
      console.error("Failed to update settings:", error);
      toast.error("네트워크 오류가 발생했습니다");
    }
  };

  if (isLoading) {
    return <RoomPageSkeleton />;
  }

  if (!room && !isLoading && currentRoomId === roomId) {
      return (
          <div className="flex flex-col items-center justify-center p-12">
              <p className="text-red-500 mb-4">방 정보를 불러올 수 없습니다.</p>
              <Button onClick={onLeaveRoom}>돌아가기</Button>
          </div>
      );
  }

  if (roomId !== currentRoomId) {
       return <RoomPageSkeleton />;
  }

  return (
    <div className="min-h-screen flex flex-col bg-slate-50/80 dark:bg-slate-950/80 transition-colors duration-300">
      {/* Header */}
      <header className="border-b bg-white/70 dark:bg-black/60 backdrop-blur-md border-white/20 dark:border-white/10 shadow-sm transition-colors duration-300">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h1 className="truncate">{room?.room_name || room?.name}</h1>
                <WebSocketStatus showLabel={false} />
              </div>
              <div className="flex items-center gap-2 mt-1">
                <p className="text-sm text-muted-foreground">
                  방 ID: {room?.room_id || room?.id}
                </p>
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2"
                  onClick={handleCopyInviteLink}
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
                focusTime={focusTime}
                breakTime={breakTime}
                autoStart={autoStart}
                removeOnLeave={removeOnLeave}
                onUpdateSettings={handleUpdateSettings}
                onDeleteRoom={handleDeleteRoom}
                isHost={isHost}
              />
              {isHost && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleDeleteRoom}
                  className="hidden sm:flex"
                >
                  <Trash2 className="w-4 h-4 mr-2" />방 삭제
                </Button>
              )}
              <Button variant="outline" onClick={handleLeaveRoom}>
                <LogOut className="w-4 h-4 mr-2" />
                나가기
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* WebSocket Status Banner */}
      <div className="container mx-auto px-4 py-2">
        <WebSocketConnectionBanner
          isConnected={wsConnected}
          isConnecting={wsConnecting}
          connectionError={wsError}
          reconnectAttempts={reconnectAttempts}
          maxReconnectAttempts={wsClient.getMaxReconnectAttempts()}
          onReconnect={() => {
            if (currentRoomId) {
              wsClient.connect(currentRoomId).catch((error) => {
                console.error("Manual reconnect failed:", error);
                toast.error("재연결에 실패했습니다");
              });
            }
          }}
        />
      </div>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-[1fr_350px] gap-8">
          {/* Timer Section */}
          <div className="flex flex-col items-center justify-center gap-8">
            <TimerDisplay
              minutes={timer.minutes}
              seconds={timer.seconds}
              status={timer.status}
              sessionType={timer.displaySessionType}
              totalSeconds={timer.totalSeconds}
              remainingSeconds={timer.remainingSeconds}
            />
            <TimerControls
              status={timer.status}
              onStart={async () => {
                if (timer.status === "running") {
                  toast.error("타이머가 이미 실행 중입니다");
                  return;
                }

                if (timer.status === "paused") {
                  timer.resumeTimer();
                  wsClient.sendResumeTimer();
                } else if (timer.status === "completed") {
                  const nextSessionType = timer.sessionType === "work" ? "break" : "work";
                  const newState = await timer.completeSession();
                  if (newState) {
                    if (newState.status === "idle") {
                      await timer.startTimer(nextSessionType);
                      wsClient.sendStartTimer(nextSessionType);
                    } else if (newState.status === "running") {
                      wsClient.sendStartTimer(nextSessionType);
                    }
                  }
                } else {
                  // idle state: start current session type
                  timer.startTimer(timer.sessionType);
                  wsClient.sendStartTimer(timer.sessionType);
                }
              }}
              onPause={() => {
                timer.pauseTimer();
                wsClient.sendPauseTimer();
              }}
              onReset={() => {
                timer.resetTimer();
                wsClient.sendResetTimer();
              }}
            />
          </div>

          {/* Participant List */}
          <div className="lg:block hidden">
            <ParticipantList
              participants={listParticipants}
              isLoading={isLoadingParticipants}
              currentCount={participantCount ?? undefined}
              maxCount={maxParticipants}
            />
          </div>
        </div>

        {/* Mobile Participant List */}
        <div className="lg:hidden mt-8">
            <ParticipantList
              participants={listParticipants}
              isLoading={isLoadingParticipants}
              currentCount={participantCount ?? undefined}
              maxCount={maxParticipants}
            />
        </div>

        <section className="mt-10">
          <GlassCard>
            <div className="border-b border-white/10 px-4 py-3">
              <h2 className="text-base font-semibold">방 채팅</h2>
            </div>
            <div className="flex flex-col gap-4 p-4">
              <div className="flex flex-wrap gap-2">
                {QUICK_SIGNALS.map((signal) => {
                  const icon = getQuickSignalIcon(signal);
                  return (
                    <Button
                      key={signal.id}
                      variant="secondary"
                      size="sm"
                      className="h-8 px-3"
                      onClick={() => handleQuickSignal(signal)}
                    >
                      <span className="mr-1 text-lg">{icon}</span>
                      {signal.label}
                    </Button>
                  );
                })}
              </div>

              <div
                ref={chatScrollRef}
                className="min-h-[300px] rounded-lg border bg-background p-3"
              >
                {chatMessages.length === 0 ? (
                  <p className="text-sm text-muted-foreground">
                    아직 메시지가 없습니다.
                  </p>
                ) : (
                  <div className="flex flex-col gap-3">
                    {chatMessages.map((message) => {
                      // Check both currentParticipantId and user ID for anonymous users
                      const currentUserId = authService.getCurrentUser()?.id;
                      const isMine = message.sender_id === currentParticipantId ||
                                     (currentUserId && message.sender_id === currentUserId);
                      const timeLabel = new Date(
                        message.created_at
                      ).toLocaleTimeString("ko-KR", {
                        hour: "2-digit",
                        minute: "2-digit",
                      });
                      return (
                        <div
                          key={message.id}
                          className={`flex ${isMine ? "justify-end" : "justify-start"}`}
                        >
                          <div
                            className={`max-w-[80%] rounded-lg px-3 py-2 text-sm ${
                              isMine
                                ? "bg-primary text-primary-foreground"
                                : "bg-muted text-foreground"
                            }`}
                          >
                            <div className="mb-1 text-xs opacity-70">
                              {isMine ? "나" : message.sender_name} · {timeLabel}
                            </div>
                            <div className="whitespace-pre-wrap break-all">
                              {message.content}
                            </div>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="flex gap-2">
                <input
                  className="flex-1 rounded-md border bg-background px-3 py-2 text-sm"
                  placeholder="메시지 입력"
                  value={chatInput}
                  onChange={(event) => setChatInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === "Enter" && !event.nativeEvent.isComposing) {
                      event.preventDefault();
                      handleSendMessage();
                    }
                  }}
                  maxLength={CHAT_MAX_LENGTH}
                />
                <Button
                  variant="default"
                  onClick={handleSendMessage}
                  disabled={!chatInput.trim()}
                >
                  전송
                </Button>
              </div>
            </div>
          </GlassCard>
        </section>
      </main>
    </div>
  );
}

export default RoomPage;
