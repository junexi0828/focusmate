import React, { useState } from "react";
import { motion } from "framer-motion";
import {
  Users,
  Plus,
  Settings,
  LogOut,
  UserPlus,
  Copy,
  Check,
  Trophy,
  Target,
  Zap,
  Gamepad2,
  TrendingUp,
} from "lucide-react";
import { Button } from "../components/ui/button-enhanced";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { EmptyState } from "../components/EmptyState";
import { PageTransition } from "../components/PageTransition";
import {
  Team,
  rankingService,
  LeaderboardEntry,
} from "../features/ranking/services/rankingService";
import { GameTrialDialog } from "../features/ranking/components/GameTrialDialog";
import { GameTrial } from "../features/ranking/components/GameTrial";
import { Switch } from "../components/ui/switch";
import { Label } from "../components/ui/label";
import { useQuery } from "@tanstack/react-query";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "../components/ui/table";

interface RankingPageProps {
  teams: Team[];
  currentUserId?: string;
  onCreateTeam: () => void;
  onViewTeam: (teamId: string) => void;
  onInviteMember: (teamId: string) => void;
  onLeaveTeam: (teamId: string) => void;
  onManageTeam: (teamId: string) => void;
}

export function RankingPage({
  teams,
  currentUserId,
  onCreateTeam,
  onViewTeam,
  onInviteMember,
  onLeaveTeam,
  onManageTeam,
}: RankingPageProps) {
  const [copiedCode, setCopiedCode] = useState<string | null>(null);
  const [isTrialMode, setIsTrialMode] = useState(false);
  const [isGameDialogOpen, setIsGameDialogOpen] = useState(false);
  const [selectedGame, setSelectedGame] = useState<string | null>(null);
  const [leaderboardPeriod, setLeaderboardPeriod] = useState<
    "weekly" | "monthly" | "all_time"
  >("weekly");

  // Fetch leaderboard data
  const { data: leaderboardData, isLoading: isLeaderboardLoading } = useQuery({
    queryKey: ["ranking", "leaderboard", leaderboardPeriod],
    queryFn: async () => {
      const response = await rankingService.getLeaderboard(
        leaderboardPeriod,
        50
      );
      if (response.status === "error") {
        throw new Error(
          response.error?.message || "Failed to load leaderboard"
        );
      }
      return response.data;
    },
    refetchInterval: 30000, // Auto-refresh every 30 seconds
    refetchOnWindowFocus: true,
  });

  const handleCopyCode = async (code: string) => {
    try {
      await navigator.clipboard.writeText(code);
      setCopiedCode(code);
      setTimeout(() => setCopiedCode(null), 2000);
    } catch (err) {
      console.error("Failed to copy:", err);
    }
  };

  const getTeamTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      general: "일반",
      department: "학과",
      lab: "연구실",
      club: "동아리",
    };
    return labels[type] || type;
  };

  const getVerificationStatusBadge = (status: string) => {
    const variants: Record<
      string,
      {
        label: string;
        variant: "default" | "secondary" | "destructive" | "outline";
      }
    > = {
      none: { label: "인증 불필요", variant: "outline" },
      pending: { label: "인증 대기", variant: "secondary" },
      verified: { label: "인증 완료", variant: "default" },
      rejected: { label: "인증 반려", variant: "destructive" },
    };
    return variants[status] || { label: status, variant: "outline" as const };
  };

  const handleSelectGame = (gameType: string) => {
    setSelectedGame(gameType);
  };

  const handleCloseGame = () => {
    setSelectedGame(null);
  };

  return (
    <PageTransition className="space-y-6 w-full">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">랭킹전</h1>
          <p className="text-muted-foreground mt-1">
            팀과 함께 경쟁하며 집중력을 높여보세요
          </p>
        </div>
        <div className="flex items-center gap-4">
          {/* 체험하기 토글 */}
          <div className="flex items-center gap-2">
            <Switch
              id="trial-mode"
              checked={isTrialMode}
              onCheckedChange={setIsTrialMode}
            />
            <Label htmlFor="trial-mode" className="cursor-pointer">
              체험하기
            </Label>
          </div>
          {isTrialMode && (
            <Button variant="outline" onClick={() => setIsGameDialogOpen(true)}>
              <Gamepad2 className="w-4 h-4 mr-2" />
              게임 선택
            </Button>
          )}
          <Button variant="primary" onClick={onCreateTeam}>
            <Plus className="w-4 h-4 mr-2" />팀 만들기
          </Button>
        </div>
      </div>

      {/* Teams Grid */}
      {teams.length === 0 ? (
        <EmptyState
          icon={Users}
          title="참여 중인 팀이 없습니다"
          description="새로운 팀을 만들거나 초대를 받아 팀에 참여하세요"
          action={
            <Button variant="primary" onClick={onCreateTeam}>
              <Plus className="w-4 h-4 mr-2" />팀 만들기
            </Button>
          }
        />
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {teams.map((team) => {
            const statusBadge = getVerificationStatusBadge(
              team.verification_status
            );
            const isLeader = currentUserId === team.leader_id;

            return (
              <motion.div
                key={team.team_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                whileHover={{ y: -4 }}
                transition={{ duration: 0.2 }}
              >
                <Card className="h-full flex flex-col hover:border-primary/50 transition-colors">
                  <CardHeader>
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <CardTitle className="text-xl mb-2">
                          {team.team_name}
                        </CardTitle>
                        <div className="flex items-center gap-2 flex-wrap">
                          <Badge variant="outline">
                            {getTeamTypeLabel(team.team_type)}
                          </Badge>
                          <Badge variant={statusBadge.variant}>
                            {statusBadge.label}
                          </Badge>
                          {team.mini_game_enabled && (
                            <Badge variant="secondary">🎮 미니게임</Badge>
                          )}
                        </div>
                      </div>
                    </div>
                    {team.affiliation_info && (
                      <CardDescription className="mt-2">
                        {team.affiliation_info.school && (
                          <div>{team.affiliation_info.school}</div>
                        )}
                        {team.affiliation_info.department && (
                          <div>{team.affiliation_info.department}</div>
                        )}
                        {team.affiliation_info.lab && (
                          <div>{team.affiliation_info.lab}</div>
                        )}
                        {team.affiliation_info.club && (
                          <div>{team.affiliation_info.club}</div>
                        )}
                      </CardDescription>
                    )}
                  </CardHeader>
                  <CardContent className="flex-1 flex flex-col">
                    {/* Invite Code */}
                    {team.invite_code && (
                      <div className="mb-4 p-3 bg-muted rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <p className="text-xs text-muted-foreground mb-1">
                              초대 코드
                            </p>
                            <p className="font-mono text-sm font-semibold">
                              {team.invite_code}
                            </p>
                          </div>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => handleCopyCode(team.invite_code!)}
                            className="h-8 w-8 p-0"
                          >
                            {copiedCode === team.invite_code ? (
                              <Check className="w-4 h-4 text-green-600" />
                            ) : (
                              <Copy className="w-4 h-4" />
                            )}
                          </Button>
                        </div>
                      </div>
                    )}

                    {/* Stats - Real Data from API */}
                    <div className="grid grid-cols-3 gap-2 mb-4">
                      <div className="text-center p-2 bg-muted/50 rounded">
                        <Trophy className="w-4 h-4 mx-auto mb-1 text-muted-foreground" />
                        <p className="text-xs text-muted-foreground">순위</p>
                        <p className="text-sm font-semibold">
                          {team.current_rank || "-"}
                        </p>
                      </div>
                      <div className="text-center p-2 bg-muted/50 rounded">
                        <Target className="w-4 h-4 mx-auto mb-1 text-muted-foreground" />
                        <p className="text-xs text-muted-foreground">세션</p>
                        <p className="text-sm font-semibold">
                          {team.total_sessions || 0}
                        </p>
                      </div>
                      <div className="text-center p-2 bg-muted/50 rounded">
                        <Zap className="w-4 h-4 mx-auto mb-1 text-muted-foreground" />
                        <p className="text-xs text-muted-foreground">포인트</p>
                        <p className="text-sm font-semibold">
                          {team.total_points || 0}
                        </p>
                      </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-2 mt-auto">
                      <Button
                        variant="outline"
                        size="sm"
                        className="flex-1"
                        onClick={() => onViewTeam(team.team_id)}
                      >
                        보기
                      </Button>
                      {isLeader && (
                        <>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onInviteMember(team.team_id)}
                          >
                            <UserPlus className="w-4 h-4" />
                          </Button>
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() => onManageTeam(team.team_id)}
                          >
                            <Settings className="w-4 h-4" />
                          </Button>
                        </>
                      )}
                      {!isLeader && (
                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() => onLeaveTeam(team.team_id)}
                        >
                          <LogOut className="w-4 h-4" />
                        </Button>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>
      )}

      {/* 체험하기 모드 안내 */}
      {isTrialMode && (
        <Card className="border-primary/50 bg-primary/5">
          <CardContent className="pt-6">
            <div className="flex items-center gap-2">
              <Gamepad2 className="w-5 h-5 text-primary" />
              <div>
                <p className="font-semibold">체험하기 모드</p>
                <p className="text-sm text-muted-foreground">
                  게임을 선택하여 체험해보세요. 체험하기 모드에서는 점수가
                  저장되지 않습니다.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* 게임 선택 다이얼로그 */}
      <GameTrialDialog
        open={isGameDialogOpen}
        onOpenChange={setIsGameDialogOpen}
        onSelectGame={handleSelectGame}
      />

      {/* 게임 실행 */}
      {selectedGame && (
        <GameTrial gameType={selectedGame} onClose={handleCloseGame} />
      )}

      {/* 팀별 통계 대시보드 */}
      <Card className="mt-8">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                팀별 순위 통계
              </CardTitle>
              <CardDescription>
                모든 팀의 순위, 세션 수, 포인트를 확인하세요
              </CardDescription>
            </div>
            <div className="flex gap-2">
              <Button
                variant={leaderboardPeriod === "weekly" ? "default" : "outline"}
                size="sm"
                onClick={() => setLeaderboardPeriod("weekly")}
              >
                주간
              </Button>
              <Button
                variant={
                  leaderboardPeriod === "monthly" ? "default" : "outline"
                }
                size="sm"
                onClick={() => setLeaderboardPeriod("monthly")}
              >
                월간
              </Button>
              <Button
                variant={
                  leaderboardPeriod === "all_time" ? "default" : "outline"
                }
                size="sm"
                onClick={() => setLeaderboardPeriod("all_time")}
              >
                전체
              </Button>
            </div>
          </div>
        </CardHeader>
        <CardContent>
          {isLeaderboardLoading ? (
            <div className="flex items-center justify-center py-8">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
            </div>
          ) : leaderboardData?.leaderboard &&
            leaderboardData.leaderboard.length > 0 ? (
            <div className="overflow-x-auto">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead className="w-16 text-center">순위</TableHead>
                    <TableHead>팀명</TableHead>
                    <TableHead className="w-24 text-center">팀 유형</TableHead>
                    <TableHead className="w-24 text-center">세션</TableHead>
                    <TableHead className="w-32 text-center">포인트</TableHead>
                    <TableHead className="w-32 text-center">
                      평균 포인트
                    </TableHead>
                    <TableHead className="w-24 text-center">멤버 수</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {leaderboardData.leaderboard.map(
                    (entry: LeaderboardEntry) => {
                      const getRankBadge = (rank: number) => {
                        if (rank === 1) return "🥇";
                        if (rank === 2) return "🥈";
                        if (rank === 3) return "🥉";
                        return rank;
                      };

                      const getTeamTypeLabel = (type: string) => {
                        const labels: Record<string, string> = {
                          general: "일반",
                          department: "학과",
                          lab: "연구실",
                          club: "동아리",
                        };
                        return labels[type] || type;
                      };

                      return (
                        <TableRow
                          key={entry.team_id}
                          className="hover:bg-muted/50"
                        >
                          <TableCell className="text-center font-semibold">
                            {getRankBadge(entry.rank)}
                          </TableCell>
                          <TableCell className="font-medium">
                            {entry.team_name}
                          </TableCell>
                          <TableCell className="text-center">
                            <Badge variant="outline">
                              {getTeamTypeLabel(entry.team_type)}
                            </Badge>
                          </TableCell>
                          <TableCell className="text-center">
                            {entry.total_sessions ?? 0}
                          </TableCell>
                          <TableCell className="text-center font-semibold">
                            {Math.round(entry.score).toLocaleString()}
                          </TableCell>
                          <TableCell className="text-center text-muted-foreground">
                            {entry.average_score
                              ? Math.round(entry.average_score).toLocaleString()
                              : "-"}
                          </TableCell>
                          <TableCell className="text-center">
                            {entry.member_count ?? 0}명
                          </TableCell>
                        </TableRow>
                      );
                    }
                  )}
                </TableBody>
              </Table>
            </div>
          ) : (
            <div className="text-center py-8 text-muted-foreground">
              <Trophy className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>아직 랭킹 데이터가 없습니다</p>
            </div>
          )}
        </CardContent>
      </Card>
    </PageTransition>
  );
}
