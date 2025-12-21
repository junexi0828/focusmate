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
  ArrowLeft,
  Users,
  Calendar,
  Clock,
  CheckCircle2,
  XCircle,
  Hourglass,
  MessageSquare,
  ArrowRight,
  Flag,
} from "lucide-react";
import { MatchingProposal, MatchingPool } from "../types/matching";
import { formatDistanceToNow, format } from "date-fns";
import { ko } from "date-fns/locale";
import { useNavigate } from "@tanstack/react-router";

interface ProposalDetailPageProps {
  proposal: MatchingProposal;
  currentUserId?: string;
  userPoolId?: string;
  userGroupStatus: string | null;
  otherGroupStatus: string | null;
  canRespond: boolean;
  onAccept: () => void;
  onReject: () => void;
  onBack: () => void;
  onReport?: () => void;
  isLoading: boolean;
}

export function ProposalDetailPage({
  proposal,
  currentUserId,
  userPoolId,
  userGroupStatus,
  otherGroupStatus,
  canRespond,
  onAccept,
  onReject,
  onBack,
  onReport,
  isLoading,
}: ProposalDetailPageProps) {
  const navigate = useNavigate();

  const statusLabels: Record<string, string> = {
    pending: "대기 중",
    accepted: "수락됨",
    rejected: "거절됨",
    matched: "매칭 완료",
  };

  const statusColors: Record<string, string> = {
    pending: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100",
    accepted: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100",
    rejected: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100",
    matched: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100",
  };

  const statusIcons: Record<string, React.ReactNode> = {
    pending: <Hourglass className="w-4 h-4" />,
    accepted: <CheckCircle2 className="w-4 h-4" />,
    rejected: <XCircle className="w-4 h-4" />,
    matched: <CheckCircle2 className="w-4 h-4" />,
  };

  const timeRemaining = React.useMemo(() => {
    const expiresAt = new Date(proposal.expires_at);
    const now = new Date();
    const diff = expiresAt.getTime() - now.getTime();

    if (diff <= 0) {
      return "만료됨";
    }

    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    const hours = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));

    if (days > 0) {
      return `${days}일 ${hours}시간 후`;
    } else if (hours > 0) {
      return `${hours}시간 ${minutes}분 후`;
    } else {
      return `${minutes}분 후`;
    }
  }, [proposal.expires_at]);

  const isGroupA = proposal.pool_id_a === userPoolId;
  const myPool = isGroupA ? proposal.pool_a : proposal.pool_b;
  const otherPool = isGroupA ? proposal.pool_b : proposal.pool_a;

  return (
    <div className="min-h-full bg-muted/30">
      <div className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Header */}
        <div className="mb-6">
          <Button variant="ghost" onClick={onBack} className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            뒤로가기
          </Button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">매칭 제안 상세</h1>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge className={statusColors[proposal.final_status]}>
                  {statusIcons[proposal.final_status]}
                  <span className="ml-1">
                    {statusLabels[proposal.final_status]}
                  </span>
                </Badge>
                {proposal.chat_room_id && (
                  <Badge variant="default">
                    <MessageSquare className="w-3 h-3 mr-1" />
                    채팅방 생성됨
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Proposal Status */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>제안 상태</CardTitle>
            <CardDescription>제안의 현재 상태를 확인하세요</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="p-4 rounded-lg bg-muted/50">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">우리 그룹</p>
                  <Badge className={statusColors[userGroupStatus || "pending"]}>
                    {statusIcons[userGroupStatus || "pending"]}
                    <span className="ml-1">
                      {statusLabels[userGroupStatus || "pending"]}
                    </span>
                  </Badge>
                </div>
                {myPool && (
                  <div className="text-sm text-muted-foreground mt-2">
                    <p>{myPool.department} · {myPool.member_count}명</p>
                  </div>
                )}
              </div>

              <div className="p-4 rounded-lg bg-muted/50">
                <div className="flex items-center justify-between mb-2">
                  <p className="text-sm font-medium">상대 그룹</p>
                  <Badge className={statusColors[otherGroupStatus || "pending"]}>
                    {statusIcons[otherGroupStatus || "pending"]}
                    <span className="ml-1">
                      {statusLabels[otherGroupStatus || "pending"]}
                    </span>
                  </Badge>
                </div>
                {otherPool && (
                  <div className="text-sm text-muted-foreground mt-2">
                    <p>{otherPool.department} · {otherPool.member_count}명</p>
                  </div>
                )}
              </div>
            </div>

            {proposal.final_status === "pending" && (
              <div className="pt-4 border-t">
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-muted-foreground" />
                  <span className="text-muted-foreground">만료까지:</span>
                  <span className="font-medium">{timeRemaining}</span>
                </div>
              </div>
            )}

            {canRespond && (
              <div className="pt-4 border-t flex gap-2">
                <Button
                  onClick={onAccept}
                  disabled={isLoading}
                  className="flex-1"
                >
                  <CheckCircle2 className="w-4 h-4 mr-2" />
                  수락
                </Button>
                <Button
                  onClick={onReject}
                  variant="destructive"
                  disabled={isLoading}
                  className="flex-1"
                >
                  <XCircle className="w-4 h-4 mr-2" />
                  거절
                </Button>
              </div>
            )}

            {proposal.final_status === "matched" && proposal.chat_room_id && (
              <div className="pt-4 border-t space-y-2">
                <Button
                  onClick={() =>
                    navigate({ to: `/matching/matched/$proposalId`, params: { proposalId: proposal.proposal_id } })
                  }
                  variant="outline"
                  className="w-full"
                >
                  매칭 상세보기
                </Button>
                <Button
                  onClick={() =>
                    navigate({ to: `/chat/${proposal.chat_room_id}` })
                  }
                  className="w-full"
                >
                  <MessageSquare className="w-4 h-4 mr-2" />
                  채팅방 입장하기
                  <ArrowRight className="w-4 h-4 ml-2" />
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Pool Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* My Pool */}
          {myPool && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  우리 그룹
                </CardTitle>
                <CardDescription>우리 매칭 풀 정보</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">학과</p>
                  <p className="font-medium">{myPool.department}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">학년</p>
                  <p className="font-medium">{myPool.grade}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">성별 구성</p>
                  <p className="font-medium">{myPool.gender}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">인원</p>
                  <p className="font-medium">{myPool.member_count}명</p>
                </div>
                {myPool.message && (
                  <div className="pt-3 border-t">
                    <p className="text-sm text-muted-foreground mb-1">메시지</p>
                    <p className="text-sm">{myPool.message}</p>
                  </div>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() =>
                    navigate({ to: `/matching/pools/${myPool.pool_id}` })
                  }
                >
                  풀 상세보기
                </Button>
              </CardContent>
            </Card>
          )}

          {/* Other Pool */}
          {otherPool && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  상대 그룹
                </CardTitle>
                <CardDescription>상대 매칭 풀 정보</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">학과</p>
                  <p className="font-medium">{otherPool.department}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">학년</p>
                  <p className="font-medium">{otherPool.grade}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">성별 구성</p>
                  <p className="font-medium">{otherPool.gender}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">인원</p>
                  <p className="font-medium">{otherPool.member_count}명</p>
                </div>
                {otherPool.message && (
                  <div className="pt-3 border-t">
                    <p className="text-sm text-muted-foreground mb-1">메시지</p>
                    <p className="text-sm">{otherPool.message}</p>
                  </div>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  className="w-full"
                  onClick={() =>
                    navigate({ to: `/matching/pools/${otherPool.pool_id}` })
                  }
                >
                  풀 상세보기
                </Button>
              </CardContent>
            </Card>
          )}
        </div>

        {/* Proposal Timeline */}
        <Card>
          <CardHeader>
            <CardTitle>제안 타임라인</CardTitle>
            <CardDescription>제안의 진행 상황을 확인하세요</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-start gap-4">
                <div className="w-2 h-2 rounded-full bg-primary mt-2"></div>
                <div className="flex-1">
                  <p className="font-medium">제안 생성</p>
                  <p className="text-sm text-muted-foreground">
                    {format(new Date(proposal.created_at), "yyyy년 M월 d일 HH:mm", {
                      locale: ko,
                    })}
                  </p>
                </div>
              </div>

              {userGroupStatus !== "pending" && (
                <div className="flex items-start gap-4">
                  <div className="w-2 h-2 rounded-full bg-green-500 mt-2"></div>
                  <div className="flex-1">
                    <p className="font-medium">우리 그룹 응답</p>
                    <p className="text-sm text-muted-foreground">
                      {statusLabels[userGroupStatus || "pending"]}
                    </p>
                  </div>
                </div>
              )}

              {otherGroupStatus !== "pending" && (
                <div className="flex items-start gap-4">
                  <div className="w-2 h-2 rounded-full bg-blue-500 mt-2"></div>
                  <div className="flex-1">
                    <p className="font-medium">상대 그룹 응답</p>
                    <p className="text-sm text-muted-foreground">
                      {statusLabels[otherGroupStatus || "pending"]}
                    </p>
                  </div>
                </div>
              )}

              {proposal.matched_at && (
                <div className="flex items-start gap-4">
                  <div className="w-2 h-2 rounded-full bg-purple-500 mt-2"></div>
                  <div className="flex-1">
                    <p className="font-medium">매칭 완료</p>
                    <p className="text-sm text-muted-foreground">
                      {format(new Date(proposal.matched_at), "yyyy년 M월 d일 HH:mm", {
                        locale: ko,
                      })}
                    </p>
                  </div>
                </div>
              )}

              <div className="flex items-start gap-4">
                <div className="w-2 h-2 rounded-full bg-muted-foreground mt-2"></div>
                <div className="flex-1">
                  <p className="font-medium">만료 예정</p>
                  <p className="text-sm text-muted-foreground">
                    {format(new Date(proposal.expires_at), "yyyy년 M월 d일 HH:mm", {
                      locale: ko,
                    })}
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

