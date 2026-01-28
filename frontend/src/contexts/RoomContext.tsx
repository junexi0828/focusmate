import {
  createContext,
  useContext,
  useState,
  useEffect,
  useRef,
  useCallback,
  ReactNode,
} from "react";
import { toast } from "sonner";
import { SessionType } from "../features/timer/types/timer.types";
import { Participant } from "../features/participants/types/participant.types";
import { Room } from "../features/room/types/room.types";
import { roomService } from "../features/room/services/roomService";
import { participantService } from "../features/participants/services/participantService";
import { wsClient } from "../lib/websocket";
import { useServerTimer } from "../features/timer/hooks/useServerTimer";
import { authService } from "../features/auth/services/authService";
import { RoomChatMessage } from "../types/room-chat";

interface RoomContextType {
  // State
  roomId: string | null;
  room: Room | null;
  isLoading: boolean;
  isLoadingParticipants: boolean;
  participants: Participant[];
  listParticipants: { id: string; name: string; isHost: boolean }[];
  participantCount: number | null;
  currentParticipantId: string | null;
  participantName: string;
  isHost: boolean;
  maxParticipants: number;

  // Timer State (derived from useServerTimer)
  timer: ReturnType<typeof useServerTimer>;

  // Actions
  joinRoom: (roomId: string) => Promise<boolean>;
  leaveRoom: () => Promise<void>;

  // WebSocket Status
  isConnected: boolean;
  isConnecting: boolean;
  connectionError: string | null;
  reconnectAttempts: number;

  // Chat
  chatMessages: RoomChatMessage[];
  addChatMessage: (msg: RoomChatMessage) => void;
  sendChatMessage: (content: string) => void;
}

const RoomContext = createContext<RoomContextType | undefined>(undefined);

export function RoomProvider({ children }: { children: ReactNode }) {
  const [roomId, setRoomId] = useState<string | null>(null);
  const [room, setRoom] = useState<Room | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isLoadingParticipants, setIsLoadingParticipants] = useState(false);

  const [participants, setParticipants] = useState<Participant[]>([]);
  const [listParticipants, setListParticipants] = useState<{ id: string; name: string; isHost: boolean }[]>([]);
  const [participantCount, setParticipantCount] = useState<number | null>(null);
  const [currentParticipantId, setCurrentParticipantId] = useState<string | null>(null);
  const [participantName, setParticipantName] = useState<string>("");
  const [chatMessages, setChatMessages] = useState<RoomChatMessage[]>([]);
  const maxParticipants = room?.max_participants ?? 50;

  // WebSocket State
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  // Toast 중복 방지를 위한 ref
  const lastToastRef = useRef<Record<string, number>>({});

  const notifyOnce = useCallback(
    (key: string, message: string, intervalMs = 8000) => {
      const now = Date.now();
      if (now - (lastToastRef.current[key] || 0) < intervalMs) {
        return;
      }
      lastToastRef.current[key] = now;
      toast.error(message, { duration: 3000 });
    },
    []
  );

  // Timer Hook
  const timer = useServerTimer({
    roomId: roomId || "",
    initialTimerState: room?.timer_state,
    onSessionComplete: async (completedSessionType) => {
      const { notificationService } = await import("../lib/notificationService");
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
          description: completedSessionType === "work"
            ? "잘하셨습니다! 이제 휴식을 취하세요."
            : "다시 집중할 시간입니다!",
        }
      );
      if (completedSessionType === "work") {
        const { CelebrationSystem } = await import("../utils/celebrationSystem");
        CelebrationSystem.celebrate();
      }
    },
  });

  const { status, sessionType, minutes, seconds, updateTimerState } = timer;

  // Global Title Update
  useEffect(() => {
    if (!roomId) {
      if (document.title !== "FocusMate - 함께 집중하는 학습 타이머") {
        document.title = "FocusMate - 함께 집중하는 학습 타이머";
      }
      return;
    }

    if (status === "running" || status === "paused") {
      const mode = sessionType === "work" ? "Focus" : "Break";
      const timeStr = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
      const icon = status === "paused" ? "⏸" : "▶️";
      document.title = `${icon} [${timeStr}] ${mode} | FocusMate`;
    } else if (status === "completed") {
      document.title = "Done! | FocusMate";
    } else {
      document.title = "FocusMate - 함께 집중하는 학습 타이머";
    }

    return () => {
      document.title = "FocusMate - 함께 집중하는 학습 타이머";
    };
  }, [roomId, status, minutes, seconds, sessionType]);

  // Load Room Data with timeout and retry
  const loadRoom = useCallback(async (id: string): Promise<Room | null> => {
    setIsLoading(true);
    const timeoutMs = 12000;
    let timeoutId: ReturnType<typeof setTimeout> | null = null;
    try {
      let response: Awaited<ReturnType<typeof roomService.getRoom>> | null = null;
      for (let attempt = 0; attempt < 3; attempt += 1) {
        response = (await Promise.race([
          roomService.getRoom(id),
          new Promise<never>((_, reject) => {
            timeoutId = setTimeout(() => {
              reject(new Error("ROOM_LOAD_TIMEOUT"));
            }, timeoutMs);
          }),
        ])) as Awaited<ReturnType<typeof roomService.getRoom>>;

        if (response.status === "success") {
          break;
        }
        if (response.error?.code !== "NETWORK_ERROR") {
          break;
        }
        await new Promise((resolve) => setTimeout(resolve, 600 * (attempt + 1)));
      }

      if (response.status === "success" && response.data) {
        const roomData = response.data;
        const normalizedRoom = {
          ...roomData,
          room_id: roomData.room_id ?? roomData.id,
          room_name: roomData.room_name ?? roomData.name,
        };
        setRoom(normalizedRoom);
        if (normalizedRoom.timer_state) {
          updateTimerState(normalizedRoom.timer_state);
        }
        return normalizedRoom;
      } else {
        if (response.error?.code === "ROOM_NOT_FOUND") {
          toast.error("방을 찾을 수 없습니다");
        } else {
          toast.error(response.error?.message || "방 정보를 불러오는데 실패했습니다");
        }
        return null;
      }
    } catch (error) {
      console.error("Failed to load room:", error);
      if (error instanceof Error && error.message === "ROOM_LOAD_TIMEOUT") {
        notifyOnce("room_timeout", "방 정보를 불러오는 데 시간이 오래 걸립니다");
      } else {
        notifyOnce("room_network", "네트워크 오류가 발생했습니다");
      }
      return null;
    } finally {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
      setIsLoading(false);
    }
  }, [updateTimerState, notifyOnce]);

  // Load Participants with retry
  const loadParticipants = useCallback(async (id: string) => {
    setIsLoadingParticipants(true);
    try {
      let response = await participantService.getParticipants(id);
      if (response.status === "error" && response.error?.code === "NETWORK_ERROR") {
        await new Promise((resolve) => setTimeout(resolve, 600));
        response = await participantService.getParticipants(id);
      }

      if (response.status === "success" && response.data) {
        const uiParticipants: Participant[] = response.data.map((p) => ({
          id: p.id || p.participant_id || "",
          participant_id: p.participant_id || p.id,
          room_id: p.room_id,
          username: p.username,
          name: p.name || p.username,
          is_host: p.is_host,
          joined_at: p.joined_at,
          user_id: p.user_id,
          is_connected: p.is_connected,
          left_at: p.left_at,
        }));

        const listFormat = uiParticipants.map((p) => ({
          id: p.id,
          name: p.name || p.username,
          isHost: p.is_host,
        }));
        setParticipants(uiParticipants);
        setListParticipants(listFormat);
        setParticipantCount(uiParticipants.length);
      }
    } catch (error) {
      console.error("Failed to load participants:", error);
    } finally {
      setIsLoadingParticipants(false);
    }
  }, []);

  // WebSocket Connection with StrictMode support
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);
  const mountTimeRef = useRef<number | null>(null);
  const connectionEstablishedRef = useRef(false);
  const cleanupTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const connectionToastShownRef = useRef(false);
  const startTimerRef = useRef(timer.startTimer);
  const updateTimerStateRef = useRef(updateTimerState);
  const loadParticipantsRef = useRef(loadParticipants);

  // Keep refs updated
  useEffect(() => {
    startTimerRef.current = timer.startTimer;
    updateTimerStateRef.current = updateTimerState;
    loadParticipantsRef.current = loadParticipants;
  }, [timer.startTimer, updateTimerState, loadParticipants]);

  const connectWebSocket = useCallback(async (id: string) => {
    let unsubscribe: (() => void) | null = null;
    let isMounted = true;
    const currentMountTime = Date.now();
    mountTimeRef.current = currentMountTime;
    connectionEstablishedRef.current = false;

    // Clear previous cleanup timeout
    if (cleanupTimeoutRef.current) {
      clearTimeout(cleanupTimeoutRef.current);
      cleanupTimeoutRef.current = null;
    }

    try {
      // React StrictMode support: wait for cleanup to complete
      await new Promise((resolve) => setTimeout(resolve, 50));

      if (!isMounted) return;

      // Check if mount time changed (StrictMode double-mount)
      if (mountTimeRef.current !== currentMountTime) {
        console.log(`[RoomContext] Skipping connection - mount time changed (StrictMode)`);
        return;
      }

      setIsConnecting(true);
      setConnectionError(null);

      await wsClient.connect(id);

      // Check mount time again after async operation
      if (mountTimeRef.current !== currentMountTime) {
        if (mountTimeRef.current === null) {
          console.log(`[RoomContext] Connection finished after cleanup - disconnecting`);
          wsClient.disconnect();
        } else {
          console.log(`[RoomContext] Connection finished but superseded - yielding to new mount`);
        }
        return;
      }

      connectionEstablishedRef.current = true;
      setIsConnected(true);

      // Show connection success toast once
      if (!connectionToastShownRef.current) {
        connectionToastShownRef.current = true;
        toast.success("실시간 동기화가 연결되었습니다", { duration: 3000 });
      }

      // Set up message handler
      unsubscribe = wsClient.onMessage((message) => {
        if (message.event === "timer_update") {
          updateTimerStateRef.current(message.data);
        } else if (message.event === "participant_update") {
          if (message.data.action === "joined" && message.data.participant) {
            const p = message.data.participant;
            const newP: Participant = {
              id: p.id || "",
              participant_id: p.id,
              room_id: id,
              username: p.username || p.name || "",
              name: p.name || p.username || "",
              is_host: false,
              joined_at: new Date().toISOString(),
            };
            setParticipants((prev) => {
              if (prev.find((x) => x.id === newP.id)) return prev;
              return [...prev, newP];
            });
            setListParticipants((prev) => {
              if (prev.find((x) => x.id === newP.id)) return prev;
              return [...prev, { id: newP.id, name: newP.name, isHost: false }];
            });
          } else if (message.data.action === "left") {
            setParticipants((prev) => prev.filter((p) => p.id !== message.data.participant_id));
            setListParticipants((prev) => prev.filter((p) => p.id !== message.data.participant_id));
          }
          if (typeof message.data.current_count === "number") {
            setParticipantCount(message.data.current_count);
          }
        } else if (message.event === "timer_complete") {
          const { completed_session_type, next_session_type, auto_start } = message.data;
          toast.success(
            completed_session_type === "work" ? "집중 시간 완료!" : "휴식 종료!",
            {
              description:
                completed_session_type === "work"
                  ? "잘하셨습니다! 이제 휴식을 취하세요."
                  : "다시 집중할 시간입니다!",
            }
          );
          if (auto_start) {
            setTimeout(() => {
              startTimerRef.current(next_session_type);
            }, 3000);
          }
        } else if (message.event === "chat_backfill") {
          if (message.data?.messages?.length) {
            setChatMessages(message.data.messages);
          }
        } else if (message.event === "chat_message") {
          const incoming = message.data?.message;
          if (incoming) {
            setChatMessages((prev) => {
              if (prev.some((m) => m.id === incoming.id)) return prev;
              return [...prev, incoming];
            });
          }
        } else if (message.event === "error") {
          toast.error(message.error.message);
        }
      });

      // Start heartbeat
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
      }
      heartbeatIntervalRef.current = setInterval(() => {
        if (wsClient.currentRoomId === id && isMounted) {
          wsClient.sendPing();
        } else {
          if (heartbeatIntervalRef.current) {
            clearInterval(heartbeatIntervalRef.current);
            heartbeatIntervalRef.current = null;
          }
        }
      }, 30000);
    } catch (err: any) {
      console.error("Failed to connect WebSocket:", err);
      setConnectionError(err.message || "Failed to connect");
      setIsConnected(false);
      toast.error("실시간 동기화 연결에 실패했습니다");
    } finally {
      setIsConnecting(false);
    }

    // Return cleanup function
    return () => {
      isMounted = false;

      // Clear previous cleanup timeout
      if (cleanupTimeoutRef.current) {
        clearTimeout(cleanupTimeoutRef.current);
        cleanupTimeoutRef.current = null;
      }

      // React StrictMode: ignore cleanup within 300ms if connection not established
      const timeSinceMount = mountTimeRef.current ? Date.now() - mountTimeRef.current : Infinity;

      if (timeSinceMount < 300 && !connectionEstablishedRef.current) {
        console.log(`[RoomContext] Skipping cleanup - StrictMode double-mount detected (${timeSinceMount}ms)`);
        if (unsubscribe) {
          unsubscribe();
        }
        mountTimeRef.current = null;
        connectionEstablishedRef.current = false;
        return;
      }

      // Clear heartbeat immediately
      if (heartbeatIntervalRef.current) {
        clearInterval(heartbeatIntervalRef.current);
        heartbeatIntervalRef.current = null;
      }

      if (unsubscribe) {
        unsubscribe();
      }

      // Wait for cleanup to complete before disconnect
      cleanupTimeoutRef.current = setTimeout(() => {
        const shouldDisconnect =
          wsClient.currentRoomId === id &&
          connectionEstablishedRef.current &&
          mountTimeRef.current === currentMountTime;

        if (shouldDisconnect) {
          console.log(`[RoomContext] Cleanup: Disconnecting from room ${id}`);
          wsClient.disconnect();
        } else {
          console.log(`[RoomContext] Cleanup: Skipping disconnect (roomId mismatch or not connected)`);
        }

        mountTimeRef.current = null;
        connectionEstablishedRef.current = false;
        cleanupTimeoutRef.current = null;
      }, 200);
    };
  }, []);

  // Join Room Action
  const joinRoom = useCallback(async (id: string) => {
    // If already in a different room, leave it first
    if (roomId && roomId !== id) {
      console.log(`[RoomContext] Switching from room ${roomId} to ${id}`);
      await leaveRoom();
    }

    // 1. Fetch Room Info
    const roomData = await loadRoom(id);
    if (!roomData) return false;

    // 2. Set ID (starts global state)
    setRoomId(id);

    // 3. Join as Participant
    const user = authService.getCurrentUser();
    const userId = user?.id || null;
    const storedPid = localStorage.getItem(`participant_${id}`);

    // If stored participant ID exists, rejoin
    if (storedPid) {
      try {
        let name = localStorage.getItem("participant_name") || "";
        if (!name && user) {
          name = user.username || user.email?.split("@")[0] || "";
          localStorage.setItem("participant_name", name);
        }

        let response = await participantService.joinRoom(id, {
          username: name || "사용자",
          user_id: userId,
          participant_id: storedPid,
        });

        if (response.status === "error" && response.error?.code === "NETWORK_ERROR") {
          await new Promise((resolve) => setTimeout(resolve, 600));
          response = await participantService.joinRoom(id, {
            username: name || "사용자",
            user_id: userId,
            participant_id: storedPid,
          });
        }

        if (response.status === "success" && response.data) {
          const data = response.data;
          setCurrentParticipantId(data.id || data.participant_id || storedPid);
          setParticipantName(data.username || data.name || name);
          await loadParticipants(id);
          const cleanup = await connectWebSocket(id);
          return true;
        } else {
          // Fallback to stored participant ID
          setCurrentParticipantId(storedPid);
        }
      } catch (error) {
        console.error("Failed to rejoin room:", error);
        setCurrentParticipantId(storedPid);
      }
      const cleanup = await connectWebSocket(id);
      return true;
    }

    // New participant: get name
    let name = localStorage.getItem("participant_name") || "";
    if (!name) {
      if (user) {
        name = user.username || user.email?.split("@")[0] || "";
      }

      // If still no name, prompt for it
      if (!name) {
        const input = prompt("참여자 이름을 입력해주세요:");
        if (!input || input.trim().length === 0) {
          toast.error("이름을 입력해야 방에 참여할 수 있습니다");
          setRoomId(null);
          return false;
        }
        name = input.trim();
      }

      localStorage.setItem("participant_name", name);
    }

    try {
      let response = await participantService.joinRoom(id, {
        username: name,
        user_id: userId,
        participant_id: storedPid,
      });

      if (response.status === "error" && response.error?.code === "NETWORK_ERROR") {
        await new Promise((resolve) => setTimeout(resolve, 600));
        response = await participantService.joinRoom(id, {
          username: name,
          user_id: userId,
          participant_id: storedPid,
        });
      }

      if (response.status === "success" && response.data) {
        const participantId = response.data.id || response.data.participant_id || "";
        setCurrentParticipantId(participantId);
        localStorage.setItem(`participant_${id}`, participantId);
        setParticipantName(response.data.username || response.data.name || "");
        await loadParticipants(id);
        const cleanup = await connectWebSocket(id);
        toast.success("방에 참여했습니다!");
        return true;
      } else {
        if (response.error?.code === "CONFLICT") {
          toast.error("방이 가득 찼습니다");
        } else {
          toast.error(response.error?.message || "방 참여에 실패했습니다");
        }
        setRoomId(null);
        return false;
      }
    } catch (error) {
      console.error("Failed to join room:", error);
      toast.error("네트워크 오류가 발생했습니다");
      setRoomId(null);
      return false;
    }
  }, [roomId, loadRoom, loadParticipants, connectWebSocket]);

  // Send Chat Message with validation
  const sendChatMessage = useCallback((content: string) => {
    const trimmed = content.trim();
    if (!trimmed) return;

    const CHAT_MAX_LENGTH = 300;
    if (trimmed.length > CHAT_MAX_LENGTH) {
      toast.error(`채팅은 ${CHAT_MAX_LENGTH}자까지 보낼 수 있습니다.`);
      return;
    }

    if (!wsClient.isConnected()) {
      toast.error("실시간 연결이 끊겨 채팅을 보낼 수 없습니다.");
      return;
    }

    wsClient.sendChatMessage(trimmed);
  }, []);

  // Leave Room Action
  const leaveRoom = useCallback(async () => {
    if (!roomId) return;

    // API Call
    if (currentParticipantId) {
      try {
        await participantService.leaveRoom(roomId, currentParticipantId);
        console.log("Successfully left room");
      } catch (e) {
        console.error("Failed to leave room:", e);
      }
    }

    // Disconnect WS
    wsClient.disconnect();
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = null;
    }
    if (cleanupTimeoutRef.current) {
      clearTimeout(cleanupTimeoutRef.current);
      cleanupTimeoutRef.current = null;
    }

    // Reset State
    localStorage.removeItem(`participant_${roomId}`);
    setRoomId(null);
    setRoom(null);
    setParticipants([]);
    setListParticipants([]);
    setParticipantCount(null);
    setCurrentParticipantId(null);
    setIsConnected(false);
    setIsConnecting(false);
    setConnectionError(null);
    setReconnectAttempts(0);
    setChatMessages([]);
    connectionToastShownRef.current = false;

    document.title = "FocusMate - 함께 집중하는 학습 타이머";
  }, [roomId, currentParticipantId]);

  const addChatMessage = useCallback((msg: RoomChatMessage) => {
    setChatMessages((prev) => {
      if (prev.some((m) => m.id === msg.id)) return prev;
      return [...prev, msg];
    });
  }, []);

  // WebSocket error notification
  useEffect(() => {
    if (connectionError) {
      notifyOnce("ws_error", connectionError);
    }
  }, [connectionError, notifyOnce]);

  // Fallback polling when WebSocket is disconnected
  const participantSyncTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (!roomId || isConnected) {
      return;
    }
    const intervalId = setInterval(() => {
      void loadParticipants(roomId);
    }, 30000);
    return () => clearInterval(intervalId);
  }, [loadParticipants, roomId, isConnected]);

  // Participant sync when count mismatch
  useEffect(() => {
    if (!roomId || participantCount === null) {
      return;
    }

    if (participantCount === listParticipants.length) {
      return;
    }

    if (participantSyncTimeoutRef.current) {
      return;
    }

    participantSyncTimeoutRef.current = setTimeout(() => {
      participantSyncTimeoutRef.current = null;
      loadParticipants(roomId);
    }, 300);

    return () => {
      if (participantSyncTimeoutRef.current) {
        clearTimeout(participantSyncTimeoutRef.current);
        participantSyncTimeoutRef.current = null;
      }
    };
  }, [participantCount, listParticipants.length, loadParticipants, roomId]);

  // Request notification permission on mount
  useEffect(() => {
    import("../lib/notificationService").then(({ notificationService }) => {
      if (notificationService.isSupported() && notificationService.getPermission() === "default") {
        notificationService.requestPermission().catch(console.error);
      }
    });
  }, []);

  // Host check logic
  const currentAuthUser = authService.getCurrentUser();
  const isCurrentUserHostByRoom =
    room?.host_id && currentAuthUser?.id && room.host_id === currentAuthUser.id;
  const currentUser =
    participants.find((p) => p.user_id === currentAuthUser?.id && p.is_host) ||
    participants.find((p) => p.is_host) ||
    participants[0];
  const isCurrentUserHostByParticipant =
    currentUser?.user_id === currentAuthUser?.id && currentUser?.is_host;
  const isHost = isCurrentUserHostByRoom ?? isCurrentUserHostByParticipant;

  return (
    <RoomContext.Provider
      value={{
        roomId,
        room,
        isLoading,
        isLoadingParticipants,
        participants,
        listParticipants,
        participantCount,
        currentParticipantId,
        participantName,
        isHost: isHost || false,
        maxParticipants,
        timer,
        joinRoom,
        leaveRoom,
        isConnected,
        isConnecting,
        connectionError,
        reconnectAttempts,
        chatMessages,
        addChatMessage,
        sendChatMessage,
      }}
    >
      {children}
    </RoomContext.Provider>
  );
}

export function useRoomContext() {
  const context = useContext(RoomContext);
  if (context === undefined) {
    throw new Error("useRoomContext must be used within a RoomProvider");
  }
  return context;
}
