import React from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { ProfilePage } from "../pages/Profile";
import { authService } from "../features/auth/services/authService";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";
import { useMutation, useQueryClient, useQuery } from "@tanstack/react-query";
import {
  UserResponse,
  ProfileUpdateRequest,
} from "../features/auth/services/authService";
import { achievementService } from "../features/achievements/services/achievementService";
import { communityService } from "../features/community/services/communityService";

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

  // Fetch user profile
  const { data: profileData } = useQuery({
    queryKey: ["profile", user?.id],
    queryFn: async () => {
      if (!user?.id) return null;
      const response = await authService.getProfile(user.id);
      return response.status === "success" ? response.data : null;
    },
    enabled: !!user?.id,
  });

  // Fetch achievements
  const { data: achievements = [] } = useQuery({
    queryKey: ["achievements", "progress", user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      const response = await achievementService.getUserAchievementProgress(user.id);
      return response.status === "success" ? response.data : [];
    },
    enabled: !!user?.id,
  });

  // Fetch user posts
  const { data: userPosts = [] } = useQuery({
    queryKey: ["community", "posts", "user", user?.id],
    queryFn: async () => {
      if (!user?.id) return [];
      const response = await communityService.getPosts({ user_id: user.id, limit: 10 });
      return response.status === "success" ? response.data?.posts || [] : [];
    },
    enabled: !!user?.id,
  });

  const updateMutation = useMutation({
    mutationFn: (data: ProfileUpdateRequest) => {
      if (!user) throw new Error("User not authenticated");
      return authService.updateProfile(user.id, data);
    },
    onSuccess: (response) => {
      if (response.status === "success") {
        queryClient.invalidateQueries({ queryKey: ["profile", user?.id] });
        queryClient.invalidateQueries({ queryKey: ["achievements"] });
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

  // Use profileData if available, otherwise use cached user
  const displayUser = profileData || user;

  // Convert UserResponse to User type for ProfilePage
  const profileUser = {
    id: displayUser.id,
    email: displayUser.email,
    name: displayUser.username,
    bio: displayUser.bio,
    createdAt: new Date(displayUser.created_at),
    totalFocusTime: displayUser.total_focus_time,
    totalSessions: displayUser.total_sessions,
  };

  return (
    <PageTransition>
      <ProfilePage
        user={profileUser}
        achievements={achievements}
        userPosts={userPosts}
        onUpdateProfile={handleUpdateProfile}
        onLogout={handleLogout}
      />
    </PageTransition>
  );
}
