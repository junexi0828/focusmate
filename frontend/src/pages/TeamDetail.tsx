import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button-enhanced";
import { Badge } from "../components/ui/badge";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "../components/ui/tabs";
import { ArrowLeft, Users, Clock, Target, Trophy, Award, Calendar, Shield, History, CheckCircle2, XCircle, Gamepad2, Medal, TrendingUp } from "lucide-react";
import { Team, TeamMember, TeamStats, SessionHistory, MiniGameRecord, MiniGameLeaderboardEntry } from "../features/ranking/services/rankingService";
import { formatDistanceToNow, format } from "date-fns";
import { ko } from "date-fns/locale";
import { StatCard } from "../features/stats/components";
import { useQuery } from "@tanstack/react-query";
import { rankingService } from "../features/ranking/services/rankingService";

interface TeamDetailPageProps {
  team: Team;
  members: TeamMember[];
  stats: TeamStats | null;
  currentUserId?: string;
  onBack: () => void;
}

type PeriodFilter = "all" | "week" | "month";
type ViewFilter = "team" | "personal";
type GameType = "dino_jump" | "dot_collector" | "snake" | "all";

export function TeamDetailPage({
  team,
  members,
  stats,
  currentUserId,
  onBack,
}: TeamDetailPageProps) {
  const isLeader = team.leader_id === currentUserId;
  const [periodFilter, setPeriodFilter] = useState<PeriodFilter>("all");
  const [viewFilter, setViewFilter] = useState<ViewFilter>("team");
  const [activeTab, setActiveTab] = useState("overview");
  const [gameTypeFilter, setGameTypeFilter] = useState<GameType>("all");
  const teamTypeLabels: { [key: string]: string } = {
    general: "일반",
    department: "학과",
    lab: "연구실",
    club: "동아리",
  };

  const verificationStatusLabels: { [key: string]: string } = {
    none: "미인증",
    pending: "인증 대기",
    verified: "인증됨",
    rejected: "거부됨",
  };

  const verificationStatusColors: { [key: string]: string } = {
    none: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100",
    pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100",
    verified: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100",
    rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100",
  };

  // Calculate date filter
  const getDateFilter = (period: PeriodFilter): Date | null => {
    const now = new Date();
    switch (period) {
      case "week":
        return new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
      case "month":
        return new Date(now.getTime() - 30 * 24 * 60 * 60 * 1000);
      default:
        return null;
    }
  };

  // Fetch session history
  const { data: sessions = [], isLoading: isLoadingSessions } = useQuery({
    queryKey: ["ranking", "team", team.team_id, "sessions", viewFilter, periodFilter],
    queryFn: async () => {
      const response = await rankingService.getSessionHistory(team.team_id, {
        userId: viewFilter === "personal" ? currentUserId : undefined,
        limit: 100,
      });
      return response.status === "success" ? response.data : [];
    },
    enabled: activeTab === "sessions",
  });

  // Filter sessions by period
  const filteredSessions = React.useMemo(() => {
    if (!sessions.length) return [];
    const dateFilter = getDateFilter(periodFilter);
    if (!dateFilter) return sessions;
    return sessions.filter((session) => {
      const sessionDate = new Date(session.completed_at);
      return sessionDate >= dateFilter;
    });
  }, [sessions, periodFilter]);

  // Fetch mini-game records
  const { data: miniGames = [], isLoading: isLoadingMiniGames } = useQuery({
    queryKey: ["ranking", "team", team.team_id, "mini-games", gameTypeFilter],
    queryFn: async () => {
      const response = await rankingService.getTeamMiniGames(team.team_id, {
        gameType: gameTypeFilter !== "all" ? gameTypeFilter : undefined,
        limit: 100,
      });
      return response.status === "success" ? response.data : [];
    },
    enabled: activeTab === "mini-games" && team.mini_game_enabled,
  });

  // Fetch mini-game leaderboards for each game type
  const gameTypes: GameType[] = ["dino_jump", "dot_collector", "snake"];
  const { data: leaderboards = {} } = useQuery({
    queryKey: ["ranking", "mini-games", "leaderboard"],
    queryFn: async () => {
      const results: Record<string, MiniGameLeaderboardEntry[]> = {};
      for (const gameType of gameTypes) {
        const response = await rankingService.getMiniGameLeaderboard(gameType, 10);
        if (response.status === "success") {
          results[gameType] = response.data;
        }
      }
      return results;
    },
    enabled: activeTab === "mini-games" && team.mini_game_enabled,
  });

  // Calculate best scores per game type
  const bestScores = React.useMemo(() => {
    const scores: Record<string, { score: number; played_at: string }> = {};
    miniGames.forEach((game) => {
      if (!scores[game.game_type] || game.score > scores[game.game_type].score) {
        scores[game.game_type] = {
          score: game.score,
          played_at: game.played_at,
        };
      }
    });
    return scores;
  }, [miniGames]);

  const gameTypeLabels: Record<string, string> = {
    dino_jump: "공룡 점프",
    dot_collector: "점 수집",
    snake: "스네이크",
  };

  return (
    <div className="min-h-full bg-muted/30">
      <div className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Header */}
        <div className="mb-6">
          <Button
            variant="ghost"
            onClick={onBack}
            className="mb-4"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            뒤로가기
          </Button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">{team.team_name}</h1>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge
                  className={verificationStatusColors[team.verification_status]}
                >
                  {verificationStatusLabels[team.verification_status]}
                </Badge>
                <Badge variant="outline">
                  {teamTypeLabels[team.team_type] || team.team_type}
                </Badge>
                {team.mini_game_enabled && (
                  <Badge variant="secondary">미니게임 활성화</Badge>
                )}
                {isLeader && (
                  <Badge variant="default">
                    <Shield className="w-3 h-3 mr-1" />
                    리더
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Team Info Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>팀 정보</CardTitle>
            <CardDescription>팀의 기본 정보를 확인하세요</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">팀 유형</p>
                <p className="font-medium">{teamTypeLabels[team.team_type] || team.team_type}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">인증 상태</p>
                <Badge className={verificationStatusColors[team.verification_status]}>
                  {verificationStatusLabels[team.verification_status]}
                </Badge>
              </div>
              {team.invite_code && (
                <div>
                  <p className="text-sm text-muted-foreground mb-1">초대 코드</p>
                  <p className="font-mono font-medium">{team.invite_code}</p>
                </div>
              )}
              <div>
                <p className="text-sm text-muted-foreground mb-1">생성일</p>
                <p className="font-medium">
                  {formatDistanceToNow(new Date(team.created_at), {
                    addSuffix: true,
                    locale: ko,
                  })}
                </p>
              </div>
            </div>
            {team.affiliation_info && (
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground mb-2">소속 정보</p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {team.affiliation_info.school && (
                    <p className="text-sm">
                      <span className="text-muted-foreground">학교:</span>{" "}
                      {team.affiliation_info.school}
                    </p>
                  )}
                  {team.affiliation_info.department && (
                    <p className="text-sm">
                      <span className="text-muted-foreground">학과:</span>{" "}
                      {team.affiliation_info.department}
                    </p>
                  )}
                  {team.affiliation_info.lab && (
                    <p className="text-sm">
                      <span className="text-muted-foreground">연구실:</span>{" "}
                      {team.affiliation_info.lab}
                    </p>
                  )}
                  {team.affiliation_info.club && (
                    <p className="text-sm">
                      <span className="text-muted-foreground">동아리:</span>{" "}
                      {team.affiliation_info.club}
                    </p>
                  )}
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Team Statistics */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard
              title="총 집중 시간"
              value={`${Math.floor(stats.total_focus_time / 60)}시간 ${stats.total_focus_time % 60}분`}
              icon={Clock}
              variant="primary"
            />
            <StatCard
              title="총 세션 수"
              value={`${stats.total_sessions}개`}
              icon={Target}
              variant="secondary"
            />
            <StatCard
              title="팀원 수"
              value={`${stats.member_count}명`}
              icon={Users}
              variant="default"
            />
            <StatCard
              title="연속 기록"
              value={`${stats.current_streak}일`}
              icon={Trophy}
              variant="default"
            />
          </div>
        )}

        {/* Tabs */}
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-3">
            <TabsTrigger value="overview">개요</TabsTrigger>
            <TabsTrigger value="sessions">세션 히스토리</TabsTrigger>
            {team.mini_game_enabled && (
              <TabsTrigger value="mini-games">미니게임</TabsTrigger>
            )}
          </TabsList>

          <TabsContent value="overview" className="mt-6">
            {/* Team Members */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  팀원 목록 ({members.length}명)
                </CardTitle>
                <CardDescription>팀에 참여한 모든 멤버를 확인하세요</CardDescription>
              </CardHeader>
              <CardContent>
                {members.length === 0 ? (
                  <p className="text-center text-muted-foreground py-8">
                    아직 팀원이 없습니다
                  </p>
                ) : (
                  <div className="space-y-3">
                    {members.map((member) => {
                      const isMemberLeader = member.role === "leader";
                      const isCurrentUser = member.user_id === currentUserId;
                      return (
                        <div
                          key={member.member_id}
                          className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                              <Users className="w-5 h-5 text-primary" />
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <p className="font-medium">
                                  {member.user_id === team.leader_id
                                    ? "리더"
                                    : `멤버 ${member.user_id.slice(0, 8)}`}
                                </p>
                                {isMemberLeader && (
                                  <Badge variant="default" className="text-xs">
                                    <Shield className="w-3 h-3 mr-1" />
                                    리더
                                  </Badge>
                                )}
                                {isCurrentUser && (
                                  <Badge variant="outline" className="text-xs">
                                    나
                                  </Badge>
                                )}
                              </div>
                              <p className="text-sm text-muted-foreground">
                                가입일:{" "}
                                {formatDistanceToNow(new Date(member.joined_at), {
                                  addSuffix: true,
                                  locale: ko,
                                })}
                              </p>
                            </div>
                          </div>
                          {stats?.member_breakdown && (
                            <div className="text-right">
                              <p className="text-sm text-muted-foreground">
                                세션: {stats.member_breakdown.find((m) => m.user_id === member.user_id)?.total_sessions || 0}개
                              </p>
                              <p className="text-sm text-muted-foreground">
                                집중: {Math.floor((stats.member_breakdown.find((m) => m.user_id === member.user_id)?.total_focus_time || 0) / 60)}분
                              </p>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="sessions" className="mt-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <History className="w-5 h-5" />
                  세션 히스토리
                </CardTitle>
                <CardDescription>팀 또는 개인의 세션 기록을 확인하세요</CardDescription>
              </CardHeader>
              <CardContent>
                {/* Filters */}
                <div className="flex flex-col sm:flex-row gap-4 mb-6">
                  <div className="flex gap-2">
                    <Button
                      variant={viewFilter === "team" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setViewFilter("team")}
                    >
                      팀 전체
                    </Button>
                    <Button
                      variant={viewFilter === "personal" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setViewFilter("personal")}
                      disabled={!currentUserId}
                    >
                      내 세션
                    </Button>
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant={periodFilter === "all" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setPeriodFilter("all")}
                    >
                      전체
                    </Button>
                    <Button
                      variant={periodFilter === "week" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setPeriodFilter("week")}
                    >
                      주간
                    </Button>
                    <Button
                      variant={periodFilter === "month" ? "default" : "outline"}
                      size="sm"
                      onClick={() => setPeriodFilter("month")}
                    >
                      월간
                    </Button>
                  </div>
                </div>

                {/* Session List */}
                {isLoadingSessions ? (
                  <div className="text-center py-8">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                    <p className="text-muted-foreground mt-2">로딩 중...</p>
                  </div>
                ) : filteredSessions.length === 0 ? (
                  <div className="text-center py-8">
                    <History className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                    <p className="text-muted-foreground">세션 기록이 없습니다</p>
                  </div>
                ) : (
                  <div className="space-y-3">
                    {filteredSessions.map((session) => {
                      const sessionDate = new Date(session.completed_at);
                      const isWorkSession = session.session_type === "work";
                      return (
                        <div
                          key={session.session_id}
                          className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                        >
                          <div className="flex items-center gap-4">
                            <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                              isWorkSession
                                ? "bg-primary/10 text-primary"
                                : "bg-secondary/10 text-secondary-foreground"
                            }`}>
                              {isWorkSession ? (
                                <Target className="w-6 h-6" />
                              ) : (
                                <Clock className="w-6 h-6" />
                              )}
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <p className="font-medium">
                                  {isWorkSession ? "집중 세션" : "휴식 세션"}
                                </p>
                                {session.success ? (
                                  <CheckCircle2 className="w-4 h-4 text-green-500" />
                                ) : (
                                  <XCircle className="w-4 h-4 text-red-500" />
                                )}
                                <Badge variant={isWorkSession ? "default" : "secondary"} className="text-xs">
                                  {session.duration_minutes}분
                                </Badge>
                              </div>
                              <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                                <span className="flex items-center gap-1">
                                  <Calendar className="w-3 h-3" />
                                  {format(sessionDate, "yyyy년 M월 d일 HH:mm", { locale: ko })}
                                </span>
                                {viewFilter === "team" && (
                                  <span className="text-xs">
                                    {members.find((m) => m.user_id === session.user_id)?.role === "leader" ? "리더" : "멤버"}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          <div className="text-right">
                            {session.success ? (
                              <Badge variant="default" className="bg-green-500">
                                완료
                              </Badge>
                            ) : (
                              <Badge variant="destructive">
                                실패
                              </Badge>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>

          {team.mini_game_enabled && (
            <TabsContent value="mini-games" className="mt-6">
              <div className="space-y-6">
                {/* Best Scores */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Medal className="w-5 h-5" />
                      게임별 최고 점수
                    </CardTitle>
                    <CardDescription>팀의 각 게임별 최고 점수를 확인하세요</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {Object.keys(bestScores).length === 0 ? (
                      <p className="text-center text-muted-foreground py-8">
                        아직 플레이한 게임이 없습니다
                      </p>
                    ) : (
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        {gameTypes.map((gameType) => {
                          const best = bestScores[gameType];
                          return (
                            <div
                              key={gameType}
                              className="p-4 rounded-lg border bg-card"
                            >
                              <div className="flex items-center gap-2 mb-2">
                                <Gamepad2 className="w-5 h-5 text-primary" />
                                <p className="font-medium">{gameTypeLabels[gameType] || gameType}</p>
                              </div>
                              {best ? (
                                <>
                                  <p className="text-2xl font-bold text-primary">{best.score}점</p>
                                  <p className="text-xs text-muted-foreground mt-1">
                                    {format(new Date(best.played_at), "yyyy년 M월 d일", { locale: ko })}
                                  </p>
                                </>
                              ) : (
                                <p className="text-sm text-muted-foreground">기록 없음</p>
                              )}
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Game Type Filter */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <Gamepad2 className="w-5 h-5" />
                      게임 플레이 기록
                    </CardTitle>
                    <CardDescription>팀의 모든 게임 플레이 기록을 확인하세요</CardDescription>
                  </CardHeader>
                  <CardContent>
                    {/* Game Type Filter */}
                    <div className="flex gap-2 mb-6">
                      <Button
                        variant={gameTypeFilter === "all" ? "default" : "outline"}
                        size="sm"
                        onClick={() => setGameTypeFilter("all")}
                      >
                        전체
                      </Button>
                      {gameTypes.map((gameType) => (
                        <Button
                          key={gameType}
                          variant={gameTypeFilter === gameType ? "default" : "outline"}
                          size="sm"
                          onClick={() => setGameTypeFilter(gameType)}
                        >
                          {gameTypeLabels[gameType] || gameType}
                        </Button>
                      ))}
                    </div>

                    {/* Game Records List */}
                    {isLoadingMiniGames ? (
                      <div className="text-center py-8">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                        <p className="text-muted-foreground mt-2">로딩 중...</p>
                      </div>
                    ) : miniGames.length === 0 ? (
                      <div className="text-center py-8">
                        <Gamepad2 className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                        <p className="text-muted-foreground">게임 기록이 없습니다</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {miniGames.map((game) => {
                          const gameDate = new Date(game.played_at);
                          return (
                            <div
                              key={game.game_id}
                              className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                            >
                              <div className="flex items-center gap-4">
                                <div className="w-12 h-12 rounded-full bg-primary/10 flex items-center justify-center">
                                  <Gamepad2 className="w-6 h-6 text-primary" />
                                </div>
                                <div>
                                  <div className="flex items-center gap-2">
                                    <p className="font-medium">
                                      {gameTypeLabels[game.game_type] || game.game_type}
                                    </p>
                                    {game.success ? (
                                      <CheckCircle2 className="w-4 h-4 text-green-500" />
                                    ) : (
                                      <XCircle className="w-4 h-4 text-red-500" />
                                    )}
                                    <Badge variant="default" className="text-xs">
                                      {game.score}점
                                    </Badge>
                                  </div>
                                  <div className="flex items-center gap-4 text-sm text-muted-foreground mt-1">
                                    <span className="flex items-center gap-1">
                                      <Calendar className="w-3 h-3" />
                                      {format(gameDate, "yyyy년 M월 d일 HH:mm", { locale: ko })}
                                    </span>
                                    {game.completion_time && (
                                      <span className="flex items-center gap-1">
                                        <Clock className="w-3 h-3" />
                                        {Math.floor(game.completion_time)}초
                                      </span>
                                    )}
                                  </div>
                                </div>
                              </div>
                              <div className="text-right">
                                {game.success ? (
                                  <Badge variant="default" className="bg-green-500">
                                    성공
                                  </Badge>
                                ) : (
                                  <Badge variant="destructive">
                                    실패
                                  </Badge>
                                )}
                              </div>
                            </div>
                          );
                        })}
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* Leaderboards */}
                <Card>
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2">
                      <TrendingUp className="w-5 h-5" />
                      게임별 리더보드
                    </CardTitle>
                    <CardDescription>전체 팀 중 상위 팀을 확인하세요</CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-6">
                      {gameTypes.map((gameType) => {
                        const leaderboard = leaderboards[gameType] || [];
                        const teamRank = leaderboard.findIndex((entry) => entry.team_id === team.team_id) + 1;
                        return (
                          <div key={gameType} className="space-y-3">
                            <div className="flex items-center justify-between">
                              <h3 className="font-semibold text-lg">
                                {gameTypeLabels[gameType] || gameType}
                              </h3>
                              {teamRank > 0 && (
                                <Badge variant="default">
                                  우리 팀 순위: {teamRank}위
                                </Badge>
                              )}
                            </div>
                            {leaderboard.length === 0 ? (
                              <p className="text-sm text-muted-foreground text-center py-4">
                                리더보드 데이터가 없습니다
                              </p>
                            ) : (
                              <div className="space-y-2">
                                {leaderboard.slice(0, 10).map((entry, index) => {
                                  const isOurTeam = entry.team_id === team.team_id;
                                  return (
                                    <div
                                      key={entry.team_id}
                                      className={`flex items-center justify-between p-3 rounded-lg border ${
                                        isOurTeam
                                          ? "bg-primary/10 border-primary"
                                          : "bg-card"
                                      }`}
                                    >
                                      <div className="flex items-center gap-3">
                                        <div
                                          className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                                            index === 0
                                              ? "bg-yellow-500 text-white"
                                              : index === 1
                                              ? "bg-gray-400 text-white"
                                              : index === 2
                                              ? "bg-orange-500 text-white"
                                              : "bg-muted text-muted-foreground"
                                          }`}
                                        >
                                          {index + 1}
                                        </div>
                                        <div>
                                          <p className={`font-medium ${isOurTeam ? "text-primary" : ""}`}>
                                            {entry.team_name}
                                            {isOurTeam && " (우리 팀)"}
                                          </p>
                                          <p className="text-xs text-muted-foreground">
                                            플레이: {entry.games_played}회
                                          </p>
                                        </div>
                                      </div>
                                      <div className="text-right">
                                        <p className="font-bold text-lg">{entry.best_score}점</p>
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            )}
                          </div>
                        );
                      })}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </TabsContent>
          )}
        </Tabs>
      </div>
    </div>
  );
}

