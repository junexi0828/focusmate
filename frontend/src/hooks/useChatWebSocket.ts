/**
 * WebSocket hook for real-time chat.
 */

import { useEffect, useRef, useState, useCallback } from "react";
import type { WebSocketMessage, ChatMessage } from "@/types/chat";

const WS_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";
const WS_ENDPOINT = `${WS_URL}/api/v1/chats/ws`;

export function useChatWebSocket(token: string | null) {
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<Map<string, ChatMessage[]>>(
    new Map()
  );
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const connect = useCallback(() => {
    if (!token) return;

    const ws = new WebSocket(`${WS_ENDPOINT}?token=${token}`);

    ws.onopen = () => {
      console.log("WebSocket connected");
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);

        if (data.type === "message" && data.message) {
          setMessages((prev) => {
            const roomMessages = prev.get(data.message!.room_id) || [];
            return new Map(prev).set(data.message!.room_id, [
              ...roomMessages,
              data.message!,
            ]);
          });
        } else if (data.type === "message_updated" && data.message) {
          setMessages((prev) => {
            const roomMessages = prev.get(data.message!.room_id) || [];
            const updated = roomMessages.map((msg) =>
              msg.message_id === data.message!.message_id ? data.message! : msg
            );
            return new Map(prev).set(data.message!.room_id, updated);
          });
        } else if (
          data.type === "message_deleted" &&
          data.message_id &&
          data.room_id
        ) {
          setMessages((prev) => {
            const roomMessages = prev.get(data.room_id!) || [];
            const filtered = roomMessages.filter(
              (msg) => msg.message_id !== data.message_id
            );
            return new Map(prev).set(data.room_id!, filtered);
          });
        }
      } catch (error) {
        console.error("WebSocket message error:", error);
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setIsConnected(false);

      // Reconnect after 3 seconds
      reconnectTimeoutRef.current = setTimeout(() => {
        connect();
      }, 3000);
    };

    wsRef.current = ws;
  }, [token]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  const joinRoom = useCallback((roomId: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "join_room",
          room_id: roomId,
        })
      );
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
    joinRoom,
    leaveRoom,
    sendTyping,
  };
}
