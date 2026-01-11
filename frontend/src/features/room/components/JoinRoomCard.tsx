import React, { useState } from "react";
import {
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";
import { Button } from "../../../components/ui/button-enhanced";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { LogIn } from "lucide-react";

import { useTheme } from "../../../hooks/useTheme";

import { GlassCard } from "../../../components/ui/glass-card";

interface JoinRoomCardProps {
  onJoinRoom: (roomId: string) => void;
}

import { use3DCard } from "../../../hooks/use3DCard";

export function JoinRoomCard({ onJoinRoom }: JoinRoomCardProps) {
  const [roomId, setRoomId] = useState("");
  const [error, setError] = useState("");
  const [isJoining, setIsJoining] = useState(false);

  const { theme } = useTheme();
  const isFunMode = theme === "fun";

  // 3D Card Hook
  const { handleMouseMove, handleMouseLeave, style } = use3DCard(20);

  const normalizeRoomId = (value: string) => {
    const trimmed = value.trim();
    if (!trimmed) return "";

    // Allow full share URLs by extracting /room/{id}
    try {
      const url = new URL(trimmed);
      const match = url.pathname.match(/\/room\/([^/]+)/);
      if (match?.[1]) {
        return match[1];
      }
    } catch {
      // Not a URL, fall through to raw input
    }

    return trimmed;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const normalizedRoomId = normalizeRoomId(roomId);
    if (normalizedRoomId.length === 0) {
      setError("방 ID를 입력해주세요");
      return;
    }

    setIsJoining(true);
    setTimeout(() => {
      onJoinRoom(normalizedRoomId);
      setIsJoining(false);
    }, 500);
  };

  return (
    <GlassCard
      className={`relative w-full overflow-hidden shadow-lg transition-shadow ${
        isFunMode ? "hover:shadow-xl card-interactive" : ""
      }`}
      onMouseMove={isFunMode ? handleMouseMove : undefined}
      onMouseLeave={isFunMode ? handleMouseLeave : undefined}
      style={isFunMode ? style : undefined}
    >
      <CardHeader className="pb-6">
        <CardTitle className="flex items-center gap-3 text-2xl font-semibold">
          <LogIn className="w-6 h-6" />방 참여하기
        </CardTitle>
        <CardDescription className="text-base mt-2">
          초대받은 방의 ID를 입력하세요
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-3">
            <Label htmlFor="room-id" className="text-base font-medium">방 ID 또는 공유 URL</Label>
            <Input
              id="room-id"
              type="text"
              placeholder="예: abc-def-123"
              value={roomId}
              onChange={(e) => setRoomId(e.target.value)}
              className={`h-12 text-base ${error ? "border-destructive" : ""}`}
            />
            {error && <p className="text-sm text-destructive mt-1">{error}</p>}
          </div>

          <Button
            type="submit"
            variant="secondary"
            className="w-full h-12 text-base font-semibold mt-8"
            disabled={isJoining}
          >
            {isJoining ? "참여 중..." : "참여하기"}
          </Button>
        </form>
      </CardContent>
    </GlassCard>
  );
}
