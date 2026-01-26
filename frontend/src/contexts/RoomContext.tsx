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
  participants: Participant[];
  listParticipants: { id: string; name: string; isHost: boolean }[];
  participantCount: number | null;
  currentParticipantId: string | null;
  participantName: string;
  isHost: boolean;

  // Timer State (derived from useServerTimer)
  timer: {
    minutes: number;
    seconds: number;
    status: "idle" | "running" | "paused" | "completed";
    sessionType: SessionType;
    displaySessionType: "focus" | "break";
    totalSeconds: number;
    remainingSeconds: number;
    isLoading: boolean;
    startTimer: (type?: SessionType) => Promise<void>;
    pauseTimer: () => Promise<void>;
    resumeTimer: () => Promise<void>;
    resetTimer: () => Promise<void>;
    completeSession: () => Promise<any>;
  };

  // Actions
  joinRoom: (roomId: string) => Promise<boolean>;
  leaveRoom: () => Promise<void>;

  // WebSocket Status
  isConnected: boolean;
  isConnecting: boolean;
  connectionError: string | null;

  // Chat
  chatMessages: RoomChatMessage[];
  addChatMessage: (msg: RoomChatMessage) => void;
}

const RoomContext = createContext<RoomContextType | undefined>(undefined);

export function RoomProvider({ children }: { children: ReactNode }) {
  const [roomId, setRoomId] = useState<string | null>(null);
  const [room, setRoom] = useState<Room | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const [participants, setParticipants] = useState<Participant[]>([]);
  const [listParticipants, setListParticipants] = useState<{ id: string; name: string; isHost: boolean }[]>([]);
  const [participantCount, setParticipantCount] = useState<number | null>(null);
  const [currentParticipantId, setCurrentParticipantId] = useState<string | null>(null);
  const [participantName, setParticipantName] = useState<string>("");
  const [chatMessages, setChatMessages] = useState<RoomChatMessage[]>([]);

  // WebSocket State
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

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
       // Cleanup only if we are unmounting the entire app, but here we just let it be
       // unless roomId becomes null
    };
  }, [roomId, status, minutes, seconds, sessionType]);

  // Load Room Data
  const loadRoom = useCallback(async (id: string): Promise<Room | null> => {
    setIsLoading(true);
    try {
      const response = await roomService.getRoom(id);
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
        toast.error(response.error?.message || "방 정보를 불러오는데 실패했습니다");
        return null;
      }
    } catch (error) {
      console.error("Failed to load room:", error);
      toast.error("네트워크 오류가 발생했습니다");
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [updateTimerState]);

  // Load Participants
  const loadParticipants = useCallback(async (id: string) => {
    try {
      const response = await participantService.getParticipants(id);
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
    }
  }, []);

  // WebSocket Connection
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | null>(null);

  const connectWebSocket = useCallback(async (id: string) => {
    if (isConnected || isConnecting) return;

    setIsConnecting(true);
    setConnectionError(null);

    try {
       await wsClient.connect(id);
       setIsConnected(true);

       wsClient.onMessage((message) => {
         if (message.event === "timer_update") {
           updateTimerState(message.data);
         } else if (message.event === "participant_update") {
           // Simplify: just reload participants for correctness or handle delta
           // For now, let's reuse the delta logic roughly or just reload to be safe and simple globally
           // But delta is better for UI flicker. Let's use the delta logic from Room.tsx
           if (message.data.action === "joined" && message.data.participant) {
              const p = message.data.participant;
              const newP: Participant = {
                  id: p.id || "",
                  participant_id: p.id,
                  room_id: id,
                  username: p.name || "",
                  name: p.name || "",
                  is_host: false,
                  joined_at: new Date().toISOString(),
              };
              setParticipants(prev => {
                  if (prev.find(x => x.id === newP.id)) return prev;
                  return [...prev, newP];
              });
              setListParticipants(prev => {
                  if (prev.find(x => x.id === newP.id)) return prev;
                  return [...prev, { id: newP.id, name: newP.name || "", isHost: false }];
              });
           } else if (message.data.action === "left") {
              setParticipants(prev => prev.filter(p => p.id !== message.data.participant_id));
              setListParticipants(prev => prev.filter(p => p.id !== message.data.participant_id));
           }
           if (typeof message.data.current_count === "number") {
             setParticipantCount(message.data.current_count);
           }
         } else if (message.event === "timer_complete") {
             const { completed_session_type, next_session_type, auto_start } = message.data;
             toast.success(completed_session_type === "work" ? "집중 시간 완료!" : "휴식 종료!");
             if (auto_start) {
                 setTimeout(() => timer.startTimer(next_session_type), 3000);
             }
         } else if (message.event === "chat_backfill") {
            if (message.data?.messages?.length) {
              setChatMessages(message.data.messages);
            }
         } else if (message.event === "chat_message") {
            const incoming = message.data?.message;
            if (incoming) {
              setChatMessages(prev => {
                if (prev.some(m => m.id === incoming.id)) return prev;
                return [...prev, incoming];
              });
            }
         } else if (message.event === "error") {
            toast.error(message.error.message);
         }
       });

       // Heartbeat
       if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);
       heartbeatIntervalRef.current = setInterval(() => {
           if (wsClient.currentRoomId === id) {
             wsClient.sendPing();
           }
       }, 30000);

    } catch (err: any) {
        setConnectionError(err.message || "Failed to connect");
        setIsConnected(false);
    } finally {
        setIsConnecting(false);
    }
  }, [isConnected, isConnecting, updateTimerState, timer]);

  // Join Room Action
  const joinRoom = useCallback(async (id: string) => {
    // 1. Fetch Room Info
    const roomData = await loadRoom(id);
    if (!roomData) return false;

    // 2. Set ID (starts global state)
    setRoomId(id);

    // 3. Join as Participant
    const user = authService.getCurrentUser();
    let name = localStorage.getItem("participant_name") || "";
    if (user) name = user.username || user.email?.split("@")[0] || name;

    // Auto-prompt logic would be here, but for global context we assume name handles in UI?
    // Let's assume name is available or we use a default.
    // Ideally UI should prompt BEFORE calling joinRoom if needed.
    // For now we use "Guest" if missing, or let UI handle it.
    if (!name) name = "Guest";

    try {
        const storedPid = localStorage.getItem(`participant_${id}`);
        const response = await participantService.joinRoom(id, {
            username: name,
            user_id: user?.id,
            participant_id: storedPid
        });

        if (response.status === "success" && response.data) {
            const data = response.data;
            const pid = data.id || data.participant_id || "";
            setCurrentParticipantId(pid);
            setParticipantName(data.username || data.name || "");
            localStorage.setItem(`participant_${id}`, pid);
            localStorage.setItem("participant_name", data.username || data.name || "");

            // 4. Load Participants & Connect WS
            await loadParticipants(id);
            await connectWebSocket(id);

            return true;
        } else {
             toast.error(response.error?.message || "Join failed");
             return false;
        }
    } catch (e) {
        console.error(e);
        return false;
    }
  }, [loadRoom, loadParticipants, connectWebSocket]);

  // Leave Room Action
  const leaveRoom = useCallback(async () => {
    if (!roomId) return;

    // API Call
    if (currentParticipantId) {
        try {
            await participantService.leaveRoom(roomId, currentParticipantId);
        } catch (e) { console.error(e); }
    }

    // Disconnect WS
    wsClient.disconnect();
    if (heartbeatIntervalRef.current) clearInterval(heartbeatIntervalRef.current);

    // Reset State
    setRoomId(null);
    setRoom(null);
    setParticipants([]);
    setListParticipants([]);
    setParticipantCount(null);
    setIsConnected(false);
    setChatMessages([]);
    localStorage.removeItem(`participant_${roomId}`);

    document.title = "FocusMate";
  }, [roomId, currentParticipantId]);

  const addChatMessage = useCallback((msg: RoomChatMessage) => {
      setChatMessages(prev => [...prev, msg]);
  }, []);

  const currentAuthUser = authService.getCurrentUser();
  const isHost = room?.host_id === currentAuthUser?.id; // Simple check

  return (
    <RoomContext.Provider
      value={{
        roomId,
        room,
        isLoading,
        participants,
        listParticipants,
        participantCount,
        currentParticipantId,
        participantName,
        isHost,
        timer: timer as any, // Cast to any to avoid strict type mismatch for now
        joinRoom,
        leaveRoom,
        isConnected,
        isConnecting,
        connectionError,
        chatMessages,
        addChatMessage
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
