/**
 * WebSocket hook for real-time chat.
 */

import { useEffect, useRef, useState, useCallback } from "react";
import { authService } from "../../auth/services/authService";
import type { Message } from "../services/chatService";

const getWebSocketUrl = (): string => {
  const env = (import.meta as any).env;
  const apiBaseUrl = env?.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
  const wsBaseUrl = apiBaseUrl
    .replace(/^http:\/\//, "ws://")
    .replace(/^https:\/\//, "wss://");
  return `${wsBaseUrl}/chats/ws`;
};

export function useChatWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<Map<string, Message[]>>(new Map());
  const [typingUsers, setTypingUsers] = useState<Map<string, Set<string>>>(new Map()); // room_id -> Set of user_ids
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const joinedRoomsRef = useRef<Set<string>>(new Set());
  const typingTimeoutsRef = useRef<Map<string, NodeJS.Timeout>>(new Map()); // user_id -> timeout

  const connect = useCallback(() => {
    const token = authService.getToken();
    if (!token) return;

    const wsUrl = `${getWebSocketUrl()}?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log("Chat WebSocket connected");
      setIsConnected(true);

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
    };

    ws.onclose = () => {
      console.log("Chat WebSocket disconnected");
      setIsConnected(false);

      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    wsRef.current = ws;
  }, []);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    joinedRoomsRef.current.clear();
  }, []);

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

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return {
    isConnected,
    messages,
    typingUsers,
    joinRoom,
    leaveRoom,
    sendTyping,
  };
}

