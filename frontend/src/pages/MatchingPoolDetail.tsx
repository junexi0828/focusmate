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
  MessageSquare,
  Shield,
  CheckCircle2,
  XCircle,
  Hourglass,
} from "lucide-react";
import { MatchingPool } from "../types/matching";
import { formatDistanceToNow, format } from "date-fns";
import { ko } from "date-fns/locale";
import { useQuery } from "@tanstack/react-query";
import { authService } from "../features/auth/services/authService";

interface MatchingPoolDetailPageProps {
  pool: MatchingPool;
  currentUserId?: string;
  onBack: () => void;
}

export function MatchingPoolDetailPage({
  pool,
  currentUserId,
  onBack,
}: MatchingPoolDetailPageProps) {
  const isCreator = pool.creator_id === currentUserId;
  const isMember = pool.member_ids.includes(currentUserId || "");

  const statusLabels: Record<string, string> = {
    waiting: "대기 중",
    matched: "매칭 완료",
    expired: "만료됨",
    cancelled: "취소됨",
  };

  const statusColors: Record<string, string> = {
    waiting: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100",
    matched: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100",
    expired: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100",
    cancelled: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100",
  };

  const statusIcons: Record<string, React.ReactNode> = {
    waiting: <Hourglass className="w-4 h-4" />,
    matched: <CheckCircle2 className="w-4 h-4" />,
    expired: <Clock className="w-4 h-4" />,
    cancelled: <XCircle className="w-4 h-4" />,
  };

  const matchingTypeLabels: Record<string, string> = {
    blind: "블라인드",
    open: "공개",
  };

  const preferredMatchTypeLabels: Record<string, string> = {
    any: "무관",
    same_department: "같은 학과",
    major_category: "같은 계열",
  };

  // Fetch user information for each member
  const memberQueries = useQuery({
    queryKey: ["matching", "pool", pool.pool_id, "members"],
    queryFn: async () => {
      // Fetch user profiles for each member
      const memberPromises = pool.member_ids.map(async (userId) => {
        try {
          const profile = await authService.getProfile(userId);
          return profile.status === "success" ? profile.data : null;
        } catch {
          return null;
        }
      });
      return Promise.all(memberPromises);
    },
    enabled: !!pool.member_ids.length,
  });

  const members = memberQueries.data || [];

  const timeRemaining = React.useMemo(() => {
    const expiresAt = new Date(pool.expires_at);
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
  }, [pool.expires_at]);

  return (
    <div className="min-h-screen bg-muted/30">
      <div className="container mx-auto px-4 py-6 max-w-6xl">
        {/* Header */}
        <div className="mb-6">
          <Button variant="ghost" onClick={onBack} className="mb-4">
            <ArrowLeft className="w-4 h-4 mr-2" />
            뒤로가기
          </Button>
          <div className="flex items-start justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">매칭 풀 상세</h1>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge className={statusColors[pool.status]}>
                  {statusIcons[pool.status]}
                  <span className="ml-1">{statusLabels[pool.status]}</span>
                </Badge>
                <Badge variant="outline">
                  {pool.member_count}명 그룹
                </Badge>
                {isCreator && (
                  <Badge variant="default">
                    <Shield className="w-3 h-3 mr-1" />
                    생성자
                  </Badge>
                )}
                {isMember && !isCreator && (
                  <Badge variant="secondary">참여자</Badge>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Pool Info Card */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>매칭 풀 정보</CardTitle>
            <CardDescription>매칭 풀의 기본 정보를 확인하세요</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <p className="text-sm text-muted-foreground mb-1">학과</p>
                <p className="font-medium">{pool.department}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">학년</p>
                <p className="font-medium">{pool.grade}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">성별 구성</p>
                <p className="font-medium">{pool.gender}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">매칭 타입</p>
                <Badge variant="outline">
                  {matchingTypeLabels[pool.matching_type] || pool.matching_type}
                </Badge>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">선호 매칭 타입</p>
                <p className="font-medium">
                  {preferredMatchTypeLabels[pool.preferred_match_type] ||
                    pool.preferred_match_type}
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground mb-1">생성일</p>
                <p className="font-medium">
                  {format(new Date(pool.created_at), "yyyy년 M월 d일 HH:mm", {
                    locale: ko,
                  })}
                </p>
              </div>
            </div>

            {pool.message && (
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground mb-2 flex items-center gap-2">
                  <MessageSquare className="w-4 h-4" />
                  메시지
                </p>
                <p className="text-sm bg-muted/50 p-3 rounded-lg">{pool.message}</p>
              </div>
            )}

            {pool.preferred_categories && pool.preferred_categories.length > 0 && (
              <div className="pt-4 border-t">
                <p className="text-sm text-muted-foreground mb-2">선호 카테고리</p>
                <div className="flex flex-wrap gap-2">
                  {pool.preferred_categories.map((category, index) => (
                    <Badge key={index} variant="secondary">
                      {category}
                    </Badge>
                  ))}
                </div>
              </div>
            )}

            {pool.status === "waiting" && (
              <div className="pt-4 border-t">
                <div className="flex items-center gap-2 text-sm">
                  <Clock className="w-4 h-4 text-muted-foreground" />
                  <span className="text-muted-foreground">만료까지:</span>
                  <span className="font-medium">{timeRemaining}</span>
                </div>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Participants List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              참여자 목록 ({pool.member_count}명)
            </CardTitle>
            <CardDescription>
              이 매칭 풀에 참여한 모든 멤버를 확인하세요
            </CardDescription>
          </CardHeader>
          <CardContent>
            {memberQueries.isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary mx-auto"></div>
                <p className="text-muted-foreground mt-2">로딩 중...</p>
              </div>
            ) : members.length === 0 ? (
              <div className="text-center py-8">
                <Users className="w-12 h-12 mx-auto mb-4 text-muted-foreground opacity-50" />
                <p className="text-muted-foreground">참여자 정보를 불러올 수 없습니다</p>
              </div>
            ) : (
              <div className="space-y-3">
                {pool.member_ids.map((memberId, index) => {
                  const member = members[index];
                  const isMemberCreator = memberId === pool.creator_id;
                  const isCurrentUser = memberId === currentUserId;

                  return (
                    <div
                      key={memberId}
                      className="flex items-center justify-between p-4 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                    >
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                          <Users className="w-5 h-5 text-primary" />
                        </div>
                        <div>
                          <div className="flex items-center gap-2">
                            <p className="font-medium">
                              {member
                                ? member.username || member.email
                                : `멤버 ${memberId.slice(0, 8)}`}
                            </p>
                            {isMemberCreator && (
                              <Badge variant="default" className="text-xs">
                                <Shield className="w-3 h-3 mr-1" />
                                생성자
                              </Badge>
                            )}
                            {isCurrentUser && (
                              <Badge variant="outline" className="text-xs">
                                나
                              </Badge>
                            )}
                          </div>
                          {member && (
                            <p className="text-sm text-muted-foreground">
                              {member.email}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Matching Status */}
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>매칭 상태</CardTitle>
            <CardDescription>현재 매칭 진행 상황을 확인하세요</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 rounded-lg bg-muted/50">
                <div className="flex items-center gap-3">
                  {statusIcons[pool.status]}
                  <div>
                    <p className="font-medium">{statusLabels[pool.status]}</p>
                    <p className="text-sm text-muted-foreground">
                      {pool.status === "waiting" &&
                        "매칭 상대를 기다리는 중입니다"}
                      {pool.status === "matched" && "매칭이 완료되었습니다"}
                      {pool.status === "expired" && "매칭 풀이 만료되었습니다"}
                      {pool.status === "cancelled" && "매칭 풀이 취소되었습니다"}
                    </p>
                  </div>
                </div>
                <Badge className={statusColors[pool.status]}>
                  {statusLabels[pool.status]}
                </Badge>
              </div>

              {pool.status === "waiting" && (
                <div className="p-4 rounded-lg bg-blue-50 dark:bg-blue-950/20 border border-blue-200 dark:border-blue-800">
                  <p className="text-sm text-blue-700 dark:text-blue-300">
                    <Clock className="w-4 h-4 inline mr-2" />
                    매칭 상대를 찾는 중입니다. 매칭이 완료되면 알림을 받으실 수
                    있습니다.
                  </p>
                </div>
              )}

              {pool.status === "matched" && (
                <div className="p-4 rounded-lg bg-green-50 dark:bg-green-950/20 border border-green-200 dark:border-green-800">
                  <p className="text-sm text-green-700 dark:text-green-300">
                    <CheckCircle2 className="w-4 h-4 inline mr-2" />
                    매칭이 성사되었습니다! 채팅방에서 상대방과 대화를 시작하세요.
                  </p>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

