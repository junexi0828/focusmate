import React from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { MatchedGroupPage } from "../pages/MatchedGroup";
import { authService } from "../features/auth/services/authService";
import { matchingService } from "../features/matching/services/matchingService";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";
import { chatService } from "../features/chat/services/chatService";

export const Route = createFileRoute("/matching/matched/$proposalId")({
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
      const res = await matchingService.getProposal(params.proposalId);
      if (res.status === 'error') throw res.error;
      const proposal = res.data;

      // Check if proposal exists and is valid
      if (!proposal) {
        throw new Error("제안을 찾을 수 없습니다");
      }

      if (proposal.final_status !== "matched" || !proposal.chat_room_id) {
        toast.error("매칭이 완료되지 않았거나 채팅방이 생성되지 않았습니다");
        throw redirect({ to: "/matching" });
      }

      // Get chat room and members
      const [chatRoom, members] = await Promise.all([
        chatService.getRoom(proposal.chat_room_id).then(res => res.data),
        chatService.getRoomMembers(proposal.chat_room_id).then(res => res.data || []).catch(() => []),
      ]);

      return { proposal, chatRoom, members };
    } catch (error: any) {
      if (error?.response?.status === 404) {
        toast.error("제안을 찾을 수 없습니다");
        throw redirect({ to: "/matching" });
      }
      throw error;
    }
  },
  component: MatchedGroupComponent,
});

function MatchedGroupComponent() {
  const navigate = useNavigate();
  const { proposalId } = Route.useParams();
  const initialData = Route.useLoaderData();
  const user = authService.getCurrentUser();

  const { data: proposal } = useQuery({
    queryKey: ["matching", "proposal", proposalId],
    queryFn: async () => {
      const response = await matchingService.getProposal(proposalId);
      if (response.status === 'error') throw response.error;
      return response.data;
    },
    initialData: initialData.proposal,
    staleTime: 1000 * 60, // 1 minute
    enabled: !!proposalId,
  });

  const { data: chatRoom } = useQuery({
    queryKey: ["chat", "room", proposal?.chat_room_id],
    queryFn: async () => {
      if (!proposal?.chat_room_id) return null;
      const res = await chatService.getRoom(proposal.chat_room_id);
      return res.data;
    },
    initialData: initialData.chatRoom,
    staleTime: 1000 * 60, // 1 minute
    enabled: !!proposal?.chat_room_id,
  });

  const { data: members = [] } = useQuery({
    queryKey: ["chat", "room", proposal?.chat_room_id, "members"],
    queryFn: async () => {
      if (!proposal?.chat_room_id) return [];
      const res = await chatService.getRoomMembers(proposal.chat_room_id);
      return res.data || [];
    },
    initialData: initialData.members,
    staleTime: 1000 * 60, // 1 minute
    enabled: !!proposal?.chat_room_id,
  });

  if (!proposal || !chatRoom) {
    return null;
  }

  // Determine which pool is the user's pool
  const myPool = useQuery({
    queryKey: ["matching", "myPool"],
    queryFn: async () => {
      const res = await matchingService.getMyPool();
      return res.data;
    },
    staleTime: 1000 * 60 * 5, // 5 minutes
  });

  const userPoolId = myPool.data?.pool_id;
  const isGroupA = proposal.pool_id_a === userPoolId;

  return (
    <PageTransition>
      <MatchedGroupPage
        proposal={proposal}
        chatRoom={chatRoom}
        members={members}
        currentUserId={user?.id}
        userPoolId={userPoolId}
        isGroupA={isGroupA}
        onBack={() => navigate({ to: "/matching" })}
        onEnterChat={() => {
          if (proposal.chat_room_id) {
            navigate({ to: `/chat/${proposal.chat_room_id}` });
          }
        }}
      />
    </PageTransition>
  );
}

