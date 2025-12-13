/**
 * WebSocket 연결 상태 배너 컴포넌트
 * 연결 끊김 시 사용자에게 명확한 알림 제공
 */

import { RefreshCw, X, WifiOff } from "lucide-react";
import { Button } from "./ui/button";
import { Alert, AlertDescription, AlertTitle } from "./ui/alert";
import { cn } from "./ui/utils";

interface WebSocketConnectionBannerProps {
  isConnected: boolean;
  isConnecting: boolean;
  connectionError: string | null;
  reconnectAttempts?: number;
  maxReconnectAttempts?: number;
  onReconnect?: () => void;
  onDismiss?: () => void;
  className?: string;
}

export function WebSocketConnectionBanner({
  isConnected,
  isConnecting,
  connectionError,
  reconnectAttempts = 0,
  maxReconnectAttempts = 5,
  onReconnect,
  onDismiss,
  className,
}: WebSocketConnectionBannerProps) {
  // 연결되어 있으면 배너 표시 안 함
  if (isConnected && !connectionError) {
    return null;
  }

  // 재연결 중
  if (isConnecting) {
    return (
      <Alert className={cn("border-yellow-500 bg-yellow-50 dark:bg-yellow-950", className)}>
        <RefreshCw className="h-4 w-4 animate-spin text-yellow-600 dark:text-yellow-400" />
        <AlertTitle className="text-yellow-800 dark:text-yellow-200">
          실시간 동기화 재연결 중...
        </AlertTitle>
        <AlertDescription className="text-yellow-700 dark:text-yellow-300">
          {reconnectAttempts > 0 && (
            <span className="block mt-1">
              재연결 시도: {reconnectAttempts}/{maxReconnectAttempts}
            </span>
          )}
        </AlertDescription>
      </Alert>
    );
  }

  // 연결 끊김 및 재연결 실패
  if (connectionError || !isConnected) {
    const isMaxAttemptsReached = reconnectAttempts >= maxReconnectAttempts;

    return (
      <Alert
        className={cn(
          "border-destructive bg-destructive/10 dark:bg-destructive/20",
          className
        )}
      >
        <div className="flex items-start justify-between gap-4">
          <div className="flex items-start gap-3 flex-1">
            <WifiOff className="h-4 w-4 text-destructive mt-0.5" />
            <div className="flex-1">
              <AlertTitle className="text-destructive">
                실시간 동기화 연결 끊김
              </AlertTitle>
              <AlertDescription className="text-destructive/80 mt-1">
                {isMaxAttemptsReached ? (
                  <div className="space-y-2">
                    <p>
                      자동 재연결에 실패했습니다. 수동으로 재연결을 시도해주세요.
                    </p>
                    {onReconnect && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={onReconnect}
                        className="mt-2"
                      >
                        <RefreshCw className="w-3 h-3 mr-2" />
                        재연결 시도
                      </Button>
                    )}
                  </div>
                ) : (
                  <div>
                    <p>{connectionError || "연결이 끊어졌습니다."}</p>
                    {reconnectAttempts > 0 && (
                      <p className="text-sm mt-1">
                        재연결 시도 중: {reconnectAttempts}/{maxReconnectAttempts}
                      </p>
                    )}
                  </div>
                )}
              </AlertDescription>
            </div>
          </div>
          {onDismiss && (
            <Button
              variant="ghost"
              size="sm"
              onClick={onDismiss}
              className="h-6 w-6 p-0"
            >
              <X className="h-4 w-4" />
            </Button>
          )}
        </div>
      </Alert>
    );
  }

  return null;
}

