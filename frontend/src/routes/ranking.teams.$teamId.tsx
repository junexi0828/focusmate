import React from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { TeamDetailPage } from "../pages/TeamDetail";
import { authService } from "../features/auth/services/authService";
import { rankingService, Team, TeamMember, TeamStats } from "../features/ranking/services/rankingService";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import { Users, ArrowLeft } from "lucide-react";

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

    try {
      const [teamResponse, membersResponse, statsResponse] = await Promise.all([
        rankingService.getTeam(params.teamId),
        rankingService.getTeamMembers(params.teamId),
        rankingService.getTeamStats(params.teamId),
      ]);

      if (teamResponse.status === "error") {
        console.error("Team not found:", teamResponse.error);
        return {
          team: null,
          members: [],
          stats: null,
        };
      }

      return {
        team: teamResponse.data,
        members: membersResponse.status === "success" ? membersResponse.data : [],
        stats: statsResponse.status === "success" ? statsResponse.data : null,
      };
    } catch (error) {
      console.error("Failed to load team:", error);
      return {
        team: null,
        members: [],
        stats: null,
      };
    }
  },
  component: TeamDetailComponent,
  pendingComponent: () => (
    <PageTransition>
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">팀 정보를 불러오는 중...</p>
        </div>
      </div>
    </PageTransition>
  ),
  errorComponent: ({ error }) => (
    <PageTransition>
      <div className="container mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold text-destructive mb-4">오류가 발생했습니다</h2>
        <p className="text-muted-foreground mb-6">{error?.message || "팀 정보를 불러올 수 없습니다"}</p>
        <Button onClick={() => window.location.href = "/ranking"}>랭킹으로 돌아가기</Button>
      </div>
    </PageTransition>
  ),
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
    staleTime: 1000 * 60, // 1 minute
    enabled: !!teamId,
  });

  const { data: members = [] } = useQuery({
    queryKey: ["ranking", "team", teamId, "members"],
    queryFn: async () => {
      const response = await rankingService.getTeamMembers(teamId);
      return response.status === "success" ? response.data : [];
    },
    initialData: initialData.members,
    staleTime: 1000 * 60, // 1 minute
    enabled: !!teamId,
  });

  const { data: stats } = useQuery({
    queryKey: ["ranking", "team", teamId, "stats"],
    queryFn: async () => {
      const response = await rankingService.getTeamStats(teamId);
      return response.status === "success" ? response.data : null;
    },
    initialData: initialData.stats,
    staleTime: 1000 * 60, // 1 minute
    enabled: !!teamId,
  });

  if (!team) {
    return (
      <PageTransition>
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-2xl mx-auto text-center">
            <div className="bg-card rounded-lg p-8 border">
              <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-muted flex items-center justify-center">
                <Users className="w-8 h-8 text-muted-foreground" />
              </div>
              <h2 className="text-2xl font-bold mb-2">팀을 찾을 수 없습니다</h2>
              <p className="text-muted-foreground mb-6">
                존재하지 않거나 삭제된 팀입니다.
              </p>
              <Button onClick={() => navigate({ to: "/ranking" })}>
                <ArrowLeft className="w-4 h-4 mr-2" />
                랭킹으로 돌아가기
              </Button>
            </div>
          </div>
        </div>
      </PageTransition>
    );
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

