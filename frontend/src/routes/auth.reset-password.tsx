import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useMutation } from "@tanstack/react-query";
import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { toast } from "sonner";
import { authService } from "../features/auth/services/authService";
import { PageTransition } from "../components/PageTransition";
import { useQueryClient } from "@tanstack/react-query";

export const Route = createFileRoute("/auth/reset-password")({
  validateSearch: (search: Record<string, unknown>) => {
    return {
      token: (search.token as string) || "",
    };
  },
  component: ResetPasswordComponent,
});

function ResetPasswordComponent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { token } = Route.useSearch();
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [isVerifying, setIsVerifying] = useState(true);
  const [isValidToken, setIsValidToken] = useState(false);

  // Verify token on mount
  useEffect(() => {
    if (!token) {
      toast.error("유효하지 않은 링크입니다");
      navigate({ to: "/login" });
      return;
    }

    authService
      .verifyPasswordResetToken({ token })
      .then((response) => {
        if (response.status === "success" && response.data?.valid) {
          setIsValidToken(true);
        } else {
          toast.error("만료되었거나 유효하지 않은 링크입니다");
          navigate({ to: "/login" });
        }
      })
      .catch(() => {
        toast.error("토큰 검증에 실패했습니다");
        navigate({ to: "/login" });
      })
      .finally(() => {
        setIsVerifying(false);
      });
  });

  const resetMutation = useMutation({
    mutationFn: (data: { token: string; new_password: string }) =>
      authService.completePasswordReset(data),
    onSuccess: (response) => {
      if (response.status === "success") {
        toast.success("비밀번호가 재설정되었습니다");
        queryClient.invalidateQueries();
        navigate({ to: "/login" });
      } else {
        toast.error(response.error?.message || "비밀번호 재설정에 실패했습니다");
      }
    },
    onError: (error: any) => {
      toast.error(
        error?.response?.data?.detail || "비밀번호 재설정에 실패했습니다"
      );
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (!password || password.length < 8) {
      toast.error("비밀번호는 최소 8자 이상이어야 합니다");
      return;
    }

    if (password !== confirmPassword) {
      toast.error("비밀번호가 일치하지 않습니다");
      return;
    }

    if (!token) {
      toast.error("유효하지 않은 토큰입니다");
      return;
    }

    resetMutation.mutate({ token, new_password: password });
  };

  if (isVerifying) {
    return (
      <PageTransition>
        <div className="min-h-screen flex items-center justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
        </div>
      </PageTransition>
    );
  }

  if (!isValidToken) {
    return null;
  }

  return (
    <PageTransition>
      <div className="min-h-screen flex items-center justify-center p-4 bg-muted/30">
        <Card className="w-full max-w-md">
          <CardHeader>
            <CardTitle>새 비밀번호 설정</CardTitle>
            <CardDescription>
              새로운 비밀번호를 입력해주세요
            </CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="password">새 비밀번호</Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="최소 8자 이상"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  minLength={8}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirmPassword">비밀번호 확인</Label>
                <Input
                  id="confirmPassword"
                  type="password"
                  placeholder="비밀번호를 다시 입력하세요"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  required
                  minLength={8}
                />
              </div>
              <Button
                type="submit"
                className="w-full"
                disabled={resetMutation.isPending}
              >
                {resetMutation.isPending ? "처리 중..." : "비밀번호 재설정"}
              </Button>
            </form>
          </CardContent>
        </Card>
      </div>
    </PageTransition>
  );
}

