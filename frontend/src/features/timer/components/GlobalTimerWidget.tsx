import React from "react";
import { useRoomContext } from "../../../contexts/RoomContext";
import { useLocation, useNavigate } from "@tanstack/react-router";
import { Button } from "../../../components/ui/button";
import { Loader2, Pause, Play } from "lucide-react";

import { motion } from "framer-motion";
import { useEffect, useState } from "react";

export function GlobalTimerWidget() {
  const {
    roomId,
    timer,
    isConnected,
    room
  } = useRoomContext();
  const location = useLocation();
  const navigate = useNavigate();
  const [position, setPosition] = useState<{ x: number, y: number } | null>(null);

  // Load saved position on mount
  useEffect(() => {
    const savedPos = localStorage.getItem("global-timer-position");
    if (savedPos) {
      try {
        setPosition(JSON.parse(savedPos));
      } catch (e) {
        console.error("Failed to parse saved timer position", e);
      }
    } else {
      setPosition({ x: 0, y: 0 });
    }
  }, []);

  // Hide if no active room or if we are already on the room page
  if (!roomId || location.pathname.startsWith(`/room/${roomId}`)) {
    return null;
  }

  // Hide if position hasn't loaded (prevents jump)
  if (!position) return null;

  const { minutes, seconds, status, sessionType } = timer;
  const timeStr = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  const isWork = sessionType === "work";

  return (
    <motion.div
      className="fixed bottom-4 right-4 z-50 animate-in slide-in-from-bottom-5 fade-in duration-300"
      drag
      dragMomentum={false}
      initial={position}
      style={{ x: position.x, y: position.y }}
      onDragEnd={(_, info) => {
        const newPos = {
          x: position.x + info.offset.x,
          y: position.y + info.offset.y
        };
        setPosition(newPos);
        localStorage.setItem("global-timer-position", JSON.stringify(newPos));
      }}
    >
      <div className="bg-background/80 backdrop-blur-md border border-border shadow-lg rounded-full px-4 py-2 flex items-center gap-3 hover:bg-background/90 transition-colors cursor-grab active:cursor-grabbing">
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

        {/* Simple Controls */}
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
             onPointerDown={(e) => e.stopPropagation()} // Prevent drag when clicking button
        >
            {status === 'running' ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
        </Button>
      </div>
    </motion.div>
  );
}
