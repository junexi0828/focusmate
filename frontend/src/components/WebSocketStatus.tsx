/**
 * WebSocket 연결 상태 표시 컴포넌트
 */

import { useEffect, useState } from "react";
import { Wifi, WifiOff } from "lucide-react";
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
  const [reconnectAttempts, setReconnectAttempts] = useState(0);

  useEffect(() => {
    if (!roomId) {
      setIsConnected(false);
      setIsConnecting(false);
      setConnectionError(null);
      setReconnectAttempts(0);
      return;
    }

    // WebSocket 연결 상태 변경 감지
    const unsubscribe = wsClient.onConnectionChange((state, attempts) => {
      setIsConnected(state === "connected");
      setIsConnecting(state === "connecting");
      setReconnectAttempts(attempts || 0);

      if (state === "disconnected" && roomId) {
        const maxAttempts = wsClient.getMaxReconnectAttempts();

        // 첫 번째 재연결 시도는 조용히 처리 (방 생성 직후 Race Condition 대응)
        if (attempts === 1) {
          setConnectionError(null);
        } else if (attempts && attempts >= maxAttempts) {
          // 최대 재연결 시도 횟수 초과
          setConnectionError("자동 재연결에 실패했습니다. 수동으로 재연결을 시도해주세요.");
        } else if (attempts && attempts > 1) {
          // 2번째 이상 재연결 시도 시에만 메시지 표시
          setConnectionError("연결이 끊어졌습니다. 재연결을 시도합니다...");
        }
      } else if (state === "connecting") {
        // 연결 중일 때는 재시도 횟수에 따라 메시지 표시
        if (reconnectAttempts > 1) {
          setConnectionError("재연결 중...");
        }
      } else {
        // 연결 성공 시 에러 메시지 제거
        setConnectionError(null);
      }
    });

    return () => {
      unsubscribe();
    };
  }, [roomId, reconnectAttempts]);

  return {
    isConnected,
    isConnecting,
    connectionError,
    reconnectAttempts,
  };
}

