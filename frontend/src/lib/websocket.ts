/**
 * WebSocket 클라이언트 - 실시간 타이머 동기화
 */

import { TimerState } from "../features/timer/types/timer.types";

// WebSocket 메시지 타입 정의 (서버 → 클라이언트)
export type WebSocketEventMessage =
  | {
      event: "timer_update";
      data: TimerState;
      timestamp: string;
    }
  | {
      event: "participant_update";
      data: {
        action: "joined" | "left";
        participant?: {
          id: string;
          name: string;
        };
        participant_id?: string;
        current_count: number;
      };
      timestamp: string;
    }
  | {
      event: "timer_complete";
      data: {
        completed_session_type: "work" | "break";
        next_session_type: "work" | "break";
        auto_start: boolean;
      };
      timestamp: string;
    }
  | {
      event: "pong";
      timestamp: string;
    }
  | {
      event: "error";
      error: {
        code: string;
        message: string;
      };
      timestamp: string;
    };

// WebSocket 액션 메시지 타입 정의 (클라이언트 → 서버)
export type WebSocketActionMessage =
  | {
      action: "start_timer";
      data?: {
        session_type: "work" | "break";
      };
    }
  | {
      action: "pause_timer";
    }
  | {
      action: "resume_timer";
    }
  | {
      action: "reset_timer";
    }
  | {
      action: "ping";
    };

// Legacy type for backward compatibility
export type WebSocketMessage = WebSocketEventMessage;

export type WebSocketEventHandler = (message: WebSocketEventMessage) => void;

class WebSocketClient {
  private ws: WebSocket | null = null;
  private roomId: string | null = null;
  private handlers: Set<WebSocketEventHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private shouldReconnect = true;
  private connectionStateCallbacks: Set<
    (
      state: "connecting" | "connected" | "disconnected",
      attempts?: number
    ) => void
  > = new Set();
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private readonly HEARTBEAT_INTERVAL = 30000; // 30 seconds
  private isOnline = navigator.onLine;
  private cleaningUpRoomId: string | null = null; // React StrictMode 대응: cleanup 중인 roomId
  private connectionPromise: Promise<void> | null = null; // 중복 연결 방지
  private cleanupTimeout: NodeJS.Timeout | null = null; // cleanup 플래그 리셋을 위한 timeout

  constructor() {
    // Listen to online/offline events
    window.addEventListener("online", () => {
      this.isOnline = true;
      if (!this.ws && this.roomId && this.shouldReconnect) {
        this.reconnectAttempts = 0; // Reset attempts on network recovery
        this.connect(this.roomId).catch(console.error);
      }
    });

    window.addEventListener("offline", () => {
      this.isOnline = false;
      if (this.heartbeatInterval) {
        clearInterval(this.heartbeatInterval);
        this.heartbeatInterval = null;
      }
    });
  }

  private startHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
    }

    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        try {
          this.sendPing();
        } catch (error) {
          console.error("Failed to send heartbeat:", error);
        }
      }
    }, this.HEARTBEAT_INTERVAL);
  }

  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  connect(roomId: string): Promise<void> {
    // React StrictMode 대응: 이미 연결 중이면 기존 Promise 반환
    if (this.connectionPromise && this.roomId === roomId) {
      return this.connectionPromise;
    }

    // 이미 연결되어 있으면 즉시 resolve
    if (this.ws?.readyState === WebSocket.OPEN && this.roomId === roomId) {
      return Promise.resolve();
    }

    // Cleanup 중이면 연결하지 않음 (같은 roomId인 경우만)
    if (this.cleaningUpRoomId === roomId) {
      console.log(`[WebSocket] Cleanup in progress for room ${roomId}, skipping connection`);
      return Promise.reject(new Error("Cleanup in progress"));
    }

    // 다른 roomId로 cleanup 중이면 cleanup 완료 대기
    if (this.cleaningUpRoomId && this.cleaningUpRoomId !== roomId) {
      console.log(`[WebSocket] Waiting for cleanup of room ${this.cleaningUpRoomId} to complete`);
      // 짧은 지연 후 재시도
      return new Promise((resolve, reject) => {
        setTimeout(() => {
          if (this.cleaningUpRoomId === roomId) {
            reject(new Error("Cleanup in progress"));
          } else {
            this.connect(roomId).then(resolve).catch(reject);
          }
        }, 50);
      });
    }

    this.connectionPromise = new Promise((resolve, reject) => {
      // Don't reconnect if offline
      if (!this.isOnline) {
        console.log("WebSocket: Offline, skipping reconnection");
        this.notifyConnectionState("disconnected", this.reconnectAttempts);
        this.connectionPromise = null;
        reject(new Error("Network offline"));
        return;
      }

      // Prevent multiple simultaneous connection attempts
      if (this.ws?.readyState === WebSocket.CONNECTING) {
        console.log("WebSocket: Already connecting, skipping");
        this.connectionPromise = null;
        return;
      }

      // 기존 연결이 있으면 정리
      if (this.ws && this.ws.readyState !== WebSocket.CLOSED) {
        try {
          this.ws.close();
        } catch (e) {
          // Ignore errors when closing
        }
      }

      this.roomId = roomId;
      const wsUrl = this.getWebSocketUrl(roomId);
      console.log(`[WebSocket] Connecting to ${wsUrl}`);

      try {
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
          // React StrictMode 대응: cleanup 중이면 연결 종료 (같은 roomId인 경우만)
          if (this.cleaningUpRoomId === roomId) {
            console.log(`[WebSocket] Cleanup in progress for room ${roomId}, closing connection`);
            try {
              this.ws?.close();
            } catch (e) {
              // Ignore errors
            }
            this.connectionPromise = null;
            return;
          }

          console.log(`[WebSocket] Connected to room ${roomId}`);
          this.reconnectAttempts = 0;
          this.startHeartbeat();
          this.notifyConnectionState("connected", 0);
          this.connectionPromise = null;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const message: WebSocketEventMessage = JSON.parse(event.data);

            // Handle pong response (heartbeat)
            if (message.event === "pong") {
              return; // No action needed for heartbeat
            }

            this.handlers.forEach((handler) => handler(message));
          } catch (error) {
            console.error("Failed to parse WebSocket message:", error);
          }
        };

        this.ws.onerror = (error) => {
          console.error(
            `[WebSocket] Error connecting to room ${roomId}:`,
            error
          );
          this.stopHeartbeat();
          this.connectionPromise = null;

          // 에러 상세 정보 로깅
          if (this.ws) {
            console.error(
              `[WebSocket] ReadyState: ${this.ws.readyState}, URL: ${wsUrl}`
            );
          }

          reject(error);
        };

        this.ws.onclose = (event) => {
          this.ws = null;
          this.stopHeartbeat();
          this.connectionPromise = null;

          const closeInfo = {
            code: event.code,
            reason: event.reason,
            wasClean: event.wasClean,
            roomId: this.roomId || roomId, // 현재 roomId 사용, 없으면 파라미터 사용
          };

          // 에러 코드별 상세 로깅
          if (event.code === 1006) {
            console.error(
              "[WebSocket] Abnormal closure (1006) - Connection lost without close frame",
              closeInfo
            );
          } else if (event.code === 1012) {
            console.error(
              "[WebSocket] Service restart (1012) - Server is restarting",
              closeInfo
            );
          } else if (event.code === 1005) {
            console.warn(
              "[WebSocket] No status code (1005) - Connection closed without status",
              closeInfo
            );
          } else {
            console.log("[WebSocket] Disconnected", closeInfo);
          }

          // Cleanup 중이면 재연결하지 않음 (같은 roomId인 경우만)
          const currentRoomId = this.roomId || roomId;
          if (this.cleaningUpRoomId === currentRoomId) {
            console.log(
              `[WebSocket] Cleanup in progress for room ${currentRoomId}, skipping reconnection`
            );
            this.notifyConnectionState("disconnected", this.reconnectAttempts);
            return;
          }

          if (
            this.shouldReconnect &&
            this.reconnectAttempts < this.maxReconnectAttempts &&
            this.isOnline
          ) {
            this.reconnectAttempts++;
            this.notifyConnectionState("connecting", this.reconnectAttempts);
            const delay = Math.min(
              this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
              30000
            ); // Exponential backoff, max 30s
            console.log(
              `[WebSocket] Reconnecting to room ${roomId} in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`
            );
            setTimeout(() => {
              const reconnectRoomId = this.roomId || roomId;
              if (
                reconnectRoomId &&
                this.shouldReconnect &&
                this.isOnline &&
                this.cleaningUpRoomId !== reconnectRoomId
              ) {
                this.connect(reconnectRoomId).catch((err) => {
                  console.error(
                    `[WebSocket] Reconnection failed for room ${reconnectRoomId}:`,
                    err
                  );
                });
              }
            }, delay);
          } else {
            this.notifyConnectionState("disconnected", this.reconnectAttempts);
          }
        };
      } catch (error) {
        console.error(
          `[WebSocket] Failed to create WebSocket for room ${roomId}:`,
          error
        );
        this.connectionPromise = null;
        reject(error);
      }
    });

    return this.connectionPromise;
  }

  disconnect(): void {
    const currentRoomId = this.roomId;

    // 이미 disconnect 중이면 무시
    if (!currentRoomId && !this.cleaningUpRoomId) {
      return;
    }

    console.log(`[WebSocket] Disconnecting from room ${currentRoomId || 'unknown'}`);

    // React StrictMode 대응: cleanup 중인 roomId 설정
    if (currentRoomId) {
      this.cleaningUpRoomId = currentRoomId;
    }

    this.shouldReconnect = false;
    this.stopHeartbeat();

    if (this.ws) {
      try {
        // 정상 종료 코드로 닫기
        if (
          this.ws.readyState === WebSocket.OPEN ||
          this.ws.readyState === WebSocket.CONNECTING
        ) {
          this.ws.close(1000, "Client disconnect"); // Normal closure
        }
      } catch (e) {
        console.warn("[WebSocket] Error closing connection:", e);
      }
      this.ws = null;
    }

    this.roomId = null;
    this.handlers.clear();
    this.reconnectAttempts = 0;
    this.connectionPromise = null;

    // Cleanup 완료 후 플래그 리셋
    // React StrictMode의 빠른 마운트/언마운트 사이클을 고려하여 짧은 지연 후 리셋
    // cleanup이 완전히 끝난 후에만 플래그 해제
    if (this.cleanupTimeout) {
      clearTimeout(this.cleanupTimeout);
    }
    this.cleanupTimeout = setTimeout(() => {
      // 같은 roomId에 대해서만 cleanup 플래그 해제
      if (this.cleaningUpRoomId === currentRoomId) {
        this.cleaningUpRoomId = null;
        console.log(`[WebSocket] Cleanup completed for room ${currentRoomId}`);
      }
      this.cleanupTimeout = null;
    }, 150); // 150ms 지연으로 cleanup 완료 보장
  }

  onMessage(handler: WebSocketEventHandler): () => void {
    this.handlers.add(handler);
    return () => {
      this.handlers.delete(handler);
    };
  }

  send(message: WebSocketActionMessage): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      // Convert frontend action format to backend format
      // Frontend sends: { action: "start_timer", data: {...} }
      // Backend expects: { type: "message", data: {...} }
      const backendMessage = {
        type:
          message.action === "start_timer"
            ? "timer_start"
            : message.action === "pause_timer"
              ? "timer_pause"
              : message.action === "resume_timer"
                ? "timer_resume"
                : message.action === "reset_timer"
                  ? "timer_reset"
                  : message.action === "ping"
                    ? "ping"
                    : "message",
        data: "data" in message && message.data ? message.data : {},
      };
      this.ws.send(JSON.stringify(backendMessage));
    } else {
      console.warn("WebSocket is not connected");
    }
  }

  // Helper methods for common actions
  sendStartTimer(sessionType: "work" | "break" = "work"): void {
    this.send({
      action: "start_timer",
      data: { session_type: sessionType },
    });
  }

  sendPauseTimer(): void {
    this.send({ action: "pause_timer" });
  }

  sendResumeTimer(): void {
    this.send({ action: "resume_timer" });
  }

  sendResetTimer(): void {
    this.send({ action: "reset_timer" });
  }

  sendPing(): void {
    this.send({ action: "ping" });
  }

  private getWebSocketUrl(roomId: string): string {
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    const env = (import.meta as any).env;
    // Use HTTP base URL and convert to WebSocket URL
    const apiBaseUrl = env?.VITE_API_BASE_URL || "http://localhost:8000/api/v1";
    // Convert http:// to ws:// and https:// to wss://
    // Fix: Replace http:// with ws:// (not just http: with ws:)
    const wsBaseUrl = apiBaseUrl
      .replace(/^http:\/\//, "ws://")
      .replace(/^https:\/\//, "wss://");
    // Backend endpoint is /api/v1/ws/{room_id}
    return `${wsBaseUrl}/ws/${roomId}`;
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN || false;
  }

  getConnectionState(): "connecting" | "connected" | "disconnected" {
    if (!this.ws) return "disconnected";
    switch (this.ws.readyState) {
      case WebSocket.CONNECTING:
        return "connecting";
      case WebSocket.OPEN:
        return "connected";
      default:
        return "disconnected";
    }
  }

  onConnectionChange(
    callback: (
      state: "connecting" | "connected" | "disconnected",
      attempts?: number
    ) => void
  ): () => void {
    this.connectionStateCallbacks.add(callback);

    // 즉시 현재 상태 알림
    callback(this.getConnectionState(), this.reconnectAttempts);

    return () => {
      this.connectionStateCallbacks.delete(callback);
    };
  }

  private notifyConnectionState(
    state: "connecting" | "connected" | "disconnected",
    attempts?: number
  ): void {
    this.connectionStateCallbacks.forEach((callback) => {
      callback(state, attempts);
    });
  }

  getReconnectAttempts(): number {
    return this.reconnectAttempts;
  }

  getMaxReconnectAttempts(): number {
    return this.maxReconnectAttempts;
  }

  // Getter for roomId (for external access)
  get currentRoomId(): string | null {
    return this.roomId;
  }
}

export const wsClient = new WebSocketClient();
