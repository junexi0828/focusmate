import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { HomePage } from "../pages/Home";
import { PageTransition } from "../components/PageTransition";
import { roomService } from "../features/room/services/roomService";
import { toast } from "sonner";

export const Route = createFileRoute("/")({
  component: IndexComponent,
});

function IndexComponent() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(false);

  const handleCreateRoom = async (
    roomName: string,
    focusTime: number,
    breakTime: number
  ) => {
    setIsLoading(true);
    try {
      const response = await roomService.createRoom({
        name: roomName,
        work_duration: focusTime * 60, // 분을 초로 변환
        break_duration: breakTime * 60, // 분을 초로 변환
        auto_start_break: false,
      });

      if (response.status === "success" && response.data) {
        const room = response.data;
        const roomId = room.id || room.room_id || ""; // 하위 호환성
        if (!roomId) {
          toast.error("방 ID를 받아오지 못했습니다");
          return;
        }

        // 방 생성 후 자동으로 참여 (방장으로 참여)
        const { participantService } = await import("../features/participants/services/participantService");
        const { authService } = await import("../features/auth/services/authService");

        // 사용자 이름 가져오기 (localStorage 또는 인증 정보에서)
        let username = localStorage.getItem("participant_name") || "";
        const user = authService.getCurrentUser();
        const userId = user?.id || null;

        if (!username) {
          username = user?.username || user?.email?.split("@")[0] || "사용자";
          localStorage.setItem("participant_name", username);
        }

        // 방에 참여 (인증된 사용자의 경우 user_id 전달)
        const joinResponse = await participantService.joinRoom(roomId, {
          username: username,
          user_id: userId, // 인증된 사용자의 경우 user_id 전달
        });

        if (joinResponse.status === "success" && joinResponse.data) {
          // 참여 성공 시 participant ID 저장
          const participantId = joinResponse.data.id || joinResponse.data.participant_id || "";
          if (participantId) {
            localStorage.setItem(`participant_${roomId}`, participantId);
          }

          // 방으로 이동
          navigate({ to: "/room/$roomId", params: { roomId } });
          toast.success("방이 생성되고 참여되었습니다!");

          // Trigger refresh of MyRoomsSection
          window.dispatchEvent(new Event("refreshMyRooms"));
        } else {
          // 참여 실패해도 방으로 이동 (Room 페이지에서 다시 참여 시도)
          navigate({ to: "/room/$roomId", params: { roomId } });
          toast.warning("방이 생성되었습니다. 참여 중...");
        }
      } else {
        const errorMessage =
          response.error?.message || "방 생성에 실패했습니다";
        toast.error(errorMessage);
      }
    } catch (error) {
      console.error("Failed to create room:", error);
      toast.error("네트워크 오류가 발생했습니다");
    } finally {
      setIsLoading(false);
    }
  };

  const handleJoinRoom = async (roomId: string) => {
    setIsLoading(true);
    try {
      const extractedRoomId = roomId.includes("/room/")
        ? roomId.split("/room/")[1].split("?")[0]
        : roomId.trim();

      const response = await roomService.getRoom(extractedRoomId);

      if (response.status === "success" && response.data) {
        const room = response.data;
        const roomId = room.id || room.room_id || extractedRoomId;
        navigate({ to: "/room/$roomId", params: { roomId } });
        toast.success("방에 참여했습니다!");
      } else {
        if (response.error?.code === "ROOM_NOT_FOUND") {
          toast.error("방을 찾을 수 없습니다. 방 ID를 확인해주세요.");
        } else {
          const errorMessage =
            response.error?.message || "방 참여에 실패했습니다";
          toast.error(errorMessage);
        }
      }
    } catch (error) {
      console.error("Failed to join room:", error);
      toast.error("네트워크 오류가 발생했습니다");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <PageTransition>
      {isLoading && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      )}
      <HomePage onCreateRoom={handleCreateRoom} onJoinRoom={handleJoinRoom} />
    </PageTransition>
  );
}
