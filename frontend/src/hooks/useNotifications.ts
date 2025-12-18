/**
 * Notification WebSocket Hook
 * Real-time notification updates via WebSocket
 */

import { useEffect, useState, useRef, useCallback } from "react";
import { authService } from "../features/auth/services/authService";
import { toast } from "sonner";

const WS_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";

export interface NotificationData {
  notification_id: string;
  type: string;
  title: string;
  message: string;
  data?: {
    routing?: {
      type: string;
      path: string;
      params?: Record<string, any>;
    };
    [key: string]: any;
  };
  created_at: string;
}

export interface NotificationMessage {
  type: "notification" | "connected" | "pong";
  data?: NotificationData;
  message?: string;
  user_id?: string;
}

export function useNotifications(onNewNotification?: (notification: NotificationData) => void) {
  const [isConnected, setIsConnected] = useState(false);
  const [notifications, setNotifications] = useState<NotificationData[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const pingIntervalRef = useRef<NodeJS.Timeout | undefined>(undefined);
  const reconnectAttemptsRef = useRef(0);
  const onNewNotificationRef = useRef(onNewNotification);
  const maxReconnectAttempts = 10;

  // Update callback ref when prop changes
  useEffect(() => {
    onNewNotificationRef.current = onNewNotification;
  }, [onNewNotification]);

  const connect = useCallback(() => {
    const token = authService.getToken();
    if (!token) {
      console.log("[Notifications] No token, skipping WebSocket connection");
      return;
    }

    // Don't attempt if already at max reconnection attempts
    if (reconnectAttemptsRef.current >= maxReconnectAttempts) {
      console.log("[Notifications] Max reconnection attempts already reached, skipping connection");
      return;
    }

    // Close existing connection
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      console.log("[Notifications] Already connected, skipping connection attempt");
      return;
    }

    if (wsRef.current) {
      wsRef.current.close();
    }

    try {
      const ws = new WebSocket(`${WS_URL}/api/v1/notifications/ws?token=${token}`);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log("[Notifications] WebSocket connected");
        setIsConnected(true);
        reconnectAttemptsRef.current = 0; // Reset reconnect attempts on successful connection

        // Send ping every 30 seconds to keep connection alive
        pingIntervalRef.current = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: "ping" }));
          }
        }, 30000);
      };

      ws.onmessage = (event) => {
        try {
          const message: NotificationMessage = JSON.parse(event.data);
          console.log("[Notifications] Received:", message);

          if (message.type === "connected") {
            console.log("[Notifications] Connection confirmed:", message.message);
          } else if (message.type === "notification" && message.data) {
            // Add to local state
            setNotifications((prev) => [message.data!, ...prev]);

            // Show toast
            toast.info(message.data.title, {
              description: message.data.message,
              duration: 5000,
            });

            // Call custom handler if provided
            if (onNewNotificationRef.current) {
              onNewNotificationRef.current(message.data);
            }
          } else if (message.type === "pong") {
            // Heartbeat response
            console.log("[Notifications] Pong received");
          }
        } catch (error) {
          console.error("[Notifications] Error parsing message:", error);
        }
      };

      ws.onerror = (error) => {
        console.error("[Notifications] WebSocket error:", error);
      };

      ws.onclose = () => {
        console.log("[Notifications] WebSocket disconnected");
        setIsConnected(false);

        // Clear ping interval
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
        }

        // Attempt to reconnect with exponential backoff
        if (reconnectAttemptsRef.current < maxReconnectAttempts) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttemptsRef.current), 30000);
          console.log(
            `[Notifications] Attempting to reconnect in ${delay}ms (attempt ${reconnectAttemptsRef.current + 1}/${maxReconnectAttempts})`
          );
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectAttemptsRef.current += 1;
            connect();
          }, delay);
        } else {
          console.error(
            `[Notifications] Max reconnection attempts (${maxReconnectAttempts}) reached. Giving up.`
          );
        }
      };
    } catch (error) {
      console.error("[Notifications] Failed to create WebSocket:", error);
    }
  }, []); // No dependencies - stable function

  const disconnect = useCallback(() => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = undefined;
    }

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = undefined;
    }

    // Reset reconnect attempts when manually disconnecting
    reconnectAttemptsRef.current = 0;
    setIsConnected(false);
  }, []);

  // Auto-connect when component mounts
  useEffect(() => {
    connect();

    return () => {
      disconnect();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount

  return {
    isConnected,
    notifications,
    connect,
    disconnect,
  };
}
