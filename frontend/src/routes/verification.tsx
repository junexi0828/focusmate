/**
 * Verification page route.
 */

import { createFileRoute, redirect } from "@tanstack/react-router";
import { authService } from "../features/auth/services/authService";
import VerificationPage from "../pages/Verification";
import { toast } from "sonner";

export const Route = createFileRoute("/verification")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  component: VerificationPage,
});
