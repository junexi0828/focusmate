import React, { useState } from "react";
import { createFileRoute, redirect } from "@tanstack/react-router";
import { useQuery } from "@tanstack/react-query";
import { HallOfFamePage } from "../pages/HallOfFame";
import { authService } from "../features/auth/services/authService";
import { rankingService, HallOfFameResponse } from "../features/ranking/services/rankingService";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";

export const Route = createFileRoute("/ranking/hall-of-fame")({
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

    const response = await rankingService.getHallOfFame("all");
    if (response.status === "error") {
      if (response.error?.code === "UNAUTHORIZED") {
        authService.logout();
        throw redirect({ to: "/login" });
      }
      // Admin can proceed with empty data
      if (authService.isAdmin()) {
        return {
          period: "all",
          total_teams: 0,
          teams: [],
          top_focus_teams: [],
          top_game_teams: [],
        };
      }
      throw new Error(response.error?.message || "Failed to load Hall of Fame");
    }

    return response.data;
  },
  component: HallOfFameComponent,
});

function HallOfFameComponent() {
  const initialData = Route.useLoaderData();
  const [period, setPeriod] = useState<"weekly" | "monthly" | "all">("all");

  const { data: hallOfFame, isLoading } = useQuery({
    queryKey: ["ranking", "hall-of-fame", period],
    queryFn: async () => {
      const response = await rankingService.getHallOfFame(period);
      return response.status === "success" ? response.data : null;
    },
    initialData: period === "all" ? initialData : undefined,
    enabled: true,
  });

  return (
    <PageTransition>
      <HallOfFamePage
        data={hallOfFame}
        period={period}
        onPeriodChange={setPeriod}
        isLoading={isLoading}
      />
    </PageTransition>
  );
}

