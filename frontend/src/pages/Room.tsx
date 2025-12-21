import React, { useState, useEffect, useRef } from "react";
import { useParams } from "@tanstack/react-router";
import { Button } from "../components/ui/button";
import { TimerDisplay } from "../features/timer/components/TimerDisplay";
import { TimerControls } from "../features/timer/components/TimerControls";
import {
  ParticipantList,
  Participant,
} from "../features/participants/components/ParticipantListOriginal";
import { RoomSettingsDialog } from "../features/room/components/RoomSettingsDialog";
import { useServerTimer } from "../features/timer/hooks/useServerTimer";
import { timerService } from "../features/timer/services/timerService";
import { LogOut, Copy, Check, Loader2, Trash2 } from "lucide-react";
import { toast } from "sonner";
import { roomService } from "../features/room/services/roomService";
import { Room } from "../features/room/types/room.types";
import { LoadingSpinner } from "../components/ui/loading";
import { wsClient } from "../lib/websocket";
import { participantService } from "../features/participants/services/participantService";
import { Participant as ParticipantType } from "../features/participants/types/participant.types";
import { RoomPageSkeleton } from "../components/ui/room-skeleton";
import {
  WebSocketStatus,
  useWebSocketStatus,
} from "../components/WebSocketStatus";
import { WebSocketConnectionBanner } from "../components/WebSocketConnectionBanner";
import { authService } from "../features/auth/services/authService";

interface RoomPageProps {
  onLeaveRoom: () => void;
}

export function RoomPage({ onLeaveRoom }: RoomPageProps) {
  const { roomId } = useParams({ from: "/room/$roomId" });
  const [room, setRoom] = useState<Room | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [focusTime, setFocusTime] = useState(25);
  const [breakTime, setBreakTime] = useState(5);
  const [autoStart, setAutoStart] = useState(false);
  const [removeOnLeave, setRemoveOnLeave] = useState(false);
  const [copied, setCopied] = useState(false);

  const [participants, setParticipants] = useState<Participant[]>([]);
  const [listParticipants, setListParticipants] = useState<
    { id: string; name: string; isHost: boolean }[]
  >([]);
  const [isLoadingParticipants, setIsLoadingParticipants] = useState(false);
  const [currentParticipantId, setCurrentParticipantId] = useState<
    string | null
  >(null);
  const [participantName, setParticipantName] = useState<string>("");

  // WebSocket 연결 상태
  const {
    isConnected: wsConnected,
    isConnecting: wsConnecting,
    connectionError: wsError,
    reconnectAttempts,
  } = useWebSocketStatus(roomId || null);

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
      onLeaveRoom();
      return;
    }

    const loadRoom = async () => {
      setIsLoading(true);
      try {
        const response = await roomService.getRoom(roomId);
        if (response.status === "success" && response.data) {
          const roomData = response.data;
          setRoom(roomData);
          // Backend now stores work_duration and break_duration in minutes
          setFocusTime(roomData.work_duration); // Already in minutes
          setBreakTime(roomData.break_duration); // Already in minutes
          setAutoStart(roomData.auto_start_break ?? false);
          setRemoveOnLeave(roomData.remove_on_leave ?? false);

          // Load participants from API
          await loadParticipants(roomId);

          // Join room if not already joined
          await joinRoomIfNeeded(roomId);
        } else {
          if (response.error?.code === "ROOM_NOT_FOUND") {
            toast.error("방을 찾을 수 없습니다");
          } else {
            toast.error(
              response.error?.message || "방 정보를 불러오는데 실패했습니다"
            );
          }
          onLeaveRoom();
        }
      } catch (error) {
        console.error("Failed to load room:", error);
        toast.error("네트워크 오류가 발생했습니다");
        onLeaveRoom();
      } finally {
        setIsLoading(false);
      }
    };

    loadRoom();
  }, [roomId, onLeaveRoom]);

  // Load participants
  const loadParticipants = async (roomId: string) => {
    setIsLoadingParticipants(true);
    try {
      const response = await participantService.getParticipants(roomId);
      if (response.status === "success" && response.data) {
        // Convert API participant format to UI format
        const uiParticipants: Participant[] = response.data.map((p) => ({
          id: p.id || p.participant_id || "",
          participant_id: p.participant_id || p.id,
          room_id: p.room_id,
          username: p.username,
          name: p.name || p.username, // Use username as name if name not available
          is_host: p.is_host,
          joined_at: p.joined_at,
          user_id: p.user_id,
          is_connected: p.is_connected,
          left_at: p.left_at,
        }));

        // Also convert to ParticipantList format (which uses isHost instead of is_host)
        const listFormat = uiParticipants.map((p) => ({
          id: p.id,
          name: p.name || p.username,
          isHost: p.is_host,
        }));
        setParticipants(uiParticipants);
        setListParticipants(listFormat);
      }
    } catch (error) {
      console.error("Failed to load participants:", error);
    } finally {
      setIsLoadingParticipants(false);
    }
  };

  // Join room if needed
  const joinRoomIfNeeded = async (roomId: string) => {
    // Get user info from auth service first
    const user = authService.getCurrentUser();
    const userId = user?.id || null;

    // Check if user already has a participant ID in localStorage
    const storedParticipantId = localStorage.getItem(`participant_${roomId}`);
    if (storedParticipantId) {
      // Even if we have a stored participant ID, we should verify/update user info
      // Rejoin to ensure user info is up-to-date
      try {
        // Get participant name from user info
        let name = localStorage.getItem("participant_name") || "";
        if (!name && user) {
          name = user.username || user.email?.split("@")[0] || "";
          localStorage.setItem("participant_name", name);
        }

        // Rejoin to update user info
        const response = await participantService.joinRoom(roomId, {
          username: name || "사용자",
          user_id: userId,
        });
        if (response.status === "success" && response.data) {
          setCurrentParticipantId(
            response.data.id ||
              response.data.participant_id ||
              storedParticipantId
          );
          setParticipantName(
            response.data.username || response.data.name || name
          );
          // Reload participants list to show updated name
          await loadParticipants(roomId);
        }
      } catch (error) {
        console.error("Failed to rejoin room:", error);
        // Fall back to stored participant ID
        setCurrentParticipantId(storedParticipantId);
      }
      return;
    }

    // User info already retrieved above

    // Get participant name from localStorage, user info, or prompt
    let name = localStorage.getItem("participant_name") || "";
    if (!name) {
      // Try to get from user info first
      if (user) {
        name = user.username || user.email?.split("@")[0] || "";
      }

      // If still no name, prompt for it
      if (!name) {
        const input = prompt("참여자 이름을 입력해주세요:");
        if (!input || input.trim().length === 0) {
          toast.error("이름을 입력해야 방에 참여할 수 있습니다");
          onLeaveRoom();
          return;
        }
        name = input.trim();
      }

      localStorage.setItem("participant_name", name);
    }

    try {
      const response = await participantService.joinRoom(roomId, {
        username: name, // Backend expects 'username', not 'participant_name'
        user_id: userId, // Pass user_id if authenticated
      });
      if (response.status === "success" && response.data) {
        const participantId =
          response.data.id || response.data.participant_id || "";
        setCurrentParticipantId(participantId);
        localStorage.setItem(`participant_${roomId}`, participantId);
        setParticipantName(response.data.username || response.data.name || "");
        // Reload participants list
        await loadParticipants(roomId);
        toast.success("방에 참여했습니다!");
      } else {
        toast.error(response.error?.message || "방 참여에 실패했습니다");
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
        // Leave room API call
        participantService
          .leaveRoom(roomId, currentParticipantId)
          .then(() => {
            console.log("Successfully left room");
          })
          .catch((error) => {
            console.error("Failed to leave room:", error);
          });

        // Clean up localStorage
        localStorage.removeItem(`participant_${roomId}`);

        // Disconnect WebSocket
        wsClient.disconnect();
      }
    };
  }, [roomId, currentParticipantId]);

  // Check if current user is host
  const currentAuthUser = authService.getCurrentUser();
  // First check room.host_id (most reliable)
  const isCurrentUserHostByRoom =
    room?.host_id && currentAuthUser?.id && room.host_id === currentAuthUser.id;
  // Fallback to participant is_host check
  const currentUser =
    participants.find((p) => p.user_id === currentAuthUser?.id && p.is_host) ||
    participants.find((p) => p.is_host) ||
    participants[0];
  const isCurrentUserHostByParticipant =
    currentUser?.user_id === currentAuthUser?.id && currentUser?.is_host;
  // Use room.host_id if available, otherwise fallback to participant check
  const isCurrentUserHost = isCurrentUserHostByRoom ?? isCurrentUserHostByParticipant;

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
    onSessionComplete: async (completedSessionType) => {
      // Show notification using notification service
      const { notificationService } =
        await import("../lib/notificationService");
      notificationService.notify(
        completedSessionType === "work" ? "집중 시간 완료!" : "휴식 종료!",
        completedSessionType === "work"
          ? "잘하셨습니다! 이제 휴식을 취하세요."
          : "다시 집중할 시간입니다!",
        "/favicon.ico"
      );

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
  const mountTimeRef = useRef<number | null>(null);
  const connectionEstablishedRef = useRef(false);
  const cleanupTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const connectionToastShownRef = useRef(false); // 연결 성공 토스트 한 번만 표시

  useEffect(() => {
    if (!roomId) return;

    let unsubscribe: (() => void) | null = null;
    let isMounted = true; // React StrictMode 대응
    const currentMountTime = Date.now();
    mountTimeRef.current = currentMountTime;
    connectionEstablishedRef.current = false;
    // connectionToastShownRef는 컴포넌트 레벨에서 한 번만 초기화되므로 여기서 초기화하지 않음

    // 이전 cleanup timeout 정리
    if (cleanupTimeoutRef.current) {
      clearTimeout(cleanupTimeoutRef.current);
      cleanupTimeoutRef.current = null;
    }

    const connectWebSocket = async () => {
      try {
        // React StrictMode 대응: cleanup이 완료될 때까지 짧은 대기
        await new Promise((resolve) => setTimeout(resolve, 50));

        if (!isMounted) return; // 컴포넌트가 언마운트되었으면 연결하지 않음

        // 마운트 시간이 변경되었으면 StrictMode 이중 마운트로 간주
        if (mountTimeRef.current !== currentMountTime) {
          console.log(
            `[Room] Skipping connection - mount time changed (StrictMode)`
          );
          return;
        }

        await wsClient.connect(roomId);

        if (!isMounted) {
          // 연결 후 언마운트되었으면 즉시 disconnect
          wsClient.disconnect();
          return;
        }

        // 마운트 시간이 변경되었으면 연결 취소
        if (mountTimeRef.current !== currentMountTime) {
          console.log(
            `[Room] Canceling connection - mount time changed during connection`
          );
          wsClient.disconnect();
          return;
        }

        connectionEstablishedRef.current = true; // 연결 성공 표시

        // 연결 성공 토스트를 한 번만 표시
        if (!connectionToastShownRef.current) {
          connectionToastShownRef.current = true;
          toast.success("실시간 동기화가 연결되었습니다", {
            duration: 3000,
          });
        }

        // Set up message handler
        unsubscribe = wsClient.onMessage((message) => {
          if (message.event === "timer_update") {
            updateTimerState(message.data);
          } else if (message.event === "participant_update") {
            // Update participants list
            if (message.data.action === "joined" && message.data.participant) {
              const newParticipant: Participant = {
                id: message.data.participant.id || "",
                participant_id: message.data.participant.id,
                room_id: roomId || "",
                username:
                  message.data.participant.username ||
                  message.data.participant.name ||
                  "",
                name:
                  message.data.participant.name ||
                  message.data.participant.username ||
                  "",
                is_host: false,
                joined_at: new Date().toISOString(),
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
                prev.filter((p) => p.id !== message.data.participant_id)
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
        // Clear any existing heartbeat interval
        if (heartbeatIntervalRef.current) {
          clearInterval(heartbeatIntervalRef.current);
        }
        heartbeatIntervalRef.current = setInterval(() => {
          if (wsClient.currentRoomId === roomId && isMounted) {
            wsClient.sendPing();
          } else {
            // Stop heartbeat if room changed or component unmounted
            if (heartbeatIntervalRef.current) {
              clearInterval(heartbeatIntervalRef.current);
              heartbeatIntervalRef.current = null;
            }
          }
        }, 30000); // Every 30 seconds
      } catch (error) {
        console.error("Failed to connect WebSocket:", error);
        toast.error("실시간 동기화 연결에 실패했습니다");
      }
    };

    connectWebSocket();

    return () => {
      isMounted = false; // 컴포넌트 언마운트 플래그 설정

      // 이전 cleanup timeout 정리
      if (cleanupTimeoutRef.current) {
        clearTimeout(cleanupTimeoutRef.current);
        cleanupTimeoutRef.current = null;
      }

      // React StrictMode 대응: 마운트 후 짧은 시간 내 cleanup은 무시
      const timeSinceMount = mountTimeRef.current
        ? Date.now() - mountTimeRef.current
        : Infinity;

      // StrictMode 이중 마운트 감지: 300ms 이내이고 연결이 성공하지 않았으면 무시
      if (timeSinceMount < 300 && !connectionEstablishedRef.current) {
        console.log(
          `[Room] Skipping cleanup - React StrictMode double-mount detected (${timeSinceMount}ms)`
        );
        if (unsubscribe) {
          unsubscribe();
        }
        // 마운트 시간 리셋 (다음 마운트를 위해)
        mountTimeRef.current = null;
        connectionEstablishedRef.current = false;
        return;
      }

      // Clear heartbeat interval immediately
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }

      if (unsubscribe) {
        unsubscribe();
      }

      // cleanup이 완료될 때까지 대기 후 disconnect
      // React StrictMode에서 cleanup이 너무 빨리 일어나는 것을 방지
      cleanupTimeoutRef.current = setTimeout(() => {
        // roomId가 변경되지 않았고, 실제로 연결이 성공했을 때만 disconnect
        const shouldDisconnect =
          wsClient.currentRoomId === roomId &&
          connectionEstablishedRef.current &&
          mountTimeRef.current === currentMountTime;

        if (shouldDisconnect) {
          console.log(`[Room] Cleanup: Disconnecting from room ${roomId}`);
          wsClient.disconnect();
        } else {
          console.log(
            `[Room] Cleanup: Skipping disconnect (roomId mismatch or not connected)`
          );
        }

        // 리셋
        mountTimeRef.current = null;
        connectionEstablishedRef.current = false;
        cleanupTimeoutRef.current = null;
      }, 200); // 200ms 대기로 증가
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
    newAutoStart: boolean,
    newRemoveOnLeave: boolean
  ) => {
    if (!roomId) return;

    try {
      const response = await roomService.updateRoomSettings(roomId, {
        work_duration: newFocusTime * 60, // 분을 초로 변환
        break_duration: newBreakTime * 60, // 분을 초로 변환
        auto_start_break: newAutoStart,
        remove_on_leave: newRemoveOnLeave,
      });

      if (response.status === "success" && response.data) {
        setFocusTime(newFocusTime);
        setBreakTime(newBreakTime);
        setAutoStart(newAutoStart);
        setRemoveOnLeave(newRemoveOnLeave);

        // Reload timer state to reflect duration changes
        if (roomId) {
          try {
            const timerResponse = await timerService.getTimer(roomId);
            if (timerResponse.status === "success" && timerResponse.data) {
              updateTimerState(timerResponse.data);
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

  // Request notification permission on mount (using notification service)
  useEffect(() => {
    import("../lib/notificationService").then(({ notificationService }) => {
      if (
        notificationService.isSupported() &&
        notificationService.getPermission() === "default"
      ) {
        notificationService.requestPermission().catch(console.error);
      }
    });
  }, []);

  if (isLoading) {
    return <RoomPageSkeleton />;
  }

  if (!room) {
    return null;
  }

  return (
    <div className="min-h-full bg-background">
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
                <p className="text-sm text-muted-foreground">
                  방 ID: {room.room_id}
                </p>
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
                isHost={isCurrentUserHost || false}
                focusTime={focusTime}
                breakTime={breakTime}
                autoStart={autoStart}
                removeOnLeave={removeOnLeave}
                onUpdateSettings={handleUpdateSettings}
                onDeleteRoom={handleDeleteRoom}
              />
              {isCurrentUserHost && (
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={handleDeleteRoom}
                  className="hidden sm:flex"
                >
                  <Trash2 className="w-4 h-4 mr-2" />방 삭제
                </Button>
              )}
              <Button variant="outline" onClick={onLeaveRoom}>
                <LogOut className="w-4 h-4 mr-2" />
                나가기
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* WebSocket 연결 상태 배너 */}
      <div className="container mx-auto px-4 py-2">
        <WebSocketConnectionBanner
          isConnected={wsConnected}
          isConnecting={wsConnecting}
          connectionError={wsError}
          reconnectAttempts={reconnectAttempts}
          maxReconnectAttempts={wsClient.getMaxReconnectAttempts()}
          onReconnect={() => {
            if (roomId) {
              wsClient.connect(roomId).catch((error) => {
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
                // RUNNING 상태에서는 시작하지 않음
                if (status === "running") {
                  toast.error("타이머가 이미 실행 중입니다");
                  return;
                }
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
            <ParticipantList
              participants={participants}
              isLoading={isLoadingParticipants}
            />
          </div>
        </div>

        {/* Mobile Participant List */}
        <div className="lg:hidden mt-8">
          <ParticipantList
            participants={participants}
            isLoading={isLoadingParticipants}
          />
        </div>
      </main>
    </div>
  );
}

export default RoomPage;
