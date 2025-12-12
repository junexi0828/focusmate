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
} from "lucide-react";
import { Button } from "../components/ui/button-enhanced";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { EmptyState } from "../components/EmptyState";
import { PageTransition } from "../components/PageTransition";
import { Team } from "../features/ranking/services/rankingService";
import { cn } from "../utils";

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
    const variants: Record<string, { label: string; variant: "default" | "secondary" | "destructive" | "outline" }> = {
      none: { label: "인증 불필요", variant: "outline" },
      pending: { label: "인증 대기", variant: "secondary" },
      verified: { label: "인증 완료", variant: "default" },
      rejected: { label: "인증 반려", variant: "destructive" },
    };
    return variants[status] || { label: status, variant: "outline" as const };
  };

  return (
    <PageTransition className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">랭킹전</h1>
          <p className="text-muted-foreground mt-1">
            팀과 함께 경쟁하며 집중력을 높여보세요
          </p>
        </div>
        <Button variant="primary" onClick={onCreateTeam}>
          <Plus className="w-4 h-4 mr-2" />
          팀 만들기
        </Button>
      </div>

      {/* Teams Grid */}
      {teams.length === 0 ? (
        <EmptyState
          icon={Users}
          title="참여 중인 팀이 없습니다"
          description="새로운 팀을 만들거나 초대를 받아 팀에 참여하세요"
          action={
            <Button variant="primary" onClick={onCreateTeam}>
              <Plus className="w-4 h-4 mr-2" />
              팀 만들기
            </Button>
          }
        />
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {teams.map((team) => {
            const statusBadge = getVerificationStatusBadge(team.verification_status);
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
                        <CardTitle className="text-xl mb-2">{team.team_name}</CardTitle>
                        <div className="flex items-center gap-2 flex-wrap">
                          <Badge variant="outline">{getTeamTypeLabel(team.team_type)}</Badge>
                          <Badge variant={statusBadge.variant}>{statusBadge.label}</Badge>
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
                            <p className="text-xs text-muted-foreground mb-1">초대 코드</p>
                            <p className="font-mono text-sm font-semibold">{team.invite_code}</p>
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

                    {/* Stats Placeholder */}
                    <div className="grid grid-cols-3 gap-2 mb-4">
                      <div className="text-center p-2 bg-muted/50 rounded">
                        <Trophy className="w-4 h-4 mx-auto mb-1 text-muted-foreground" />
                        <p className="text-xs text-muted-foreground">순위</p>
                        <p className="text-sm font-semibold">-</p>
                      </div>
                      <div className="text-center p-2 bg-muted/50 rounded">
                        <Target className="w-4 h-4 mx-auto mb-1 text-muted-foreground" />
                        <p className="text-xs text-muted-foreground">세션</p>
                        <p className="text-sm font-semibold">-</p>
                      </div>
                      <div className="text-center p-2 bg-muted/50 rounded">
                        <Zap className="w-4 h-4 mx-auto mb-1 text-muted-foreground" />
                        <p className="text-xs text-muted-foreground">스트릭</p>
                        <p className="text-sm font-semibold">-</p>
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
    </PageTransition>
  );
}

