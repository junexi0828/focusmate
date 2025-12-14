import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../../../components/ui/card";
import { Button } from "../../../components/ui/button-enhanced";
import { Input } from "../../../components/ui/input";
import { Label } from "../../../components/ui/label";
import { Slider } from "../../../components/ui/slider";
import { Plus } from "lucide-react";

interface CreateRoomCardProps {
  onCreateRoom: (
    roomName: string,
    focusTime: number,
    breakTime: number
  ) => void;
}

export function CreateRoomCard({ onCreateRoom }: CreateRoomCardProps) {
  const [roomName, setRoomName] = useState("");
  const [focusTime, setFocusTime] = useState(25);
  const [breakTime, setBreakTime] = useState(5);
  const [error, setError] = useState("");
  const [isCreating, setIsCreating] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    const trimmedName = roomName.trim();

    if (trimmedName.length < 3) {
      setError("방 이름은 최소 3자 이상이어야 합니다");
      return;
    }

    if (trimmedName.length > 50) {
      setError("방 이름은 최대 50자까지 가능합니다");
      return;
    }

    // Validate room name pattern: 영문, 숫자, 하이픈, 언더스코어만 허용
    const roomNamePattern = /^[a-zA-Z0-9_-]+$/;
    if (!roomNamePattern.test(trimmedName)) {
      setError("방 이름은 영문, 숫자, 하이픈(-), 언더스코어(_)만 사용할 수 있습니다");
      return;
    }

    setIsCreating(true);
    try {
      await onCreateRoom(trimmedName, focusTime, breakTime);
    } finally {
      setIsCreating(false);
    }
  };

  return (
    <Card className="w-full shadow-lg hover:shadow-xl transition-shadow">
      <CardHeader className="pb-6">
        <CardTitle className="flex items-center gap-3 text-2xl font-semibold">
          <Plus className="w-6 h-6" />새 방 만들기
        </CardTitle>
        <CardDescription className="text-base mt-2">
          팀과 함께 집중할 새로운 방을 만들어보세요
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-3">
            <Label htmlFor="room-name" className="text-base font-medium">방 이름</Label>
            <Input
              id="room-name"
              type="text"
              placeholder="예: 팀 집중 시간"
              value={roomName}
              onChange={(e) => setRoomName(e.target.value)}
              className={`h-12 text-base ${error ? "border-destructive" : ""}`}
              maxLength={50}
            />
            {error && <p className="text-sm text-destructive mt-1">{error}</p>}
          </div>

          <div className="space-y-5">
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <Label htmlFor="focus-time" className="text-base font-medium">집중 시간</Label>
                <span className="text-base font-semibold text-muted-foreground">
                  {focusTime}분
                </span>
              </div>
              <Slider
                id="focus-time"
                min={5}
                max={60}
                step={5}
                value={[focusTime]}
                onValueChange={(value: number[]) => setFocusTime(value[0])}
                className="w-full"
              />
            </div>

            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <Label htmlFor="break-time" className="text-base font-medium">휴식 시간</Label>
                <span className="text-base font-semibold text-muted-foreground">
                  {breakTime}분
                </span>
              </div>
              <Slider
                id="break-time"
                min={5}
                max={30}
                step={5}
                value={[breakTime]}
                onValueChange={(value: number[]) => setBreakTime(value[0])}
                className="w-full"
              />
            </div>
          </div>

          <Button
            type="submit"
            className="w-full h-12 text-base font-semibold mt-8"
            disabled={isCreating}
          >
            {isCreating ? "생성 중..." : "방 만들기"}
          </Button>
        </form>
      </CardContent>
    </Card>
  );
}
