import React from "react";
import { useRoomContext } from "../../../contexts/RoomContext";
import { useLocation, useNavigate } from "@tanstack/react-router";
import { Button } from "../../../components/ui/button";
import { Loader2, Pause, Play } from "lucide-react";

export function GlobalTimerWidget() {
  const {
    roomId,
    timer,
    isConnected,
    room
  } = useRoomContext();
  const location = useLocation();
  const navigate = useNavigate();

  // Hide if no active room or if we are already on the room page
  if (!roomId || location.pathname.startsWith(`/room/${roomId}`)) {
    return null;
  }

  // Hide if timer is idle/completed? (User choice, asking "Timer disappears" implies they want to see it running)
  // Let's show it if we have a room.

  const { minutes, seconds, status, sessionType } = timer;
  const timeStr = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  const isWork = sessionType === "work";

  return (
    <div className="fixed bottom-4 right-4 z-50 animate-in slide-in-from-bottom-5 fade-in duration-300">
      <div className="bg-background/80 backdrop-blur-md border border-border shadow-lg rounded-full px-4 py-2 flex items-center gap-3 hover:bg-background/90 transition-colors">
        <div
          className="cursor-pointer flex items-center gap-3"
          onClick={() => navigate({ to: `/room/${roomId}` })}
        >
            <div className={`w-2 h-2 rounded-full ${isWork ? "bg-red-500 animate-pulse" : "bg-green-500"}`} />

            <div className="flex flex-col">
                <span className="text-xs font-semibold text-muted-foreground">
                    {room?.room_name || "FocusMate"}
                </span>
                <span className="font-mono font-bold tabular-nums text-lg leading-none">
                    {timeStr}
                </span>
            </div>
        </div>

        {/* Simple Controls (Optional, user didn't explicitly ask but it's handy) */}
        {/* Keeping it simple: clicking goes to room */}
        <Button
            size="icon"
            variant="ghost"
            className="h-8 w-8 rounded-full ml-1"
            onClick={(e) => {
                e.stopPropagation();
                if (status === 'running') timer.pauseTimer();
                else if (status === 'paused') timer.resumeTimer();
                else timer.startTimer();
            }}
        >
            {status === 'running' ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
        </Button>
      </div>
    </div>
  );
}
