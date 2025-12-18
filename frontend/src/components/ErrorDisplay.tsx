/**
 * Error Display Component
 * Shows detailed error information for debugging
 */

import { AlertCircle, RefreshCcw } from "lucide-react";
import { Button } from "./ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "./ui/card";

interface ErrorDisplayProps {
  error: Error | { message: string; stack?: string } | null;
  title?: string;
  onRetry?: () => void;
  showDetails?: boolean;
}

export function ErrorDisplay({
  error,
  title = "오류가 발생했습니다",
  onRetry,
  showDetails = true
}: ErrorDisplayProps) {
  if (!error) return null;

  const errorMessage = error instanceof Error ? error.message : error.message || "알 수 없는 오류";
  const errorStack = error instanceof Error ? error.stack : error.stack;

  return (
    <Card className="border-destructive">
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-destructive">
          <AlertCircle className="w-5 h-5" />
          {title}
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-sm">{errorMessage}</p>

        {showDetails && errorStack && (
          <details className="text-xs">
            <summary className="cursor-pointer text-muted-foreground hover:text-foreground">
              기술 정보 보기
            </summary>
            <pre className="mt-2 p-2 bg-muted rounded overflow-auto max-h-40">
              {errorStack}
            </pre>
          </details>
        )}

        {onRetry && (
          <Button onClick={onRetry} variant="outline" className="gap-2">
            <RefreshCcw className="w-4 h-4" />
            다시 시도
          </Button>
        )}
      </CardContent>
    </Card>
  );
}
