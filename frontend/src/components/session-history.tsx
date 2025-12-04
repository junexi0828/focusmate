import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { ScrollArea } from "./ui/scroll-area";
import { mockSessions } from "../utils/mock-data";
import { History, CheckCircle2, XCircle, Clock } from "lucide-react";

export function SessionHistory() {
  const recentSessions = mockSessions.slice(0, 20);

  const formatDate = (date: Date) => {
    const now = new Date();
    const diffInDays = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60 * 24));
    
    if (diffInDays === 0) return "오늘";
    if (diffInDays === 1) return "어제";
    if (diffInDays < 7) return `${diffInDays}일 전`;
    
    return date.toLocaleDateString("ko-KR", {
      month: "short",
      day: "numeric",
    });
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString("ko-KR", {
      hour: "2-digit",
      minute: "2-digit",
    });
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <History className="w-5 h-5" />
          세션 히스토리
        </CardTitle>
        <CardDescription>최근 집중 및 휴식 세션 기록</CardDescription>
      </CardHeader>
      <CardContent>
        <ScrollArea className="h-[500px] pr-4">
          <div className="space-y-4">
            {recentSessions.map((session) => (
              <div
                key={session.id}
                className="flex items-start gap-4 p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
              >
                {/* Icon */}
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                    session.type === "focus"
                      ? "bg-primary/10 text-primary"
                      : "bg-secondary/10 text-secondary"
                  }`}
                >
                  <Clock className="w-5 h-5" />
                </div>

                {/* Content */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <Badge
                      variant={session.type === "focus" ? "default" : "secondary"}
                      className="text-xs"
                    >
                      {session.type === "focus" ? "집중" : "휴식"}
                    </Badge>
                    {session.completed ? (
                      <CheckCircle2 className="w-4 h-4 text-secondary" />
                    ) : (
                      <XCircle className="w-4 h-4 text-muted-foreground" />
                    )}
                  </div>
                  
                  <p className="text-sm">
                    {session.duration}분 {session.completed ? "완료" : "미완료"}
                  </p>
                  
                  {session.roomName && (
                    <p className="text-xs text-muted-foreground mt-1">
                      방: {session.roomName}
                    </p>
                  )}
                </div>

                {/* Date/Time */}
                <div className="text-right text-xs text-muted-foreground flex-shrink-0">
                  <p>{formatDate(session.date)}</p>
                  <p className="mt-1">{formatTime(session.date)}</p>
                </div>
              </div>
            ))}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
