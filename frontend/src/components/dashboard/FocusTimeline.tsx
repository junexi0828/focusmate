import React, { useMemo } from "react";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import { BrainCircuit, Coffee, Clock } from "lucide-react";
import { ScrollArea } from "../ui/scroll-area";
import { Card, CardHeader, CardTitle, CardContent } from "../ui/card";
import { Badge } from "../ui/badge";
import { SessionRecord } from "../../utils/api-transformers";
import { cn } from "../ui/utils";

interface FocusTimelineProps {
  sessions: SessionRecord[];
}

export function FocusTimeline({ sessions }: FocusTimelineProps) {
  // Filter for today's sessions and sort by newest first
  const todaySessions = useMemo(() => {
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return sessions
      .filter((session) => {
        const sessionDate = new Date(session.completedAt);
        sessionDate.setHours(0, 0, 0, 0);
        return sessionDate.getTime() === today.getTime();
      })
      .sort(
        (a, b) =>
          new Date(b.completedAt).getTime() - new Date(a.completedAt).getTime()
      );
  }, [sessions]);

  // Calculate stats for the header
  const stats = useMemo(() => {
    const focusCount = todaySessions.filter((s) => s.sessionType === "work").length;
    const totalMinutes = todaySessions
      .filter((s) => s.sessionType === "work")
      .reduce((acc, s) => acc + s.durationMinutes, 0);

    return { focusCount, totalMinutes };
  }, [todaySessions]);

  return (
    <Card className="h-full flex flex-col border-border bg-card">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg font-semibold flex items-center gap-2">
            <Clock className="w-5 h-5 text-primary" />
            오늘의 집중 기록
          </CardTitle>
          <Badge variant="outline" className="font-normal">
            {stats.totalMinutes}분 집중 ({stats.focusCount}회)
          </Badge>
        </div>
      </CardHeader>
      <CardContent className="flex-1 min-h-0 pl-2 pr-4 pb-4">
        {todaySessions.length === 0 ? (
          <EmptyState />
        ) : (
          <ScrollArea className="h-[400px] pr-4">
            <div className="relative pl-6 space-y-8 py-2">
              {/* Vertical Line */}
              <div className="absolute left-[11px] top-2 bottom-2 w-0.5 bg-border/50" />

              {todaySessions.map((session, index) => (
                <TimelineItem
                  key={session.sessionId}
                  session={session}
                  isLast={index === todaySessions.length - 1}
                />
              ))}
            </div>
          </ScrollArea>
        )}
      </CardContent>
    </Card>
  );
}

function TimelineItem({ session, isLast }: { session: SessionRecord; isLast: boolean }) {
  const isWork = session.sessionType === "work";
  const date = new Date(session.completedAt);

  // Calculate start time based on duration (approximate, assuming completedAt is end time)
  const startTime = new Date(date.getTime() - session.durationMinutes * 60000);

  return (
    <div className={cn("relative group", isLast && "pb-0")}>
      {/* Node Dot */}
      <div
        className={cn(
          "absolute -left-[29px] top-1.5 w-6 h-6 rounded-full border-4 border-background flex items-center justify-center z-10 transition-transform group-hover:scale-110 shadow-sm",
          isWork ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"
        )}
      >
        {isWork ? <BrainCircuit className="w-3 h-3" /> : <Coffee className="w-3 h-3" />}
      </div>

      {/* Content */}
      <div className="flex flex-col gap-1 -mt-1">
        <div className="flex items-center justify-between">
          <span className={cn(
            "text-sm font-medium",
            isWork ? "text-foreground" : "text-muted-foreground"
          )}>
            {isWork ? "집중 세션" : "휴식"}
          </span>
          <span className="text-xs text-muted-foreground font-mono">
            {session.durationMinutes}m
          </span>
        </div>

        <div className="text-xs text-muted-foreground">
          {format(startTime, "a h:mm", { locale: ko })} - {format(date, "a h:mm", { locale: ko })}
        </div>

        {session.roomName && (
           <div className="text-xs text-muted-foreground/80 mt-1 line-clamp-1 bg-muted/40 px-2 py-0.5 rounded-sm w-fit max-w-full">
            in {session.roomName}
           </div>
        )}
      </div>
    </div>
  );
}

function EmptyState() {
  return (
    <div className="h-[300px] flex flex-col items-center justify-center text-center p-4 text-muted-foreground">
      <div className="w-12 h-12 rounded-full bg-muted/30 flex items-center justify-center mb-4">
        <Clock className="w-6 h-6 opacity-50" />
      </div>
      <p className="font-medium text-foreground mb-1">아직 기록이 없습니다</p>
      <p className="text-sm">오늘의 첫 번째 집중을 시작해보세요!</p>
    </div>
  );
}
