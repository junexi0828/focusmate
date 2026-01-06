import React from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { MatchingPoolDetailPage } from "../pages/MatchingPoolDetail";
import { authService } from "../features/auth/services/authService";
import { matchingService } from "../features/matching/services/matchingService";
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
      const res = await matchingService.getPool(params.poolId);
      if (res.status === 'error') throw res.error;
      const pool = res.data;
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
      const response = await matchingService.getPool(poolId);
      if (response.status === 'error') throw response.error;
      return response.data;
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


