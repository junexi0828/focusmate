import React from "react";
import { Button } from "../../../components/ui/button";
import { Play, Pause, RotateCcw } from "lucide-react";
import { TimerStatus } from "./TimerDisplay";

interface TimerControlsProps {
  status: TimerStatus;
  onStart: () => void;
  onPause: () => void;
  onReset: () => void;
}

export function TimerControls({
  status,
  onStart,
  onPause,
  onReset,
}: TimerControlsProps) {
  return (
    <div className="flex flex-wrap items-center justify-center gap-4">
      {status === "idle" || status === "paused" || status === "completed" ? (
        <Button onClick={onStart} size="lg" className="min-w-[140px]">
          <Play className="w-5 h-5 mr-2" />
          {status === "completed" ? "다시 시작" : "시작"}
        </Button>
      ) : (
        <Button
          onClick={onPause}
          size="lg"
          variant="outline"
          className="min-w-[140px] border-warning text-warning hover:bg-warning hover:text-warning-foreground"
        >
          <Pause className="w-5 h-5 mr-2" />
          일시정지
        </Button>
      )}

      <Button
        onClick={onReset}
        size="lg"
        variant="outline"
        className="min-w-[140px]"
        disabled={status === "idle"}
      >
        <RotateCcw className="w-5 h-5 mr-2" />
        재설정
      </Button>
    </div>
  );
}
