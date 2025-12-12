/**
 * WebSocket 연결 상태 표시 컴포넌트
 */

import { useEffect, useState } from "react";
import { Wifi, WifiOff, Loader2 } from "lucide-react";
import { Badge } from "./ui/badge";
import { cn } from "./ui/utils";
import { wsClient } from "../lib/websocket";

interface WebSocketStatusProps {
  className?: string;
  showLabel?: boolean;
}

export function WebSocketStatus({ className, showLabel = true }: WebSocketStatusProps) {
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // 초기 연결 상태 확인
    setIsConnected(wsClient.isConnected());

    // 주기적으로 연결 상태 확인
    const checkInterval = setInterval(() => {
      setIsConnected(wsClient.isConnected());
    }, 1000);

    return () => {
      clearInterval(checkInterval);
    };
  }, []);

  // WebSocket 이벤트 리스너 (연결/끊김 감지)
  useEffect(() => {
    // WebSocket 클라이언트의 내부 상태를 추적하기 위해
    // 주기적으로 확인하는 방식 사용
    // (실제 구현에서는 WebSocket 클라이언트에 이벤트 리스너 추가 가능)
  }, []);

  return (
    <Badge
      variant={isConnected ? "default" : "destructive"}
      className={cn("flex items-center gap-1.5", className)}
    >
      {isConnected ? (
        <>
          <Wifi className="w-3 h-3" />
          {showLabel && <span>연결됨</span>}
        </>
      ) : (
        <>
          <WifiOff className="w-3 h-3" />
          {showLabel && <span>연결 끊김</span>}
        </>
      )}
    </Badge>
  );
}

/**
 * WebSocket 연결 상태를 관리하는 훅
 */
export function useWebSocketStatus(roomId: string | null) {
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);

  useEffect(() => {
    if (!roomId) {
      setIsConnected(false);
      setIsConnecting(false);
      return;
    }

    // WebSocket 연결 상태 변경 감지
    const unsubscribe = wsClient.onConnectionChange((state) => {
      setIsConnected(state === "connected");
      setIsConnecting(state === "connecting");

      if (state === "disconnected" && roomId) {
        setConnectionError("연결이 끊어졌습니다. 재연결을 시도합니다...");
      } else {
        setConnectionError(null);
      }
    });

    return () => {
      unsubscribe();
    };
  }, [roomId]);

  return {
    isConnected,
    isConnecting,
    connectionError,
  };
}

