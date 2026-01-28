import { useRoomContext } from "../../../contexts/RoomContext";
import { useLocation, useNavigate } from "@tanstack/react-router";
import { Button } from "../../../components/ui/button";
import { Pause, Play } from "lucide-react";

import { motion } from "framer-motion";
import { useEffect, useState, useCallback } from "react";
import { useTimerPiP } from "../hooks/useTimerPiP";
import { PictureInPicture2 } from "lucide-react";

export function GlobalTimerWidget() {
  const {
    roomId,
    timer,
    room,
    participantName
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

  // Destructure stable functions from timer
  const { startTimer, pauseTimer, resumeTimer } = timer;
  const { minutes, seconds, status, sessionType } = timer;
  const timeStr = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
  const isWork = sessionType === "work";

  // Calculate progress for PiP
  const totalSeconds = isWork ? (timer as any).work_duration || 1500 : (timer as any).break_duration || 300;
  const remainingTotal = (minutes * 60) + seconds;
  const progress = totalSeconds > 0 ? ((totalSeconds - remainingTotal) / totalSeconds) * 100 : 0;

  const handlePlayPause = useCallback(() => {
    if (status === 'running') {
      pauseTimer();
    } else if (status === 'paused') {
      resumeTimer();
    } else {
      startTimer();
    }
  }, [status, startTimer, pauseTimer, resumeTimer]); // Dependencies are now clearer and mostly stable

  const { togglePiP, isPipActive, isSupported } = useTimerPiP({
    minutes,
    seconds,
    status,
    sessionType: isWork ? "focus" : "break",
    progress,
    userName: participantName || "User",
    onPlayPause: handlePlayPause,
  });

  // Keyboard shortcut: Alt + P to toggle PiP
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.altKey && e.key === 'p' && isSupported) {
        e.preventDefault();
        togglePiP();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [togglePiP, isSupported]);

  // Hide if no active room or if we are already on the room page
  if (!roomId || location.pathname.startsWith(`/room/${roomId}`)) {
    return null;
  }



  // Hide if position hasn't loaded (prevents jump)
  if (!position) return null;

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

        {/* PiP Toggle - Only show if supported */}
        {isSupported && (
          <Button
              size="icon"
              variant="ghost"
              className={`h-8 w-8 rounded-full ml-1 ${isPipActive ? "text-primary bg-primary/10" : "text-muted-foreground"}`}
              onClick={(e) => {
                  e.stopPropagation();
                  togglePiP();
              }}
              onPointerDown={(e) => e.stopPropagation()}
              title="타이머 팝업 (PiP) - Alt+P"
          >
              <PictureInPicture2 className="h-4 w-4" />
          </Button>
        )}

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
