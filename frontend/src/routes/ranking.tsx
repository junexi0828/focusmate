import React, { useState } from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { RankingPage } from "../pages/Ranking";
import { authService } from "../features/auth/services/authService";
import {
  rankingService,
  Team,
} from "../features/ranking/services/rankingService";
import { CreateTeamDialog } from "../features/ranking/components/CreateTeamDialog";
import { InviteMemberDialog } from "../features/ranking/components/InviteMemberDialog";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";
import { useNavigate } from "@tanstack/react-router";

export const Route = createFileRoute("/ranking")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  loader: async () => {
    const user = authService.getCurrentUser();
    if (!user?.id) {
      throw redirect({ to: "/login" });
    }
    const token = authService.getToken();
    if (!token) {
      throw redirect({ to: "/login" });
    }
    const response = await rankingService.getMyTeams();
    if (response.status === "error") {
      // Admin can proceed with empty data
      if (authService.isAdmin()) {
        return [];
      }
      // If authentication error, redirect to login
      if (
        response.error?.code === "UNAUTHORIZED" ||
        response.error?.message?.includes("authentication")
      ) {
        authService.logout();
        throw redirect({ to: "/login" });
      }
      throw new Error(response.error?.message || "Failed to load teams");
    }
    return response.data || [];
  },
  component: RankingComponent,
});

function RankingComponent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const user = authService.getCurrentUser();
  const initialTeams = Route.useLoaderData();
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isInviteDialogOpen, setIsInviteDialogOpen] = useState(false);
  const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);

  const { data: teams = initialTeams, isLoading } = useQuery({
    queryKey: ["ranking", "teams", user?.id],
    queryFn: async () => {
      const response = await rankingService.getMyTeams();
      if (response.status === "error") {
        throw new Error(response.error?.message || "Failed to load teams");
      }
      return response.data || [];
    },
    initialData: initialTeams,
    staleTime: 1000 * 30, // 30 seconds
  });

  const createTeamMutation = useMutation({
    mutationFn: (data: Parameters<typeof rankingService.createTeam>[0]) =>
      rankingService.createTeam(data),
    onSuccess: (response) => {
      if (response.status === "success") {
        queryClient.invalidateQueries({ queryKey: ["ranking", "teams"] });
        toast.success("팀이 생성되었습니다!");
        setIsCreateDialogOpen(false);
      } else {
        toast.error(response.error?.message || "팀 생성에 실패했습니다");
      }
    },
    onError: (error) => {
      toast.error(
        error instanceof Error ? error.message : "팀 생성에 실패했습니다"
      );
    },
  });

  const inviteMemberMutation = useMutation({
    mutationFn: ({ teamId, email }: { teamId: string; email: string }) =>
      rankingService.inviteMember(teamId, { email }),
    onSuccess: (response) => {
      if (response.status === "success") {
        queryClient.invalidateQueries({ queryKey: ["ranking", "teams"] });
        toast.success("초대가 발송되었습니다!");
        setIsInviteDialogOpen(false);
        setSelectedTeam(null);
      } else {
        toast.error(response.error?.message || "초대에 실패했습니다");
      }
    },
    onError: (error) => {
      toast.error(
        error instanceof Error ? error.message : "초대에 실패했습니다"
      );
    },
  });

  const leaveTeamMutation = useMutation({
    mutationFn: (teamId: string) => rankingService.leaveTeam(teamId),
    onSuccess: (response) => {
      if (response.status === "success") {
        queryClient.invalidateQueries({ queryKey: ["ranking", "teams"] });
        toast.success("팀에서 탈퇴했습니다");
      } else {
        toast.error(response.error?.message || "팀 탈퇴에 실패했습니다");
      }
    },
    onError: (error) => {
      toast.error(
        error instanceof Error ? error.message : "팀 탈퇴에 실패했습니다"
      );
    },
  });

  const handleCreateTeam = () => {
    setIsCreateDialogOpen(true);
  };

  const handleSubmitTeam = async (
    data: Parameters<typeof rankingService.createTeam>[0]
  ) => {
    await createTeamMutation.mutateAsync(data);
  };

  const handleInviteMember = (teamId: string) => {
    const team = teams.find((t) => t.team_id === teamId);
    setSelectedTeam(team || null);
    setIsInviteDialogOpen(true);
  };

  const handleSubmitInvite = async (email: string) => {
    if (!selectedTeam) return;
    await inviteMemberMutation.mutateAsync({
      teamId: selectedTeam.team_id,
      email,
    });
  };

  const handleViewTeam = (teamId: string) => {
    // TODO: Navigate to team detail page
    toast.info(`팀 상세 페이지: ${teamId}`);
  };

  const handleLeaveTeam = async (teamId: string) => {
    if (
      !confirm("정말로 팀에서 탈퇴하시겠습니까? 이 작업은 되돌릴 수 없습니다.")
    ) {
      return;
    }
    await leaveTeamMutation.mutateAsync(teamId);
  };

  const handleManageTeam = (teamId: string) => {
    // TODO: Navigate to team management page
    toast.info(`팀 관리 페이지: ${teamId}`);
  };

  if (isLoading && !teams.length) {
    return (
      <div className="min-h-screen bg-muted/30 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <PageTransition>
      <RankingPage
        teams={teams}
        currentUserId={user?.id}
        onCreateTeam={handleCreateTeam}
        onViewTeam={handleViewTeam}
        onInviteMember={handleInviteMember}
        onLeaveTeam={handleLeaveTeam}
        onManageTeam={handleManageTeam}
      />
      <CreateTeamDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onSubmit={handleSubmitTeam}
      />
      <InviteMemberDialog
        open={isInviteDialogOpen}
        onOpenChange={setIsInviteDialogOpen}
        onSubmit={handleSubmitInvite}
        inviteCode={selectedTeam?.invite_code || null}
      />
    </PageTransition>
  );
}
