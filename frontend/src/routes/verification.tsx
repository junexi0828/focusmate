/**
 * Verification page route.
 */

import { createFileRoute, redirect } from "@tanstack/react-router";
import { authService } from "../features/auth/services/authService";
import { VerificationStatus, VerificationSettings } from "../features/verification";
import { PageTransition } from "../components/PageTransition";
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

function VerificationPage() {
  return (
    <PageTransition>
      <div className="space-y-6">
        <div>
          <h1 className="text-4xl font-bold tracking-tight">사용자 인증</h1>
          <p className="text-muted-foreground mt-2">
            학교 인증을 통해 매칭 시스템을 이용하세요
          </p>
        </div>

        <VerificationStatus />
        <VerificationSettings />
      </div>
    </PageTransition>
  );
}
