import React, { useState } from "react";
import { LoginForm } from "../components/login-form";
import { SignupForm } from "../components/signup-form";
import { Timer } from "lucide-react";
import { Button } from "../components/ui/button-enhanced";
import { authService } from "../features/auth/services/authService";
import { toast } from "sonner";
import { useNavigate } from "@tanstack/react-router";
import { useQueryClient } from "@tanstack/react-query";

type AuthView = "login" | "signup";

interface AuthPageProps {
  onLogin: (email: string, password: string) => void;
  onSignup: (email: string, password: string, name: string) => void;
  isLoading?: boolean;
}

export function AuthPage({ onLogin, onSignup, isLoading = false }: AuthPageProps) {
  const [view, setView] = useState<AuthView>("login");
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const handleNaverLogin = async () => {
    try {
      const response = await authService.getNaverLoginUrl();
      if (response.status === "success" && response.data) {
        // Store state for verification
        if (response.data.state) {
          sessionStorage.setItem("naver_oauth_state", response.data.state);
        }
        // Redirect to Naver OAuth
        window.location.href = response.data.auth_url;
      } else {
        toast.error("네이버 로그인 URL을 가져오는데 실패했습니다");
      }
    } catch (error) {
      toast.error("네이버 로그인에 실패했습니다");
      console.error("Naver login error:", error);
    }
  };

  return (
    <div className="h-full flex flex-col items-center justify-center p-4 bg-muted/30">
      <div className="w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 rounded-full bg-primary flex items-center justify-center">
              <Timer className="w-7 h-7 text-primary-foreground" />
            </div>
            <h1 className="text-3xl">Focus Mate</h1>
          </div>
          <p className="text-muted-foreground">팀과 함께하는 포모도로 타이머</p>
        </div>

        {/* Auth Forms */}
        {view === "login" ? (
          <>
            <LoginForm
              onLogin={onLogin}
              onSwitchToSignup={() => setView("signup")}
            />
            <div className="mt-4">
              <div className="relative">
                <div className="absolute inset-0 flex items-center">
                  <span className="w-full border-t" />
                </div>
                <div className="relative flex justify-center text-xs uppercase">
                  <span className="bg-background px-2 text-muted-foreground">
                    또는
                  </span>
                </div>
              </div>
              <Button
                type="button"
                variant="outline"
                className="w-full mt-4 bg-[#03C75A] hover:bg-[#02B350] text-white border-[#03C75A]"
                onClick={handleNaverLogin}
                disabled={isLoading}
              >
                <svg
                  className="w-5 h-5 mr-2"
                  viewBox="0 0 24 24"
                  fill="currentColor"
                >
                  <path d="M16.273 12.845L7.376 0H0v24h7.726V11.156L16.624 24H24V0h-7.727v12.845z" />
                </svg>
                네이버로 로그인
              </Button>
            </div>
          </>
        ) : (
          <SignupForm
            onSignup={onSignup}
            onSwitchToLogin={() => setView("login")}
          />
        )}
      </div>
    </div>
  );
}
