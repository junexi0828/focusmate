import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button-enhanced";
import { Badge } from "../components/ui/badge";
import {
  Trophy,
  Medal,
  Clock,
  Target,
  Gamepad2,
  TrendingUp,
  ArrowRight,
} from "lucide-react";
import {
  HallOfFameResponse,
  HallOfFameEntry,
} from "../features/ranking/services/rankingService";
import { useNavigate } from "@tanstack/react-router";
import { format } from "date-fns";
import { ko } from "date-fns/locale";

interface HallOfFamePageProps {
  data: HallOfFameResponse | null;
  period: "weekly" | "monthly" | "all";
  onPeriodChange: (period: "weekly" | "monthly" | "all") => void;
  isLoading: boolean;
}

export function HallOfFamePage({
  data,
  period,
  onPeriodChange,
  isLoading,
}: HallOfFamePageProps) {
  const navigate = useNavigate();

  const periodLabels: Record<string, string> = {
    weekly: "주간",
    monthly: "월간",
    all: "전체",
  };

  const teamTypeLabels: Record<string, string> = {
    general: "일반",
    department: "학과",
    lab: "연구실",
    club: "동아리",
  };

  const handleTeamClick = (teamId: string) => {
    navigate({ to: `/ranking/teams/${teamId}` });
  };

  const getRankIcon = (rank: number) => {
    if (rank === 1) {
      return <Trophy className="w-6 h-6 text-yellow-500" />;
    } else if (rank === 2) {
      return <Medal className="w-6 h-6 text-gray-400" />;
    } else if (rank === 3) {
      return <Medal className="w-6 h-6 text-orange-500" />;
    }
    return null;
  };

  const getRankBadgeColor = (rank: number) => {
    if (rank === 1) {
      return "bg-yellow-500 text-white";
    } else if (rank === 2) {
      return "bg-gray-400 text-white";
    } else if (rank === 3) {
      return "bg-orange-500 text-white";
    }
    return "bg-muted text-muted-foreground";
  };

  return (
    <div className="min-h-screen bg-muted/30">
      <div className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2 flex items-center gap-2">
            <Trophy className="w-8 h-8 text-yellow-500" />
            Hall of Fame
          </h1>
          <p className="text-muted-foreground">
            최고의 집중력과 성과를 보여준 팀들을 확인하세요
          </p>
        </div>

        {/* Period Filter */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>기간 선택</CardTitle>
            <CardDescription>랭킹 기간을 선택하세요</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex gap-2">
              <Button
                variant={period === "weekly" ? "default" : "outline"}
                onClick={() => onPeriodChange("weekly")}
              >
                주간
              </Button>
              <Button
                variant={period === "monthly" ? "default" : "outline"}
                onClick={() => onPeriodChange("monthly")}
              >
                월간
              </Button>
              <Button
                variant={period === "all" ? "default" : "outline"}
                onClick={() => onPeriodChange("all")}
              >
                전체
              </Button>
            </div>
          </CardContent>
        </Card>

        {/* Leaderboard */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  {periodLabels[period]} 랭킹
                </CardTitle>
                <CardDescription>
                  총 {data?.total_teams || 0}개 팀이 랭킹에 등록되어 있습니다
                </CardDescription>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto"></div>
                <p className="text-muted-foreground mt-4">로딩 중...</p>
              </div>
            ) : !data || data.top_focus_teams.length === 0 ? (
              <div className="text-center py-12">
                <Trophy className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
                <p className="text-lg font-medium text-muted-foreground mb-2">
                  랭킹 데이터가 없습니다
                </p>
                <p className="text-sm text-muted-foreground">
                  아직 랭킹에 등록된 팀이 없습니다
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                {data.top_focus_teams.map((team, index) => {
                  const rank = index + 1;
                  const rankIcon = getRankIcon(rank);
                  const badgeColor = getRankBadgeColor(rank);

                  return (
                    <div
                      key={team.team_id}
                      className="flex items-center gap-4 p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors cursor-pointer group"
                      onClick={() => handleTeamClick(team.team_id)}
                    >
                      {/* Rank */}
                      <div className="flex-shrink-0 w-16 flex items-center justify-center">
                        {rankIcon ? (
                          rankIcon
                        ) : (
                          <div
                            className={`w-10 h-10 rounded-full flex items-center justify-center font-bold ${badgeColor}`}
                          >
                            {rank}
                          </div>
                        )}
                      </div>

                      {/* Team Info */}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <h3 className="font-semibold text-lg truncate">
                            {team.team_name}
                          </h3>
                          <Badge variant="outline" className="text-xs">
                            {teamTypeLabels[team.team_type] || team.team_type}
                          </Badge>
                        </div>

                        {/* Stats */}
                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-3">
                          <div className="flex items-center gap-2">
                            <Clock className="w-4 h-4 text-muted-foreground" />
                            <div>
                              <p className="text-xs text-muted-foreground">
                                집중 시간
                              </p>
                              <p className="text-sm font-medium">
                                {Math.floor(team.total_focus_time / 60)}시간{" "}
                                {Math.floor(team.total_focus_time % 60)}분
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Target className="w-4 h-4 text-muted-foreground" />
                            <div>
                              <p className="text-xs text-muted-foreground">
                                세션 수
                              </p>
                              <p className="text-sm font-medium">
                                {team.session_count}개
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Gamepad2 className="w-4 h-4 text-muted-foreground" />
                            <div>
                              <p className="text-xs text-muted-foreground">
                                게임 점수
                              </p>
                              <p className="text-sm font-medium">
                                {team.total_game_score}점
                              </p>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-muted-foreground" />
                            <div>
                              <p className="text-xs text-muted-foreground">
                                게임 횟수
                              </p>
                              <p className="text-sm font-medium">
                                {team.game_count}회
                              </p>
                            </div>
                          </div>
                        </div>
                      </div>

                      {/* Arrow */}
                      <div className="flex-shrink-0">
                        <ArrowRight className="w-5 h-5 text-muted-foreground group-hover:text-primary transition-colors" />
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Info Card */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>랭킹 기준</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>
                • 랭킹은 집중 시간, 세션 수, 게임 점수를 종합하여 계산됩니다
              </p>
              <p>• 인증된 팀만 랭킹에 표시됩니다</p>
              <p>• 주간/월간 랭킹은 해당 기간 동안의 활동을 기준으로 합니다</p>
              <p>• 전체 랭킹은 모든 기간의 누적 데이터를 기준으로 합니다</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
