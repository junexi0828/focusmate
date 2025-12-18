import React from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { MatchingPoolDetailPage } from "../pages/MatchingPoolDetail";
import { authService } from "../features/auth/services/authService";
import { matchingApi } from "../api/matching";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";

export const Route = createFileRoute("/matching/pools/$poolId")({
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
      const pool = await matchingApi.getPool(params.poolId);
      return { pool };
    } catch (error: any) {
      if (error?.response?.status === 404) {
        toast.error("매칭 풀을 찾을 수 없습니다");
        throw redirect({ to: "/matching" });
      }
      throw error;
    }
  },
  component: MatchingPoolDetailComponent,
});

function MatchingPoolDetailComponent() {
  const navigate = useNavigate();
  const { poolId } = Route.useParams();
  const initialData = Route.useLoaderData();
  const user = authService.getCurrentUser();

  const { data: pool } = useQuery({
    queryKey: ["matching", "pool", poolId],
    queryFn: async () => {
      const response = await matchingApi.getPool(poolId);
      return response;
    },
    initialData: initialData.pool,
    staleTime: 1000 * 60, // 1 minute
    enabled: !!poolId,
  });

  if (!pool) {
    return null;
  }

  return (
    <PageTransition>
      <MatchingPoolDetailPage
        pool={pool}
        currentUserId={user?.id}
        onBack={() => navigate({ to: "/matching" })}
      />
    </PageTransition>
  );
}


