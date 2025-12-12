import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/card";
import { Badge } from "./ui/badge";
import { ScrollArea } from "./ui/scroll-area";
import { SessionRecord } from "../features/stats/services/statsService";
import { History, CheckCircle2, Clock } from "lucide-react";

interface SessionHistoryProps {
  sessions: SessionRecord[];
}

export function SessionHistory({ sessions }: SessionHistoryProps) {
  const recentSessions = [...sessions]
    .sort((a, b) => new Date(b.completed_at).getTime() - new Date(a.completed_at).getTime())
    .slice(0, 20);

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
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

  const formatTime = (dateString: string) => {
    const date = new Date(dateString);
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
            {recentSessions.length === 0 ? (
              <div className="text-center py-12 text-muted-foreground">
                <p>아직 완료된 세션이 없습니다</p>
                <p className="text-sm mt-2">포모도로 세션을 완료하면 여기에 표시됩니다</p>
              </div>
            ) : (
              recentSessions.map((session) => (
                <div
                  key={session.session_id}
                  className="flex items-start gap-4 p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                >
                  {/* Icon */}
                  <div
                    className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                      session.session_type === "work"
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
                        variant={session.session_type === "work" ? "default" : "secondary"}
                        className="text-xs"
                      >
                        {session.session_type === "work" ? "집중" : "휴식"}
                      </Badge>
                      <CheckCircle2 className="w-4 h-4 text-secondary" />
                    </div>

                    <p className="text-sm">
                      {session.duration_minutes}분 완료
                    </p>

                    {session.room_name && (
                      <p className="text-xs text-muted-foreground mt-1">
                        방: {session.room_name}
                      </p>
                    )}
                  </div>

                  {/* Date/Time */}
                  <div className="text-right text-xs text-muted-foreground flex-shrink-0">
                    <p>{formatDate(session.completed_at)}</p>
                    <p className="mt-1">{formatTime(session.completed_at)}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </ScrollArea>
      </CardContent>
    </Card>
  );
}
