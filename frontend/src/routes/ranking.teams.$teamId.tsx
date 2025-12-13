import React from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { TeamDetailPage } from "../pages/TeamDetail";
import { authService } from "../features/auth/services/authService";
import { rankingService, Team, TeamMember, TeamStats } from "../features/ranking/services/rankingService";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";

export const Route = createFileRoute("/ranking/teams/$teamId")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  loader: async ({ params }) => {
    const user = authService.getCurrentUser();
    if (!user?.id) {
      throw redirect({ to: "/login" });
    }

    const [teamResponse, membersResponse, statsResponse] = await Promise.all([
      rankingService.getTeam(params.teamId),
      rankingService.getTeamMembers(params.teamId),
      rankingService.getTeamStats(params.teamId),
    ]);

    if (teamResponse.status === "error") {
      if (teamResponse.error?.code === "NOT_FOUND") {
        throw redirect({ to: "/ranking" });
      }
      throw new Error(teamResponse.error?.message || "Failed to load team");
    }

    return {
      team: teamResponse.data,
      members: membersResponse.status === "success" ? membersResponse.data : [],
      stats: statsResponse.status === "success" ? statsResponse.data : null,
    };
  },
  component: TeamDetailComponent,
});

function TeamDetailComponent() {
  const navigate = useNavigate();
  const { teamId } = Route.useParams();
  const initialData = Route.useLoaderData();
  const user = authService.getCurrentUser();

  const { data: team } = useQuery({
    queryKey: ["ranking", "team", teamId],
    queryFn: async () => {
      const response = await rankingService.getTeam(teamId);
      return response.status === "success" ? response.data : null;
    },
    initialData: initialData.team,
    enabled: !!teamId,
  });

  const { data: members = [] } = useQuery({
    queryKey: ["ranking", "team", teamId, "members"],
    queryFn: async () => {
      const response = await rankingService.getTeamMembers(teamId);
      return response.status === "success" ? response.data : [];
    },
    initialData: initialData.members,
    enabled: !!teamId,
  });

  const { data: stats } = useQuery({
    queryKey: ["ranking", "team", teamId, "stats"],
    queryFn: async () => {
      const response = await rankingService.getTeamStats(teamId);
      return response.status === "success" ? response.data : null;
    },
    initialData: initialData.stats,
    enabled: !!teamId,
  });

  if (!team) {
    return null;
  }

  return (
    <PageTransition>
      <TeamDetailPage
        team={team}
        members={members}
        stats={stats}
        currentUserId={user?.id}
        onBack={() => navigate({ to: "/ranking" })}
      />
    </PageTransition>
  );
}

