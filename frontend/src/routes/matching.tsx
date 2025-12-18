import React from "react";
import { createFileRoute, redirect, Outlet } from "@tanstack/react-router";
import { authService } from "../features/auth/services/authService";
import { toast } from "sonner";

export const Route = createFileRoute("/matching")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  component: MatchingLayoutComponent,
});

function MatchingLayoutComponent() {
  return <Outlet />;
}
