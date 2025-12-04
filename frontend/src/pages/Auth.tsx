import React, { useState } from "react";
import { LoginForm } from "../components/login-form";
import { SignupForm } from "../components/signup-form";
import { Timer } from "lucide-react";

type AuthView = "login" | "signup";

interface AuthPageProps {
  onLogin: (email: string, password: string) => void;
  onSignup: (email: string, password: string, name: string) => void;
}

export function AuthPage({ onLogin, onSignup }: AuthPageProps) {
  const [view, setView] = useState<AuthView>("login");

  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4 bg-muted/30">
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
          <LoginForm
            onLogin={onLogin}
            onSwitchToSignup={() => setView("signup")}
          />
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
