/**
 * WebSocket hook for real-time chat with improved reconnection logic.
 */

import { useEffect, useRef, useState, useCallback } from "react";
import { authService } from "../../auth/services/authService";
import type { Message } from "../services/chatService";

const getWebSocketUrl = (): string => {
  const env = import.meta.env;
  const apiBaseUrl = env?.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
  const wsBaseUrl = apiBaseUrl
    .replace(/^http:\/\//, "ws://")
    .replace(/^https:\/\//, "wss://");
  return `${wsBaseUrl}/chats/ws`;
};

// Reconnection configuration
const MAX_RECONNECT_ATTEMPTS = 5;
const INITIAL_RECONNECT_DELAY = 1000; // 1 second
const MAX_RECONNECT_DELAY = 30000; // 30 seconds
const HEARTBEAT_INTERVAL = 5000; // 5 seconds (reduced from 30s to prevent connection timeout)

export function useChatWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [messages, setMessages] = useState<Map<string, Message[]>>(new Map());
  const [typingUsers, setTypingUsers] = useState<Map<string, Set<string>>>(new Map()); // room_id -> Set of user_ids
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const heartbeatIntervalRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const joinedRoomsRef = useRef<Set<string>>(new Set());
  const typingTimeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map()); // user_id -> timeout
  const reconnectAttemptsRef = useRef(0);
  const shouldReconnectRef = useRef(true);
  const isOnlineRef = useRef(navigator.onLine);
  const hasInitializedRef = useRef(false);
  const consecutive1005ErrorsRef = useRef(0);
  const isCleaningUpRef = useRef(false);
  const connectionTimeRef = useRef<number>(0);

  // Calculate exponential backoff delay
  const getReconnectDelay = useCallback((attempt: number): number => {
    const delay = Math.min(
      INITIAL_RECONNECT_DELAY * Math.pow(2, attempt - 1),
      MAX_RECONNECT_DELAY
    );
    return delay;
  }, []);

  // Clear all timers
  const clearTimers = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = undefined;
    }
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
      heartbeatIntervalRef.current = undefined;
    }
  }, []);

  // Start heartbeat to keep connection alive
  const startHeartbeat = useCallback((ws: WebSocket) => {
    if (heartbeatIntervalRef.current) {
      clearInterval(heartbeatIntervalRef.current);
    }

    heartbeatIntervalRef.current = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        try {
          ws.send(JSON.stringify({ type: "ping" }));
        } catch (error) {
          console.error("Failed to send heartbeat:", error);
        }
      }
    }, HEARTBEAT_INTERVAL);
  }, []);

  const connect = useCallback(() => {
    // Prevent connection during cleanup (React StrictMode double-mount)
    if (isCleaningUpRef.current) {
      console.log("Chat WebSocket: Cleanup in progress, skipping connection");
      return;
    }

    const token = authService.getToken();
    if (!token || !shouldReconnectRef.current) return;

    // Check if token is expired
    if (authService.isTokenExpired()) {
      console.warn("Chat WebSocket: Token expired, stopping reconnection attempts");
      shouldReconnectRef.current = false;
      setIsConnecting(false);
      setIsConnected(false);
      // Clear token and redirect to login
      authService.logout();
      window.location.href = "/login";
      return;
    }

    // Don't reconnect if offline
    if (!isOnlineRef.current) {
      console.log("Chat WebSocket: Offline, skipping reconnection");
      return;
    }

    // Prevent multiple simultaneous connection attempts
    if (wsRef.current?.readyState === WebSocket.CONNECTING) {
      console.log("Chat WebSocket: Already connecting, skipping");
      return;
    }

    // If already connected and open, don't reconnect
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      console.log("Chat WebSocket: Already connected, skipping");
      return;
    }

    // Close existing connection if any (but not if it's already open)
    if (wsRef.current && wsRef.current.readyState !== WebSocket.OPEN) {
      try {
        wsRef.current.close();
      } catch (e) {
        // Ignore errors when closing
      }
      wsRef.current = null;
    }

    setIsConnecting(true);
    const wsUrl = `${getWebSocketUrl()}?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      // Check if we're cleaning up (React StrictMode double-mount)
      if (isCleaningUpRef.current) {
        console.log("Chat WebSocket: Cleanup in progress, closing connection");
        try {
          ws.close();
        } catch (e) {
          // Ignore errors
        }
        return;
      }

      connectionTimeRef.current = Date.now();
      console.log("Chat WebSocket connected");
      setIsConnected(true);
      setIsConnecting(false);
      reconnectAttemptsRef.current = 0; // Reset on successful connection
      consecutive1005ErrorsRef.current = 0; // Reset consecutive 1005 errors on successful connection

      // Send immediate ping to keep connection alive and verify backend is responsive
      try {
        ws.send(JSON.stringify({ type: "ping" }));
        console.log("Chat WebSocket: Sent initial ping");
      } catch (error) {
        console.error("Chat WebSocket: Failed to send initial ping:", error);
      }

      // Start heartbeat
      startHeartbeat(ws);

      // Rejoin all previously joined rooms
      joinedRoomsRef.current.forEach((roomId) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(
            JSON.stringify({
              type: "join_room",
              room_id: roomId,
            })
          );
        }
      });
    };

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Handle pong response
        if (data.type === "pong") {
          console.log("[WebSocket] Received pong from server");
          return; // Heartbeat response, no action needed
        }

        // Handle connection confirmation
        if (data.type === "connected") {
          console.log("Chat WebSocket: Connection confirmed by server");
          return; // Connection confirmed, no action needed
        }

        if (data.type === "message" && data.message) {
          const message: Message = data.message;
          setMessages((prev) => {
            const roomMessages = prev.get(message.room_id) || [];
            // Check if message already exists (avoid duplicates)
            const exists = roomMessages.some(
              (m) => m.message_id === message.message_id
            );
            if (exists) return prev;
            return new Map(prev).set(message.room_id, [...roomMessages, message]);
          });
        } else if (data.type === "message_updated" && data.message) {
          const message: Message = data.message;
          setMessages((prev) => {
            const roomMessages = prev.get(message.room_id) || [];
            const updated = roomMessages.map((msg) =>
              msg.message_id === message.message_id ? message : msg
            );
            return new Map(prev).set(message.room_id, updated);
          });
        } else if (
          data.type === "message_deleted" &&
          data.message_id &&
          data.room_id
        ) {
          setMessages((prev) => {
            const roomMessages = prev.get(data.room_id) || [];
            const filtered = roomMessages.filter(
              (msg) => msg.message_id !== data.message_id
            );
            return new Map(prev).set(data.room_id, filtered);
          });
        } else if (data.type === "joined" || data.type === "left") {
          // Room join/leave confirmation
          console.log(`Room ${data.room_id}: ${data.type}`);
        } else if (data.type === "typing" && data.room_id && data.user_id) {
          // Typing indicator
          setTypingUsers((prev) => {
            const roomTyping = prev.get(data.room_id) || new Set();
            roomTyping.add(data.user_id);
            const newMap = new Map(prev);
            newMap.set(data.room_id, roomTyping);

            // Clear existing timeout for this user
            const timeoutKey = `${data.room_id}-${data.user_id}`;
            const existingTimeout = typingTimeoutsRef.current.get(timeoutKey);
            if (existingTimeout) {
              clearTimeout(existingTimeout);
            }

            // Set timeout to remove typing indicator after 3 seconds
            const timeout = setTimeout(() => {
              setTypingUsers((current) => {
                const currentRoomTyping = current.get(data.room_id) || new Set();
                currentRoomTyping.delete(data.user_id);
                const updatedMap = new Map(current);
                if (currentRoomTyping.size === 0) {
                  updatedMap.delete(data.room_id);
                } else {
                  updatedMap.set(data.room_id, currentRoomTyping);
                }
                return updatedMap;
              });
              typingTimeoutsRef.current.delete(timeoutKey);
            }, 3000);

            typingTimeoutsRef.current.set(timeoutKey, timeout);
            return newMap;
          });
        }
      } catch (error) {
        console.error("WebSocket message error:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("Chat WebSocket error:", error);
      setIsConnecting(false);
    };

    ws.onclose = (event) => {
      const connectionDuration = connectionTimeRef.current
        ? Date.now() - connectionTimeRef.current
        : 0;

      console.log("Chat WebSocket disconnected", {
        code: event.code,
        reason: event.reason,
        wasClean: event.wasClean,
        duration: `${connectionDuration}ms`,
        timestamp: new Date().toISOString(),
      });

      setIsConnected(false);
      setIsConnecting(false);
      clearTimers();

      // If connection lasted less than 100ms, likely React StrictMode cleanup
      if (connectionDuration > 0 && connectionDuration < 100) {
        console.warn(
          `Chat WebSocket: Connection closed very quickly (${connectionDuration}ms), ` +
          "likely due to React StrictMode double-mount. This is normal in development."
        );
        // Don't reconnect if it was a very short connection (likely cleanup)
        if (isCleaningUpRef.current) {
          return;
        }
      }

      // Code 1005: No Status Received - server closed connection without close frame
      // This is often a normal closure (browser tab closed, navigation, etc.)
      // Only treat as error if it happens repeatedly or with expired token
      if (event.code === 1005) {
        // Check if token is expired first
        if (authService.isTokenExpired()) {
          console.warn("Chat WebSocket: Token expired (code 1005), stopping reconnection");
          shouldReconnectRef.current = false;
          authService.logout();
          window.location.href = "/login";
          return;
        }

        // Code 1005 can be normal (tab closed, navigation, etc.)
        // Only log as warning if it happens multiple times consecutively
        consecutive1005ErrorsRef.current++;

        // If 1005 errors occur consecutively 3+ times, might be server issue
        if (consecutive1005ErrorsRef.current >= 3) {
          console.warn(
            `Chat WebSocket: ${consecutive1005ErrorsRef.current} consecutive 1005 closures. ` +
            "This might indicate a server-side issue. Will attempt reconnection."
          );
          // Don't stop reconnecting, just log the warning
        } else {
          // Normal closure - just log debug info
          console.log(
            `Chat WebSocket: Connection closed normally (code 1005). Duration: ${connectionDuration}ms`
          );
        }
      } else {
        // Reset counter if different error code
        consecutive1005ErrorsRef.current = 0;
      }

      // Check if connection was rejected due to expired token (403 Forbidden or 1008 Policy Violation)
      if (event.code === 1008 || event.code === 403) {
        // Check if token is expired
        if (authService.isTokenExpired()) {
          console.warn("Chat WebSocket: Token expired, stopping reconnection");
          shouldReconnectRef.current = false;
          authService.logout();
          window.location.href = "/login";
          return;
        }
      }

      // Don't reconnect if manually disconnected or max attempts reached
      if (!shouldReconnectRef.current) {
        return;
      }

      if (reconnectAttemptsRef.current >= MAX_RECONNECT_ATTEMPTS) {
        console.error(
          `Chat WebSocket: Max reconnection attempts (${MAX_RECONNECT_ATTEMPTS}) reached`
        );
        return;
      }

      // For code 1005, use longer delay to avoid rapid reconnection loops
      const baseDelay = event.code === 1005 ? 3000 : 1000;

      // Exponential backoff reconnection
      reconnectAttemptsRef.current++;
      const delay = Math.max(
        getReconnectDelay(reconnectAttemptsRef.current),
        baseDelay
      );
      console.log(
        `Chat WebSocket: Reconnecting in ${delay}ms (attempt ${reconnectAttemptsRef.current}/${MAX_RECONNECT_ATTEMPTS})`
      );

      reconnectTimeoutRef.current = setTimeout(() => {
        if (shouldReconnectRef.current && isOnlineRef.current) {
          connect();
        }
      }, delay);
    };

    wsRef.current = ws;
  }, [clearTimers, getReconnectDelay, startHeartbeat]);

  const disconnect = useCallback(() => {
    isCleaningUpRef.current = true;
    shouldReconnectRef.current = false;
    clearTimers();
    if (wsRef.current) {
      try {
        wsRef.current.close();
      } catch (e) {
        // Ignore errors during cleanup
      }
      wsRef.current = null;
    }
    setIsConnected(false);
    setIsConnecting(false);
    joinedRoomsRef.current.clear();

    // Reset cleanup flag after a short delay to allow cleanup to complete
    setTimeout(() => {
      isCleaningUpRef.current = false;
    }, 100);
  }, [clearTimers]);

  const joinRoom = useCallback((roomId: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "join_room",
          room_id: roomId,
        })
      );
      joinedRoomsRef.current.add(roomId);
    }
  }, []);

  const leaveRoom = useCallback((roomId: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "leave_room",
          room_id: roomId,
        })
      );
      joinedRoomsRef.current.delete(roomId);
    }
  }, []);

  const sendTyping = useCallback((roomId: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "typing",
          room_id: roomId,
        })
      );
    }
  }, []);

  // Handle online/offline events
  useEffect(() => {
    const handleOnline = () => {
      console.log("Chat WebSocket: Network online, attempting reconnection");
      isOnlineRef.current = true;
      if (!isConnected && shouldReconnectRef.current) {
        reconnectAttemptsRef.current = 0; // Reset attempts on network recovery
        connect();
      }
    };

    const handleOffline = () => {
      console.log("Chat WebSocket: Network offline");
      isOnlineRef.current = false;
      clearTimers();
    };

    window.addEventListener("online", handleOnline);
    window.addEventListener("offline", handleOffline);

    return () => {
      window.removeEventListener("online", handleOnline);
      window.removeEventListener("offline", handleOffline);
    };
  }, [connect, clearTimers, isConnected]);

  useEffect(() => {
    // Prevent double initialization in React StrictMode
    if (hasInitializedRef.current) {
      return;
    }

    const mountTime = Date.now();
    hasInitializedRef.current = true;
    shouldReconnectRef.current = true;
    connect();

    return () => {
      // React StrictMode 대응: 마운트 후 200ms 이내 cleanup은 무시
      const timeSinceMount = Date.now() - mountTime;
      if (timeSinceMount < 200 && !isConnected) {
        console.log(`[Chat WS] Skipping cleanup - React StrictMode double-mount detected (${timeSinceMount}ms)`);
        hasInitializedRef.current = false;
        return;
      }

      shouldReconnectRef.current = false;
      // cleanup이 완료될 때까지 짧은 대기 후 disconnect
      setTimeout(() => {
        disconnect();
        hasInitializedRef.current = false;
      }, 100);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  return {
    isConnected,
    isConnecting,
    messages,
    typingUsers,
    joinRoom,
    leaveRoom,
    sendTyping,
    reconnectAttempts: reconnectAttemptsRef.current,
    maxReconnectAttempts: MAX_RECONNECT_ATTEMPTS,
  };
}

