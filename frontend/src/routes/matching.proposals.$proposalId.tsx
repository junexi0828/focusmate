import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ProposalDetailPage } from "../pages/ProposalDetail";
import { authService } from "../features/auth/services/authService";
import { matchingApi } from "../api/matching";
import { PageTransition } from "../components/PageTransition";
import { ReportDialog } from "../components/ReportDialog";
import { toast } from "sonner";
import { useState } from "react";
import type { MatchingProposal } from "../types/matching";

export const Route = createFileRoute("/matching/proposals/$proposalId")({
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

    // 데모 모드 체크: proposal_id가 "demo-"로 시작하면 데모 데이터 사용
    if (params.proposalId.startsWith("demo-")) {
      // 데모 모드에서는 API 호출하지 않고 null 반환 (컴포넌트에서 처리)
      return { proposal: null, isDemo: true };
    }

    try {
      // Fetch proposal with full pool details
      const proposal = await matchingApi.getProposal(params.proposalId, true);
      return { proposal, isDemo: false };
    } catch (error: any) {
      if (error?.response?.status === 404) {
        toast.error("제안을 찾을 수 없습니다");
        throw redirect({ to: "/matching" });
      }
      // 422 에러도 처리 (UUID 형식이 아닌 경우)
      if (error?.response?.status === 422) {
        toast.error("유효하지 않은 제안 ID입니다");
        throw redirect({ to: "/matching" });
      }
      throw error;
    }
  },
  component: ProposalDetailComponent,
});

function ProposalDetailComponent() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { proposalId } = Route.useParams();
  const initialData = Route.useLoaderData();
  const user = authService.getCurrentUser();
  const isDemo = initialData.isDemo || proposalId.startsWith("demo-");
  const [isReportDialogOpen, setIsReportDialogOpen] = useState(false);

  // 데모 모드: 쿼리 캐시에서 데모 proposal 찾기
  const demoProposals =
    queryClient.getQueryData<MatchingProposal[]>(["matching", "proposals"]) ||
    [];
  const demoProposal = isDemo
    ? demoProposals.find((p) => p.proposal_id === proposalId)
    : null;

  const { data: proposal } = useQuery({
    queryKey: ["matching", "proposal", proposalId],
    queryFn: async () => {
      // 데모 모드면 API 호출하지 않음
      if (isDemo) {
        return demoProposal || null;
      }
      // Fetch proposal with full pool details
      const response = await matchingApi.getProposal(proposalId, true);
      return response;
    },
    initialData: isDemo ? demoProposal : initialData.proposal,
    staleTime: 1000 * 60, // 1 minute
    enabled: !!proposalId && !isDemo, // 데모 모드에서는 쿼리 비활성화
  });

  // 데모 모드에서는 demoProposal 사용
  const displayProposal = isDemo ? demoProposal : proposal;

  // 데모 모드: 제안 응답 처리
  const handleDemoRespond = (action: "accept" | "reject") => {
    if (!demoProposal) return;

    const updatedProposal: MatchingProposal = {
      ...demoProposal,
      group_a_status: action === "accept" ? "accepted" : "rejected",
      final_status: action === "accept" ? "matched" : "rejected",
      matched_at: action === "accept" ? new Date().toISOString() : null,
      chat_room_id: action === "accept" ? `demo-chat-${Date.now()}` : null,
    };

    // 쿼리 캐시 업데이트
    queryClient.setQueryData<MatchingProposal[]>(
      ["matching", "proposals"],
      (old = []) =>
        old.map((p) => (p.proposal_id === proposalId ? updatedProposal : p))
    );
    queryClient.setQueryData<MatchingProposal>(
      ["matching", "proposal", proposalId],
      updatedProposal
    );

    // 통계 쿼리 캐시도 무효화하여 통계 페이지에서 업데이트된 데이터를 볼 수 있도록 함
    queryClient.invalidateQueries({
      queryKey: ["matching", "comprehensive-stats"],
    });

    if (action === "accept") {
      toast.success("매칭이 성사되었습니다! 데모 채팅방이 생성되었습니다.");
    } else {
      toast.info("제안이 거절되었습니다");
    }
  };

  const respondMutation = useMutation({
    mutationFn: (action: "accept" | "reject") => {
      if (isDemo) {
        // 데모 모드는 동기적으로 처리
        handleDemoRespond(action);
        return Promise.resolve(demoProposal!);
      }
      return matchingApi.respondToProposal(proposalId, { action });
    },
    onSuccess: (data) => {
      if (!isDemo) {
        queryClient.invalidateQueries({
          queryKey: ["matching", "proposal", proposalId],
        });
        queryClient.invalidateQueries({ queryKey: ["matching", "proposals"] });
        queryClient.invalidateQueries({ queryKey: ["matching", "myPool"] });
      }

      if (data?.final_status === "matched") {
        if (!isDemo) {
          toast.success("매칭이 성사되었습니다! 채팅방이 생성되었습니다.");
          navigate({
            to: "/matching/matched/$proposalId",
            params: { proposalId },
          });
        }
      } else if (data?.final_status === "rejected") {
        if (!isDemo) {
          toast.info("제안이 거절되었습니다");
        }
      } else {
        if (!isDemo) {
          toast.success("응답이 전송되었습니다");
        }
      }
    },
    onError: (error: any) => {
      const message =
        error?.response?.data?.detail || "응답 전송에 실패했습니다";
      toast.error(message);
    },
  });

  if (!displayProposal) {
    // 데모 모드에서 proposal을 찾을 수 없으면 매칭 페이지로 리다이렉트
    if (isDemo) {
      toast.error("데모 제안을 찾을 수 없습니다");
      navigate({ to: "/matching" });
      return null;
    }
    return null;
  }

  // Determine which pool is the user's pool
  const myPool = useQuery({
    queryKey: ["matching", "myPool"],
    queryFn: () => matchingApi.getMyPool().catch(() => null),
    staleTime: 1000 * 60 * 5, // 5 minutes
    enabled: !isDemo, // 데모 모드에서는 API 호출 안 함
  });

  // 데모 모드: 데모 풀 ID 사용
  const demoPoolId = isDemo ? displayProposal.pool_id_a : null;
  const userPoolId = isDemo ? demoPoolId : myPool.data?.pool_id;
  const isGroupA = displayProposal.pool_id_a === userPoolId;
  const isGroupB = displayProposal.pool_id_b === userPoolId;
  const userGroupStatus = isGroupA
    ? displayProposal.group_a_status
    : isGroupB
      ? displayProposal.group_b_status
      : null;
  const otherGroupStatus = isGroupA
    ? displayProposal.group_b_status
    : isGroupB
      ? displayProposal.group_a_status
      : null;

  const canRespond =
    (isGroupA || isGroupB) &&
    userGroupStatus === "pending" &&
    displayProposal.final_status === "pending";

  return (
    <PageTransition>
      {isDemo && (
        <div className="mb-4 p-3 bg-pink-50 dark:bg-pink-950/20 border border-pink-200 dark:border-pink-800 rounded-lg">
          <p className="text-sm text-pink-700 dark:text-pink-300">
            🎮 데모 모드: 이 제안은 실제 데이터베이스와 연동되지 않습니다.
          </p>
        </div>
      )}
      <ProposalDetailPage
        proposal={displayProposal}
        currentUserId={user?.id}
        userPoolId={userPoolId || undefined}
        userGroupStatus={userGroupStatus}
        otherGroupStatus={otherGroupStatus}
        canRespond={canRespond}
        onAccept={() => respondMutation.mutate("accept")}
        onReject={() => respondMutation.mutate("reject")}
        onBack={() => navigate({ to: "/matching" })}
        onReport={() => setIsReportDialogOpen(true)}
        isLoading={respondMutation.isPending}
      />
      <ReportDialog
        open={isReportDialogOpen}
        onOpenChange={setIsReportDialogOpen}
        proposalId={!isDemo ? proposalId : undefined}
        poolId={displayProposal?.pool_id_a || displayProposal?.pool_id_b}
        reportedUserId={
          displayProposal?.pool_a?.creator_id ||
          displayProposal?.pool_b?.creator_id
        }
      />
    </PageTransition>
  );
}
