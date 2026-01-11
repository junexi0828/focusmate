import { createFileRoute } from "@tanstack/react-router";
import { RoomPage } from "../pages/Room";
import { useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { authService } from "../features/auth/services/authService";

export const Route = createFileRoute('/room/$roomId')({
  component: RoomComponent,
});

function RoomComponent() {
  const navigate = useNavigate();
  const isAuthenticated =
    authService.isAuthenticated() && !authService.isTokenExpired();

  useEffect(() => {
    if (!isAuthenticated) {
      navigate({ to: "/login" });
    }
  }, [isAuthenticated, navigate]);

  const handleLeaveRoom = () => {
    navigate({ to: '/' });
  };

  if (!isAuthenticated) {
    return null;
  }

  return <RoomPage onLeaveRoom={handleLeaveRoom} />;
}
