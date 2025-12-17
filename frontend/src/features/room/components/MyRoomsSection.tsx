import React, { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "../../../components/ui/card";
import { Button } from "../../../components/ui/button";
import { Users, ArrowRight } from "lucide-react";
import { roomService } from "../services/roomService";
import { Room } from "../types/room.types";
import { useNavigate } from "@tanstack/react-router";
import { authService } from "../../auth/services/authService";

export function MyRoomsSection() {
  const navigate = useNavigate();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Only load if user is authenticated
    if (authService.isAuthenticated()) {
      loadMyRooms();
    } else {
      setIsLoading(false);
    }
  }, []);

  // Reload when page becomes visible (e.g., after returning from room creation)
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible" && authService.isAuthenticated()) {
        loadMyRooms();
      }
    };

    // Custom event listener for manual refresh (e.g., after creating/leaving a room)
    const handleRefreshRooms = () => {
      if (authService.isAuthenticated()) {
        loadMyRooms();
      }
    };

    document.addEventListener("visibilitychange", handleVisibilityChange);
    window.addEventListener("refreshMyRooms", handleRefreshRooms);

    return () => {
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      window.removeEventListener("refreshMyRooms", handleRefreshRooms);
    };
  }, []);

  const loadMyRooms = async () => {
    setIsLoading(true);
    try {
      const response = await roomService.getMyRooms();
      if (response.status === "success" && response.data) {
        setRooms(response.data);
      }
    } catch (error) {
      console.error("Failed to load my rooms:", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinRoom = (roomId: string) => {
    navigate({ to: "/room/$roomId", params: { roomId } });
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center gap-2">
            <Users className="w-4 h-4" />
            참여방
          </CardTitle>
          {rooms.length > 0 && (
            <Button
              size="sm"
              variant="ghost"
              onClick={() => navigate({ to: "/reservations" })}
              className="text-xs"
            >
              전체 보기
            </Button>
          )}
        </div>
      </CardHeader>
      <CardContent>
        {isLoading ? (
          <div className="text-sm text-muted-foreground text-center py-4">
            로딩 중...
          </div>
        ) : rooms.length === 0 ? (
          <div className="text-sm text-muted-foreground text-center py-4">
            참여 중인 방이 없습니다
          </div>
        ) : (
          <div className="space-y-2">
            {rooms.slice(0, 3).map((room) => (
              <div
                key={room.id}
                className="flex items-center justify-between p-2 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
                onClick={() => handleJoinRoom(room.id)}
              >
                <div className="flex-1 min-w-0">
                  <div className="text-sm font-medium truncate">{room.name}</div>
                  <div className="text-xs text-muted-foreground mt-1">
                    {room.work_duration / 60}분 집중 · {room.break_duration / 60}분 휴식
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="ghost"
                  className="h-7 w-7 p-0"
                  onClick={(e: React.MouseEvent) => {
                    e.stopPropagation();
                    handleJoinRoom(room.id);
                  }}
                >
                  <ArrowRight className="w-3 h-3" />
                </Button>
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}

