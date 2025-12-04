import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Button } from "../components/ui/button";
import { TimerDisplay } from "../features/timer/components/TimerDisplay";
import { TimerControls } from "../features/timer/components/TimerControls";
import {
  ParticipantList,
  Participant,
} from "../features/participants/components/ParticipantListOriginal";
import { RoomSettingsDialog } from "../features/room/components/RoomSettingsDialog";
import { useServerTimer } from "../features/timer/hooks/useServerTimer";
import { LogOut, Copy, Check, Loader2 } from "lucide-react";
import { toast } from "sonner";
import { roomService } from "../features/room/services/roomService";
import { Room } from "../features/room/types/room.types";
import { LoadingSpinner } from "../components/ui/loading";
import { wsClient } from "../lib/websocket";
import { participantService } from "../features/participants/services/participantService";
import { Participant as ParticipantType } from "../features/participants/types/participant.types";
import { RoomPageSkeleton } from "../components/ui/room-skeleton";
import { WebSocketStatus, useWebSocketStatus } from "../components/WebSocketStatus";

interface RoomPageProps {
  onLeaveRoom: () => void;
}

export function RoomPage({ onLeaveRoom }: RoomPageProps) {
  const { roomId } = useParams<{ roomId: string }>();
  const navigate = useNavigate();
  const [room, setRoom] = useState<Room | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [focusTime, setFocusTime] = useState(25);
  const [breakTime, setBreakTime] = useState(5);
  const [autoStart, setAutoStart] = useState(false);
  const [copied, setCopied] = useState(false);

  const [participants, setParticipants] = useState<Participant[]>([]);
  const [isLoadingParticipants, setIsLoadingParticipants] = useState(false);
  const [currentParticipantId, setCurrentParticipantId] = useState<string | null>(null);
  const [participantName, setParticipantName] = useState<string>("");

  // WebSocket 연결 상태
  const { isConnected: wsConnected, isConnecting: wsConnecting, connectionError: wsError } = useWebSocketStatus(roomId || null);

  // WebSocket 에러 메시지 표시
  useEffect(() => {
    if (wsError) {
      toast.error(wsError, { duration: 3000 });
    }
  }, [wsError]);

  // Load room data on mount
  useEffect(() => {
    if (!roomId) {
      toast.error("방 ID가 없습니다");
      navigate("/");
      return;
    }

    const loadRoom = async () => {
      setIsLoading(true);
      try {
        const response = await roomService.getRoom(roomId);
        if (response.status === "success" && response.data) {
          const roomData = response.data;
          setRoom(roomData);
          setFocusTime(roomData.work_duration / 60); // seconds to minutes
          setBreakTime(roomData.break_duration / 60); // seconds to minutes
          setAutoStart(roomData.auto_start_break || false);

          // Load participants from API
          await loadParticipants(roomId);

          // Join room if not already joined
          await joinRoomIfNeeded(roomId);
        } else {
          if (response.error?.code === "ROOM_NOT_FOUND") {
            toast.error("방을 찾을 수 없습니다");
          } else {
            toast.error(response.error?.message || "방 정보를 불러오는데 실패했습니다");
          }
          navigate("/");
        }
      } catch (error) {
        console.error("Failed to load room:", error);
        toast.error("네트워크 오류가 발생했습니다");
        navigate("/");
      } finally {
        setIsLoading(false);
      }
    };

    loadRoom();
  }, [roomId, navigate]);

  // Load participants
  const loadParticipants = async (roomId: string) => {
    setIsLoadingParticipants(true);
    try {
      const response = await participantService.getParticipants(roomId);
      if (response.status === "success" && response.data) {
        // Convert API participant format to UI format
        const uiParticipants: Participant[] = response.data.map((p) => ({
          id: p.participant_id,
          name: p.name,
          isHost: p.is_host,
        }));
        setParticipants(uiParticipants);
      }
    } catch (error) {
      console.error("Failed to load participants:", error);
    } finally {
      setIsLoadingParticipants(false);
    }
  };

  // Join room if needed
  const joinRoomIfNeeded = async (roomId: string) => {
    // Check if user already has a participant ID in localStorage
    const storedParticipantId = localStorage.getItem(`participant_${roomId}`);
    if (storedParticipantId) {
      setCurrentParticipantId(storedParticipantId);
      return;
    }

    // Get participant name from localStorage or prompt
    let name = localStorage.getItem("participant_name") || "";
    if (!name) {
      // Prompt for name
      const input = prompt("참여자 이름을 입력해주세요:");
      if (!input || input.trim().length === 0) {
        toast.error("이름을 입력해야 방에 참여할 수 있습니다");
        navigate("/");
        return;
      }
      name = input.trim();
      localStorage.setItem("participant_name", name);
    }

    try {
      const response = await participantService.joinRoom(roomId, {
        participant_name: name,
      });
      if (response.status === "success" && response.data) {
        setCurrentParticipantId(response.data.participant_id);
        localStorage.setItem(
          `participant_${roomId}`,
          response.data.participant_id
        );
        setParticipantName(response.data.name);
        // Reload participants list
        await loadParticipants(roomId);
        toast.success("방에 참여했습니다!");
      } else {
        toast.error(
          response.error?.message || "방 참여에 실패했습니다"
        );
      }
    } catch (error) {
      console.error("Failed to join room:", error);
      toast.error("네트워크 오류가 발생했습니다");
    }
  };

  // Leave room on unmount
  useEffect(() => {
    return () => {
      if (roomId && currentParticipantId) {
        participantService
          .leaveRoom(roomId, currentParticipantId)
          .catch(console.error);
        localStorage.removeItem(`participant_${roomId}`);
      }
    };
  }, [roomId, currentParticipantId]);

  const currentUser = participants.find((p) => p.isHost) || participants[0];

  // Use server-side timer hook
  const {
    minutes,
    seconds,
    status,
    sessionType,
    displaySessionType,
    totalSeconds,
    remainingSeconds,
    isLoading: isTimerLoading,
    timerState,
    startTimer,
    pauseTimer,
    resumeTimer,
    resetTimer,
    updateTimerState,
  } = useServerTimer({
    roomId: roomId || "",
    initialTimerState: room?.timer_state,
    onSessionComplete: (completedSessionType) => {
      if ("Notification" in window && Notification.permission === "granted") {
        new Notification(
          completedSessionType === "work" ? "집중 시간 완료!" : "휴식 종료!",
          {
            body:
              completedSessionType === "work"
                ? "잘하셨습니다! 이제 휴식을 취하세요."
                : "다시 집중할 시간입니다!",
            icon: "/favicon.ico",
          }
        );
      }
      toast.success(
        completedSessionType === "work" ? "집중 시간 완료!" : "휴식 종료!",
        {
          description:
            completedSessionType === "work"
              ? "잘하셨습니다! 이제 휴식을 취하세요."
              : "다시 집중할 시간입니다!",
        }
      );
    },
  });

  // WebSocket connection and synchronization
  useEffect(() => {
    if (!roomId) return;

    let unsubscribe: (() => void) | null = null;

        const connectWebSocket = async () => {
      try {
        await wsClient.connect(roomId);
        toast.success("실시간 동기화가 연결되었습니다");

        // Set up message handler
        unsubscribe = wsClient.onMessage((message) => {
          if (message.event === "timer_update") {
            updateTimerState(message.data);
          } else if (message.event === "participant_update") {
            // Update participants list
            if (message.data.action === "joined" && message.data.participant) {
              const newParticipant: Participant = {
                id: message.data.participant.id,
                name: message.data.participant.name,
                isHost: false, // Will be updated when we reload the list
              };
              setParticipants((prev) => {
                // Check if participant already exists
                if (prev.find((p) => p.id === newParticipant.id)) {
                  return prev;
                }
                return [...prev, newParticipant];
              });
              // Reload to get updated host status
              if (roomId) {
                loadParticipants(roomId);
              }
            } else if (message.data.action === "left") {
              setParticipants((prev) =>
                prev.filter(
                  (p) => p.id !== message.data.participant_id
                )
              );
            }
          } else if (message.event === "timer_complete") {
            const { completed_session_type, next_session_type, auto_start } =
              message.data;

            toast.success(
              completed_session_type === "work"
                ? "집중 시간 완료!"
                : "휴식 종료!",
              {
                description:
                  completed_session_type === "work"
                    ? "잘하셨습니다! 이제 휴식을 취하세요."
                    : "다시 집중할 시간입니다!",
              }
            );

            if (auto_start) {
              setTimeout(() => {
                startTimer(next_session_type);
              }, 3000);
            }
          } else if (message.event === "error") {
            toast.error(message.error.message);
          }
        });

        // Start heartbeat
        const heartbeatInterval = setInterval(() => {
          wsClient.sendPing();
        }, 30000); // Every 30 seconds

        return () => {
          clearInterval(heartbeatInterval);
        };
      } catch (error) {
        console.error("Failed to connect WebSocket:", error);
        toast.error("실시간 동기화 연결에 실패했습니다");
      }
    };

    connectWebSocket();

    return () => {
      if (unsubscribe) {
        unsubscribe();
      }
      wsClient.disconnect();
    };
  }, [roomId, updateTimerState, startTimer, loadParticipants]);

  // Update timer state when room data changes
  useEffect(() => {
    if (room?.timer_state) {
      updateTimerState(room.timer_state);
    }
  }, [room?.timer_state, updateTimerState]);

  const handleUpdateSettings = async (
    newFocusTime: number,
    newBreakTime: number,
    newAutoStart: boolean
  ) => {
    if (!roomId) return;

    try {
      const response = await roomService.updateRoomSettings(roomId, {
        work_duration_minutes: newFocusTime,
        break_duration_minutes: newBreakTime,
        auto_start_break: newAutoStart,
      });

      if (response.status === "success" && response.data) {
        setFocusTime(newFocusTime);
        setBreakTime(newBreakTime);
        setAutoStart(newAutoStart);
        toast.success("설정이 업데이트되었습니다");
      } else {
        toast.error(response.error?.message || "설정 업데이트에 실패했습니다");
      }
    } catch (error) {
      console.error("Failed to update settings:", error);
      toast.error("네트워크 오류가 발생했습니다");
    }
  };

  const handleDeleteRoom = async () => {
    if (!roomId) return;

    try {
      const response = await roomService.deleteRoom(roomId);
      if (response.status === "success") {
        toast.success("방이 삭제되었습니다");
        setTimeout(() => {
          onLeaveRoom();
        }, 1000);
      } else {
        if (response.error?.code === "FORBIDDEN") {
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

  const handleCopyRoomId = async () => {
    if (!roomId) return;
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
  useEffect(() => {
    if ("Notification" in window && Notification.permission === "default") {
      Notification.requestPermission();
    }
  }, []);

  if (isLoading) {
    return <RoomPageSkeleton />;
  }

  if (!room) {
    return null;
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between gap-4 flex-wrap">
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2">
                <h1 className="truncate">{room.room_name}</h1>
                <WebSocketStatus showLabel={false} />
              </div>
              <div className="flex items-center gap-2 mt-1">
                <p className="text-sm text-muted-foreground">방 ID: {room.room_id}</p>
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
                isHost={currentUser?.isHost || false}
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

      {/* WebSocket 연결 상태 알림 */}
      {wsConnecting && (
        <div className="container mx-auto px-4 py-2">
          <div className="bg-muted border border-border rounded-lg p-3 flex items-center gap-2">
            <Loader2 className="w-4 h-4 animate-spin text-muted-foreground" />
            <p className="text-sm text-muted-foreground">실시간 동기화 연결 중...</p>
          </div>
        </div>
      )}

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <div className="grid lg:grid-cols-[1fr_350px] gap-8">
          {/* Timer Section */}
          <div className="flex flex-col items-center justify-center gap-8">
            <TimerDisplay
              minutes={minutes}
              seconds={seconds}
              status={status}
              sessionType={displaySessionType}
              totalSeconds={totalSeconds}
              remainingSeconds={remainingSeconds}
            />
            <TimerControls
              status={status}
              onStart={() => {
                const nextSessionType =
                  sessionType === "work" ? "break" : "work";
                startTimer(nextSessionType);
                // Also send via WebSocket
                wsClient.sendStartTimer(nextSessionType);
              }}
              onPause={() => {
                pauseTimer();
                wsClient.sendPauseTimer();
              }}
              onReset={() => {
                resetTimer();
                wsClient.sendResetTimer();
              }}
            />

            {status === "paused" && (
              <Button
                variant="secondary"
                onClick={() => {
                  resumeTimer();
                  wsClient.sendResumeTimer();
                }}
                className="mt-4"
                disabled={isTimerLoading}
              >
                재개
              </Button>
            )}

            {status === "completed" && (
              <Button
                variant="secondary"
                onClick={() => {
                  const nextSessionType =
                    sessionType === "work" ? "break" : "work";
                  startTimer(nextSessionType);
                  wsClient.sendStartTimer(nextSessionType);
                }}
                className="mt-4"
                disabled={isTimerLoading}
              >
                {sessionType === "work" ? "휴식 시작" : "집중 시작"}
              </Button>
            )}
          </div>

          {/* Participant List */}
          <div className="lg:block hidden">
            <ParticipantList participants={participants} isLoading={isLoadingParticipants} />
          </div>
        </div>

        {/* Mobile Participant List */}
        <div className="lg:hidden mt-8">
          <ParticipantList participants={participants} isLoading={isLoadingParticipants} />
        </div>
      </main>
    </div>
  );
}

export default RoomPage;
