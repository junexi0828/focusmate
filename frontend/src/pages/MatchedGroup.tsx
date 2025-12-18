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
  MessageSquare,
  CheckCircle2,
  User,
  Shield,
  Eye,
  EyeOff,
} from "lucide-react";
import { MatchingProposal } from "../types/matching";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import { useQuery } from "@tanstack/react-query";
import { authService } from "../features/auth/services/authService";
import { matchingApi } from "../api/matching";

interface ChatRoom {
  room_id: string;
  room_type: string;
  room_name?: string;
  display_mode?: string;
  metadata?: {
    type?: string;
    proposal_id?: string;
    group_a_info?: {
      member_ids?: string[];
      department?: string;
    };
    group_b_info?: {
      member_ids?: string[];
      department?: string;
    };
  };
  created_at: string;
}

interface ChatMember {
  member_id: string;
  user_id: string;
  role: string;
  display_name?: string;
  anonymous_name?: string;
  group_label?: string;
  member_index?: number;
  is_active: boolean;
  joined_at: string;
}

interface MatchedGroupPageProps {
  proposal: MatchingProposal;
  chatRoom: ChatRoom;
  members: ChatMember[];
  currentUserId?: string;
  userPoolId?: string;
  isGroupA: boolean;
  onBack: () => void;
  onEnterChat: () => void;
}

export function MatchedGroupPage({
  proposal,
  chatRoom,
  members,
  currentUserId,
  userPoolId,
  isGroupA,
  onBack,
  onEnterChat,
}: MatchedGroupPageProps) {
  const myPool = useQuery({
    queryKey: ["matching", "pool", isGroupA ? proposal.pool_id_a : proposal.pool_id_b],
    queryFn: async () => {
      const poolId = isGroupA ? proposal.pool_id_a : proposal.pool_id_b;
      return await matchingApi.getPool(poolId);
    },
    enabled: !!userPoolId,
  });

  const otherPool = useQuery({
    queryKey: ["matching", "pool", isGroupA ? proposal.pool_id_b : proposal.pool_id_a],
    queryFn: async () => {
      const poolId = isGroupA ? proposal.pool_id_b : proposal.pool_id_a;
      return await matchingApi.getPool(poolId);
    },
  });

  // Fetch user profiles for members
  const memberProfiles = useQuery({
    queryKey: ["chat", "members", "profiles", members.map((m) => m.user_id).join(",")],
    queryFn: async () => {
      const profiles = await Promise.all(
        members.map(async (member) => {
          try {
            const profile = await authService.getProfile(member.user_id);
            return profile.status === "success" ? profile.data : null;
          } catch {
            return null;
          }
        })
      );
      return profiles;
    },
    enabled: members.length > 0,
  });

  const profiles = memberProfiles.data || [];

  // Group members by group label
  const groupAMembers = members.filter((m) => m.group_label === "A");
  const groupBMembers = members.filter((m) => m.group_label === "B");

  const isBlindMode = chatRoom.display_mode === "blind";

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
              <h1 className="text-3xl font-bold mb-2">매칭 성사! 🎉</h1>
              <div className="flex items-center gap-2 flex-wrap">
                <Badge className="bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100">
                  <CheckCircle2 className="w-4 h-4 mr-1" />
                  매칭 완료
                </Badge>
                {isBlindMode ? (
                  <Badge variant="outline">
                    <EyeOff className="w-3 h-3 mr-1" />
                    블라인드 모드
                  </Badge>
                ) : (
                  <Badge variant="outline">
                    <Eye className="w-3 h-3 mr-1" />
                    공개 모드
                  </Badge>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Success Message */}
        <Card className="mb-6 border-green-200 bg-green-50 dark:bg-green-950/20">
          <CardContent className="pt-6">
            <div className="flex items-center gap-4">
              <div className="w-16 h-16 rounded-full bg-green-100 dark:bg-green-900 flex items-center justify-center">
                <CheckCircle2 className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <div className="flex-1">
                <h2 className="text-xl font-bold mb-1">매칭이 성사되었습니다!</h2>
                <p className="text-muted-foreground">
                  채팅방이 자동으로 생성되었습니다. 이제 상대방과 대화를 시작할 수
                  있습니다.
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Chat Room Info */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <MessageSquare className="w-5 h-5" />
              채팅방 정보
            </CardTitle>
            <CardDescription>
              매칭 성사로 자동 생성된 채팅방입니다
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm text-muted-foreground mb-1">채팅방 이름</p>
              <p className="font-medium">
                {chatRoom.room_name || "매칭 그룹 채팅"}
              </p>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">표시 모드</p>
              <Badge variant="outline">
                {isBlindMode ? "블라인드 (익명)" : "공개 (실명)"}
              </Badge>
            </div>
            <div>
              <p className="text-sm text-muted-foreground mb-1">생성일</p>
              <p className="font-medium">
                {format(new Date(chatRoom.created_at), "yyyy년 M월 d일 HH:mm", {
                  locale: ko,
                })}
              </p>
            </div>
            <Button onClick={onEnterChat} className="w-full" size="lg">
              <MessageSquare className="w-5 h-5 mr-2" />
              채팅방 입장하기
            </Button>
          </CardContent>
        </Card>

        {/* Group Information */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          {/* Our Group */}
          {myPool.data && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  우리 그룹 (그룹 {isGroupA ? "A" : "B"})
                </CardTitle>
                <CardDescription>우리 매칭 풀 정보</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">학과</p>
                  <p className="font-medium">{myPool.data.department}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">인원</p>
                  <p className="font-medium">{myPool.data.member_count}명</p>
                </div>
                {myPool.data.message && (
                  <div className="pt-3 border-t">
                    <p className="text-sm text-muted-foreground mb-1">메시지</p>
                    <p className="text-sm">{myPool.data.message}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}

          {/* Other Group */}
          {otherPool.data && (
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <Users className="w-5 h-5" />
                  상대 그룹 (그룹 {isGroupA ? "B" : "A"})
                </CardTitle>
                <CardDescription>상대 매칭 풀 정보</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div>
                  <p className="text-sm text-muted-foreground mb-1">학과</p>
                  <p className="font-medium">{otherPool.data.department}</p>
                </div>
                <div>
                  <p className="text-sm text-muted-foreground mb-1">인원</p>
                  <p className="font-medium">{otherPool.data.member_count}명</p>
                </div>
                {otherPool.data.message && (
                  <div className="pt-3 border-t">
                    <p className="text-sm text-muted-foreground mb-1">메시지</p>
                    <p className="text-sm">{otherPool.data.message}</p>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </div>

        {/* Members List */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users className="w-5 h-5" />
              그룹원 목록 ({members.length}명)
            </CardTitle>
            <CardDescription>
              매칭된 그룹의 모든 멤버를 확인하세요
            </CardDescription>
          </CardHeader>
          <CardContent>
            {/* Group A Members */}
            {groupAMembers.length > 0 && (
              <div className="mb-6">
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <Badge variant="outline">그룹 A</Badge>
                  {chatRoom.metadata?.group_a_info?.department && (
                    <span className="text-sm text-muted-foreground">
                      ({chatRoom.metadata.group_a_info.department})
                    </span>
                  )}
                </h3>
                <div className="space-y-2">
                  {groupAMembers.map((member, index) => {
                    const profile = profiles.find((p) => p?.id === member.user_id);
                    const isCurrentUser = member.user_id === currentUserId;
                    const displayName = isBlindMode
                      ? member.anonymous_name || `A${member.member_index || index + 1}`
                      : profile?.username || member.display_name || `멤버 ${index + 1}`;

                    return (
                      <div
                        key={member.member_id}
                        className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                            <User className="w-5 h-5 text-primary" />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="font-medium">{displayName}</p>
                              {isCurrentUser && (
                                <Badge variant="outline" className="text-xs">
                                  나
                                </Badge>
                              )}
                              {isBlindMode && (
                                <Badge variant="secondary" className="text-xs">
                                  익명
                                </Badge>
                              )}
                            </div>
                            {!isBlindMode && profile && (
                              <p className="text-sm text-muted-foreground">
                                {profile.email}
                              </p>
                            )}
                          </div>
                        </div>
                        {member.role === "owner" && (
                          <Badge variant="default" className="text-xs">
                            <Shield className="w-3 h-3 mr-1" />
                            방장
                          </Badge>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Group B Members */}
            {groupBMembers.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold mb-3 flex items-center gap-2">
                  <Badge variant="outline">그룹 B</Badge>
                  {chatRoom.metadata?.group_b_info?.department && (
                    <span className="text-sm text-muted-foreground">
                      ({chatRoom.metadata.group_b_info.department})
                    </span>
                  )}
                </h3>
                <div className="space-y-2">
                  {groupBMembers.map((member, index) => {
                    const profile = profiles.find((p) => p?.id === member.user_id);
                    const isCurrentUser = member.user_id === currentUserId;
                    const displayName = isBlindMode
                      ? member.anonymous_name || `B${member.member_index || index + 1}`
                      : profile?.username || member.display_name || `멤버 ${index + 1}`;

                    return (
                      <div
                        key={member.member_id}
                        className="flex items-center justify-between p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                      >
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 rounded-full bg-primary/10 flex items-center justify-center">
                            <User className="w-5 h-5 text-primary" />
                          </div>
                          <div>
                            <div className="flex items-center gap-2">
                              <p className="font-medium">{displayName}</p>
                              {isCurrentUser && (
                                <Badge variant="outline" className="text-xs">
                                  나
                                </Badge>
                              )}
                              {isBlindMode && (
                                <Badge variant="secondary" className="text-xs">
                                  익명
                                </Badge>
                              )}
                            </div>
                            {!isBlindMode && profile && (
                              <p className="text-sm text-muted-foreground">
                                {profile.email}
                              </p>
                            )}
                          </div>
                        </div>
                        {member.role === "owner" && (
                          <Badge variant="default" className="text-xs">
                            <Shield className="w-3 h-3 mr-1" />
                            방장
                          </Badge>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

