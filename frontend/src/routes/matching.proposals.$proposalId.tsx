import React from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { ProposalDetailPage } from "../pages/ProposalDetail";
import { authService } from "../features/auth/services/authService";
import { matchingApi } from "../api/matching";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";

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

    try {
      // Fetch proposal with full pool details
      const proposal = await matchingApi.getProposal(params.proposalId, true);
      return { proposal };
    } catch (error: any) {
      if (error?.response?.status === 404) {
        toast.error("제안을 찾을 수 없습니다");
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

  const { data: proposal } = useQuery({
    queryKey: ["matching", "proposal", proposalId],
    queryFn: async () => {
      // Fetch proposal with full pool details
      const response = await matchingApi.getProposal(proposalId, true);
      return response;
    },
    initialData: initialData.proposal,
    staleTime: 1000 * 60, // 1 minute
    enabled: !!proposalId,
  });

  const respondMutation = useMutation({
    mutationFn: (action: "accept" | "reject") =>
      matchingApi.respondToProposal(proposalId, { action }),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["matching", "proposal", proposalId] });
      queryClient.invalidateQueries({ queryKey: ["matching", "proposals"] });
      queryClient.invalidateQueries({ queryKey: ["matching", "myPool"] });

      if (data.final_status === "matched") {
        toast.success("매칭이 성사되었습니다! 채팅방이 생성되었습니다.");
        // Navigate to matched group page
        navigate({ to: "/matching/matched/$proposalId", params: { proposalId } });
      } else if (data.final_status === "rejected") {
        toast.info("제안이 거절되었습니다");
      } else {
        toast.success("응답이 전송되었습니다");
      }
    },
    onError: (error: any) => {
      const message = error?.response?.data?.detail || "응답 전송에 실패했습니다";
      toast.error(message);
    },
  });

  if (!proposal) {
    return null;
  }

  // Determine which pool is the user's pool
  const myPool = useQuery({
    queryKey: ["matching", "myPool"],
    queryFn: () => matchingApi.getMyPool().catch(() => null),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const userPoolId = myPool.data?.pool_id;
  const isGroupA = proposal.pool_id_a === userPoolId;
  const isGroupB = proposal.pool_id_b === userPoolId;
  const userGroupStatus = isGroupA
    ? proposal.group_a_status
    : isGroupB
    ? proposal.group_b_status
    : null;
  const otherGroupStatus = isGroupA
    ? proposal.group_b_status
    : isGroupB
    ? proposal.group_a_status
    : null;

  const canRespond =
    (isGroupA || isGroupB) &&
    userGroupStatus === "pending" &&
    proposal.final_status === "pending";

  return (
    <PageTransition>
      <ProposalDetailPage
        proposal={proposal}
        currentUserId={user?.id}
        userPoolId={userPoolId}
        userGroupStatus={userGroupStatus}
        otherGroupStatus={otherGroupStatus}
        canRespond={canRespond}
        onAccept={() => respondMutation.mutate("accept")}
        onReject={() => respondMutation.mutate("reject")}
        onBack={() => navigate({ to: "/matching" })}
        isLoading={respondMutation.isPending}
      />
    </PageTransition>
  );
}


