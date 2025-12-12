import React from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { ProfilePage } from "../pages/Profile";
import { authService } from "../features/auth/services/authService";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import {
  UserResponse,
  ProfileUpdateRequest,
} from "../features/auth/services/authService";

export const Route = createFileRoute("/profile")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  component: ProfileComponent,
});

function ProfileComponent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const user = authService.getCurrentUser();

  const updateMutation = useMutation({
    mutationFn: (data: ProfileUpdateRequest) => {
      if (!user) throw new Error("User not authenticated");
      return authService.updateProfile(user.id, data);
    },
    onSuccess: (response) => {
      if (response.status === "success") {
        queryClient.invalidateQueries();
        toast.success("프로필이 업데이트되었습니다");
      } else {
        toast.error(
          response.error?.message || "프로필 업데이트에 실패했습니다"
        );
      }
    },
  });

  const handleUpdateProfile = (updates: Partial<UserResponse>) => {
    const updateData: ProfileUpdateRequest = {};
    if (updates.username) updateData.username = updates.username;
    if (updates.bio !== undefined) updateData.bio = updates.bio;
    updateMutation.mutate(updateData);
  };

  const handleLogout = () => {
    authService.logout();
    queryClient.clear();
    navigate({ to: "/" });
    toast.success("로그아웃되었습니다");
  };

  if (!user) {
    return null;
  }

  // Convert UserResponse to User type for ProfilePage
  const profileUser = {
    id: user.id,
    email: user.email,
    name: user.username,
    bio: user.bio,
    createdAt: new Date(user.created_at),
    totalFocusTime: user.total_focus_time,
    totalSessions: user.total_sessions,
  };

  return (
    <PageTransition>
      <ProfilePage
        user={profileUser}
        onUpdateProfile={handleUpdateProfile}
        onLogout={handleLogout}
      />
    </PageTransition>
  );
}
