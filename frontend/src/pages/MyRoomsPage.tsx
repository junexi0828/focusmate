import React, { useState, useEffect } from "react";
import { useNavigate } from "@tanstack/react-router";
import { Card, CardContent, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Users, ArrowRight, ArrowLeft } from "lucide-react";
import { roomService } from "../features/room/services/roomService";
import { Room } from "../features/room/types/room.types";
import { authService } from "../features/auth/services/authService";
import { LoadingSpinner } from "../components/ui/loading";
import { toast } from "sonner";

export function MyRoomsPage() {
  const navigate = useNavigate();
  const [rooms, setRooms] = useState<Room[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    if (authService.isAuthenticated()) {
      loadMyRooms();
    } else {
      setIsLoading(false);
      toast.error("로그인이 필요합니다");
      navigate({ to: "/login" });
    }
  }, []);

  // Reload when page becomes visible
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.visibilityState === "visible" && authService.isAuthenticated()) {
        loadMyRooms();
      }
    };

    // Custom event listener for manual refresh
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
      } else {
        toast.error(response.error?.message || "참여방 목록을 불러오는데 실패했습니다");
      }
    } catch (error) {
      console.error("Failed to load my rooms:", error);
      toast.error("네트워크 오류가 발생했습니다");
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinRoom = (roomId: string) => {
    navigate({ to: "/room/$roomId", params: { roomId } });
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <div className="mb-6">
        <Button
          variant="ghost"
          size="sm"
          onClick={() => navigate({ to: "/" })}
          className="mb-4"
        >
          <ArrowLeft className="w-4 h-4 mr-2" />
          홈으로
        </Button>
        <h1 className="text-3xl font-bold">참여방</h1>
        <p className="text-muted-foreground mt-2">
          참여 중인 모든 방을 확인하세요
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="w-5 h-5" />
            참여 중인 방 ({rooms.length})
          </CardTitle>
        </CardHeader>
        <CardContent>
          {isLoading ? (
            <div className="flex justify-center py-8">
              <LoadingSpinner />
            </div>
          ) : !authService.isAuthenticated() ? (
            <div className="text-center py-6 space-y-3">
              <p className="text-sm text-muted-foreground">
                참여방 기능을 사용하려면 로그인이 필요합니다
              </p>
              <Button
                size="sm"
                onClick={() => navigate({ to: "/login" })}
              >
                로그인하기
              </Button>
            </div>
          ) : rooms.length === 0 ? (
            <div className="text-center py-12">
              <Users className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
              <p className="text-lg font-medium mb-2">참여 중인 방이 없습니다</p>
              <p className="text-sm text-muted-foreground mb-4">
                새로운 방을 만들거나 방 ID로 참여해보세요
              </p>
              <Button onClick={() => navigate({ to: "/" })}>
                방 만들기
              </Button>
            </div>
          ) : (
            <div className="space-y-3">
              {rooms.map((room) => (
                <div
                  key={room.id}
                  className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-accent transition-colors cursor-pointer"
                  onClick={() => handleJoinRoom(room.id)}
                >
                  <div className="flex-1 min-w-0">
                    <div className="text-base font-medium truncate">{room.name}</div>
                    <div className="text-sm text-muted-foreground mt-1">
                      {room.work_duration}분 집중 · {room.break_duration}분 휴식
                    </div>
                    {room.created_at && (
                      <div className="text-xs text-muted-foreground mt-1">
                        생성일: {new Date(room.created_at).toLocaleDateString("ko-KR")}
                      </div>
                    )}
                  </div>
                  <Button
                    size="sm"
                    variant="ghost"
                    className="h-8 w-8 p-0"
                    onClick={(e: React.MouseEvent) => {
                      e.stopPropagation();
                      handleJoinRoom(room.id);
                    }}
                  >
                    <ArrowRight className="w-4 h-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

