import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { authService } from "../features/auth/services/authService";
import { PageTransition } from "../components/PageTransition";

export const Route = createFileRoute("/auth/naver/callback")({
  validateSearch: (search: Record<string, unknown>) => {
    return {
      code: (search.code as string) || "",
      state: (search.state as string) || "",
    };
  },
  component: NaverCallbackComponent,
});

function NaverCallbackComponent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { code, state } = Route.useSearch();

  useEffect(() => {
    const handleCallback = async () => {
      if (!code) {
        toast.error("인증 코드를 받지 못했습니다");
        navigate({ to: "/login" });
        return;
      }

      // Verify state if stored
      const storedState = sessionStorage.getItem("naver_oauth_state");
      if (storedState && state && storedState !== state) {
        toast.error("인증 상태가 일치하지 않습니다");
        sessionStorage.removeItem("naver_oauth_state");
        navigate({ to: "/login" });
        return;
      }

      try {
        const response = await authService.naverOAuthCallback(code, state);
        if (response.status === "success" && response.data) {
          // Store token and user
          authService.setToken(response.data.access_token);
          authService.setCurrentUser(response.data.user);
          sessionStorage.removeItem("naver_oauth_state");

          // Invalidate queries and redirect
          queryClient.invalidateQueries();
          toast.success("네이버 로그인 성공!");
          navigate({ to: "/" });
        } else {
          toast.error(response.error?.message || "네이버 로그인에 실패했습니다");
          navigate({ to: "/login" });
        }
      } catch (error: any) {
        toast.error(
          error?.response?.data?.detail || "네이버 로그인에 실패했습니다"
        );
        navigate({ to: "/login" });
      }
    };

    handleCallback();
  }, [code, state, navigate, queryClient]);

  return (
    <PageTransition>
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
          <p className="mt-4 text-muted-foreground">네이버 로그인 처리 중...</p>
        </div>
      </div>
    </PageTransition>
  );
}

