import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  TeamManagementPage,
  TeamManagementFormValues,
} from "../pages/TeamManagement";
import { authService } from "../features/auth/services/authService";
import {
  rankingService,
  TeamUpdateRequest,
} from "../features/ranking/services/rankingService";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";
import { Button } from "../components/ui/button";

export const Route = createFileRoute("/ranking/teams/$teamId/manage")({
  beforeLoad: () => {
    const user = authService.getCurrentUser();
    if (!user) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  loader: async ({ params }) => {
    const [teamResponse, membersResponse] = await Promise.all([
      rankingService.getTeam(params.teamId),
      rankingService.getTeamMembers(params.teamId),
    ]);

    if (teamResponse.status === "error" || !teamResponse.data) {
      throw new Error("팀 정보를 불러오지 못했습니다.");
    }

    const user = authService.getCurrentUser();
    if (teamResponse.data.leader_id !== user?.id) {
      toast.error("팀 리더만 접근할 수 있는 페이지입니다.");
      throw redirect({
        to: "/ranking/teams/$teamId",
        params: { teamId: params.teamId },
      });
    }

    return {
      team: teamResponse.data,
      members: membersResponse.status === "success" ? membersResponse.data : [],
    };
  },
  component: TeamManageComponent,
  pendingComponent: () => (
    <PageTransition>
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    </PageTransition>
  ),
  errorComponent: ({ error }) => (
    <PageTransition>
      <div className="container mx-auto px-4 py-12 text-center">
        <h2 className="text-2xl font-bold text-destructive mb-4">오류 발생</h2>
        <p className="text-muted-foreground mb-6">{error?.message}</p>
        <Button onClick={() => (window.location.href = "/ranking")}>
          랭킹으로 돌아가기
        </Button>
      </div>
    </PageTransition>
  ),
});

function TeamManageComponent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { teamId } = Route.useParams();
  const initialData = Route.useLoaderData();
  const user = authService.getCurrentUser();

  const { data: team, isLoading: isLoadingTeam } = useQuery({
    queryKey: ["ranking", "team", teamId],
    queryFn: async () => {
      const response = await rankingService.getTeam(teamId);
      return response.status === "success" ? response.data : null;
    },
    initialData: initialData.team,
  });

  const { data: members, isLoading: isLoadingMembers } = useQuery({
    queryKey: ["ranking", "team", teamId, "members"],
    queryFn: async () => {
      const response = await rankingService.getTeamMembers(teamId);
      return response.status === "success" ? response.data : [];
    },
    initialData: initialData.members,
  });

  const updateTeamMutation = useMutation({
    mutationFn: (values: TeamManagementFormValues) => {
      const dataToUpdate: TeamUpdateRequest = {
        team_name: values.team_name,
        mini_game_enabled: values.mini_game_enabled,
      };
      return rankingService.updateTeam(teamId, dataToUpdate);
    },
    onSuccess: (response) => {
      if (response.status === "success") {
        toast.success("팀 정보가 성공적으로 업데이트되었습니다.");
        queryClient.invalidateQueries({
          queryKey: ["ranking", "team", teamId],
        });
        queryClient.invalidateQueries({ queryKey: ["my-teams"] });
      } else {
        toast.error(
          response.error?.message || "팀 정보 업데이트에 실패했습니다."
        );
      }
    },
    onError: (error) => {
      toast.error(`오류 발생: ${error.message}`);
    },
  });

  const removeMemberMutation = useMutation({
    mutationFn: (userId: string) => rankingService.removeMember(teamId, userId),
    onSuccess: (response) => {
      if (response.status === "success") {
        toast.success(`멤버를 팀에서 내보냈습니다.`);
        queryClient.invalidateQueries({
          queryKey: ["ranking", "team", teamId, "members"],
        });
      } else {
        toast.error(
          response.error?.message || "멤버를 내보내는 데 실패했습니다."
        );
      }
    },
    onError: (error) => {
      toast.error(`오류 발생: ${error.message}`);
    },
  });

  const deleteTeamMutation = useMutation({
    mutationFn: () => rankingService.deleteTeam(teamId),
    onSuccess: (response) => {
      if (response.status === "success") {
        toast.success("팀이 성공적으로 삭제되었습니다.");
        queryClient.invalidateQueries({ queryKey: ["my-teams"] });
        navigate({ to: "/ranking" });
      } else {
        toast.error(response.error?.message || "팀 삭제에 실패했습니다.");
      }
    },
    onError: (error) => {
      toast.error(`오류 발생: ${error.message}`);
    },
  });

  const handleUpdateTeam = (values: TeamManagementFormValues) => {
    updateTeamMutation.mutate(values);
  };

  const handleRemoveMember = (userId: string) => {
    if (window.confirm(`정말로 이 멤버를 팀에서 내보내시겠습니까?`)) {
      removeMemberMutation.mutate(userId);
    }
  };

  const handleDeleteTeam = () => {
    if (
      window.confirm(
        `정말로 이 팀을 삭제하시겠습니까? 이 작업은 되돌릴 수 없으며, 모든 팀 데이터가 영구적으로 사라집니다.`
      )
    ) {
      deleteTeamMutation.mutate();
    }
  };

  const isLoading = isLoadingTeam || isLoadingMembers;

  if (isLoading && !team) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (!team) {
    return <div>팀 정보를 찾을 수 없습니다.</div>;
  }

  return (
    <PageTransition>
      <TeamManagementPage
        team={team}
        members={members || []}
        currentUserId={user?.id}
        onBack={() =>
          navigate({ to: "/ranking/teams/$teamId", params: { teamId } })
        }
        onUpdateTeam={handleUpdateTeam}
        onRemoveMember={handleRemoveMember}
        onDeleteTeam={handleDeleteTeam}
      />
    </PageTransition>
  );
}
