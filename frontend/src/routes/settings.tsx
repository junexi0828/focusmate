import { createFileRoute, redirect } from "@tanstack/react-router";
import Settings from "../pages/Settings";
import { authService } from "../features/auth/services/authService";
import { toast } from "sonner";

export const Route = createFileRoute("/settings")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  component: Settings,
});
