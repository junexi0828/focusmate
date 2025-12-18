import React, { useState } from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation } from "@tanstack/react-query";
import { authService } from "../features/auth/services/authService";
import { matchingApi } from "../api/matching";
import { PageTransition } from "../components/PageTransition";
import { toast } from "sonner";
import { Button } from "../components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../components/ui/select";
import { Heart, Users2, UserPlus, CheckCircle2, XCircle, Clock, BarChart3 } from "lucide-react";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import type { MatchingPoolCreate } from "../types/matching";
import { VerificationStatus, VerificationSettings } from "../features/verification";

export const Route = createFileRoute("/matching/")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  loader: async () => {
    try {
      const [poolStats, myPool, proposals] = await Promise.allSettled([
        matchingApi.getPoolStats(),
        matchingApi.getMyPool().catch(() => null),
        matchingApi.getMyProposals().catch(() => []),
      ]);

      return {
        stats: poolStats.status === "fulfilled" ? poolStats.value : null,
        myPool: myPool.status === "fulfilled" ? myPool.value : null,
        proposals: proposals.status === "fulfilled" ? proposals.value : [],
      };
    } catch (error) {
      console.error("Failed to load matching data:", error);
      return { stats: null, myPool: null, proposals: [] };
    }
  },
  component: MatchingComponent,
});

function MatchingComponent() {
  const navigate = useNavigate();
  const initialData = Route.useLoaderData();
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState<Partial<MatchingPoolCreate>>({
    member_ids: [],
    gender: "mixed",
    matching_type: "open",
    age_range_min: 18,
    age_range_max: 30,
  });

  const { data: stats } = useQuery({
    queryKey: ["matching", "stats"],
    queryFn: () => matchingApi.getPoolStats(),
    initialData: initialData.stats,
  });

  const { data: myPool, refetch: refetchPool } = useQuery({
    queryKey: ["matching", "myPool"],
    queryFn: () => matchingApi.getMyPool().catch(() => null),
    initialData: initialData.myPool,
  });

  const { data: proposals = [], refetch: refetchProposals } = useQuery({
    queryKey: ["matching", "proposals"],
    queryFn: () => matchingApi.getMyProposals(),
    initialData: initialData.proposals,
  });

  const cancelPoolMutation = useMutation({
    mutationFn: (poolId: string) => matchingApi.cancelPool(poolId),
    onSuccess: () => {
      toast.success("매칭 풀이 취소되었습니다");
      refetchPool();
    },
    onError: () => {
      toast.error("매칭 풀 취소에 실패했습니다");
    },
  });

  const respondToProposalMutation = useMutation({
    mutationFn: ({
      proposalId,
      action,
    }: {
      proposalId: string;
      action: { action: "accept" | "reject" };
    }) => matchingApi.respondToProposal(proposalId, action),
    onSuccess: () => {
      toast.success("응답이 전송되었습니다");
      refetchProposals();
      refetchPool();
    },
    onError: () => {
      toast.error("응답 전송에 실패했습니다");
    },
  });

  const createPoolMutation = useMutation({
    mutationFn: (data: MatchingPoolCreate) => matchingApi.createPool(data),
    onSuccess: () => {
      toast.success("매칭 풀이 생성되었습니다");
      setIsCreating(false);
      refetchPool();
      setFormData({
        member_ids: [],
        gender: "mixed",
        matching_type: "open",
        age_range_min: 18,
        age_range_max: 30,
      });
    },
    onError: (error: unknown) => {
      const detail = error?.response?.data?.detail;
      const message = typeof detail === "string"
        ? detail
        : Array.isArray(detail)
        ? detail.map((e: { msg?: string } | string) => (typeof e === 'string' ? e : e.msg || String(e))).join(", ")
        : "매칭 풀 생성에 실패했습니다";
      toast.error(message);
    },
  });

  const handleCreatePool = () => {
    if (!formData.university || !formData.department) {
      toast.error("학교와 학과를 입력해주세요");
      return;
    }
    createPoolMutation.mutate(formData as MatchingPoolCreate);
  };

  return (
    <PageTransition>
      <div className="space-y-8">
        {/* Header */}
        <div>
          <h1 className="text-4xl font-bold tracking-tight flex items-center gap-3">
            <Heart className="w-10 h-10 text-pink-500" />
            핑크캠퍼스
          </h1>
          <p className="text-muted-foreground mt-2">
            같은 학교 친구들과 그룹 매칭을 통해 함께 공부하세요
          </p>
        </div>

        {/* Verification Status */}
        <VerificationStatus />

        {/* Stats */}
        {stats && (
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>대기 중인 풀</CardDescription>
                <CardTitle className="text-3xl">{stats.total_waiting}</CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>평균 대기 시간</CardDescription>
                <CardTitle className="text-3xl">
                  {stats.average_wait_time_hours.toFixed(1)}h
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>그룹별 통계</CardDescription>
                <CardTitle className="text-2xl">
                  {Object.keys(stats.by_member_count).length > 0
                    ? Object.keys(stats.by_member_count).length
                    : "0"}{" "}
                  타입
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>내 상태</CardDescription>
                <CardTitle className="text-2xl">
                  {myPool ? (
                    <Badge variant="default" className="text-sm">
                      대기 중
                    </Badge>
                  ) : (
                    <Badge variant="secondary" className="text-sm">
                      미참여
                    </Badge>
                  )}
                </CardTitle>
              </CardHeader>
            </Card>
          </div>
        )}

        {/* Verification Settings */}
        <VerificationSettings />

        {/* My Pool */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Users2 className="w-5 h-5" />
              내 매칭 풀
            </CardTitle>
            <CardDescription>
              현재 참여 중인 매칭 풀 정보입니다
            </CardDescription>
          </CardHeader>
          <CardContent>
            {myPool ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">
                      {myPool.member_count}명 그룹 매칭
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {myPool.department} · {myPool.grade} · {myPool.gender}
                    </p>
                    {myPool.message && (
                      <p className="text-sm text-muted-foreground mt-2">
                        "{myPool.message}"
                      </p>
                    )}
                  </div>
                  <Badge
                    variant={
                      myPool.status === "waiting" ? "default" : "secondary"
                    }
                  >
                    {myPool.status === "waiting" ? "대기 중" : myPool.status}
                  </Badge>
                </div>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => cancelPoolMutation.mutate(myPool.pool_id)}
                  disabled={cancelPoolMutation.isPending}
                >
                  매칭 취소
                </Button>
              </div>
            ) : (
              <div className="text-center py-8">
                <Users2 className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground mb-4">
                  아직 매칭 풀에 참여하지 않았습니다
                </p>
                <Button onClick={() => setIsCreating(true)}>
                  <UserPlus className="w-4 h-4 mr-2" />
                  매칭 풀 생성
                </Button>
              </div>
            )}
          </CardContent>
        </Card>

        {/* Proposals */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Heart className="w-5 h-5 text-pink-500" />
              매칭 제안
            </CardTitle>
            <CardDescription>
              받은 매칭 제안을 확인하고 수락/거절하세요
            </CardDescription>
          </CardHeader>
          <CardContent>
            {proposals.length > 0 ? (
              <div className="space-y-4">
                {proposals.map((proposal) => (
                  <div
                    key={proposal.proposal_id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                    onClick={() =>
                      navigate({ to: "/matching/proposals/$proposalId", params: { proposalId: proposal.proposal_id } })
                    }
                  >
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        <p className="font-medium">새로운 매칭 제안</p>
                        {proposal.final_status === "pending" ? (
                          <Badge variant="outline">
                            <Clock className="w-3 h-3 mr-1" />
                            대기 중
                          </Badge>
                        ) : proposal.final_status === "matched" ? (
                          <Badge variant="default">
                            <CheckCircle2 className="w-3 h-3 mr-1" />
                            매칭 완료
                          </Badge>
                        ) : (
                          <Badge variant="secondary">
                            <XCircle className="w-3 h-3 mr-1" />
                            거절됨
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {format(new Date(proposal.created_at), "yyyy년 M월 d일 HH:mm", {
                          locale: ko,
                        })}
                      </p>
                    </div>
                    <div className="flex gap-2" onClick={(e) => e.stopPropagation()}>
                      {proposal.final_status === "pending" && (
                        <>
                          <Button
                            size="sm"
                            onClick={() =>
                              respondToProposalMutation.mutate({
                                proposalId: proposal.proposal_id,
                                action: { action: "accept" },
                              })
                            }
                            disabled={respondToProposalMutation.isPending}
                          >
                            <CheckCircle2 className="w-4 h-4 mr-1" />
                            수락
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() =>
                              respondToProposalMutation.mutate({
                                proposalId: proposal.proposal_id,
                                action: { action: "reject" },
                              })
                            }
                            disabled={respondToProposalMutation.isPending}
                          >
                            <XCircle className="w-4 h-4 mr-1" />
                            거절
                          </Button>
                        </>
                      )}
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() =>
                          navigate({ to: "/matching/proposals/$proposalId", params: { proposalId: proposal.proposal_id } })
                        }
                      >
                        상세보기
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-8">
                <Heart className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
                <p className="text-muted-foreground">
                  아직 받은 매칭 제안이 없습니다
                </p>
              </div>
            )}
          </CardContent>
        </Card>

               {/* Info */}
               <Card className="border-pink-200 bg-pink-50 dark:bg-pink-950/20">
                 <CardHeader>
                   <CardTitle className="text-pink-700 dark:text-pink-400">
                     핑크캠퍼스란?
                   </CardTitle>
                 </CardHeader>
                 <CardContent className="text-sm text-pink-600 dark:text-pink-300 space-y-2">
                   <p>
                     • 같은 학교, 같은 학과 학생들끼리 그룹을 만들어 매칭할 수 있습니다
                   </p>
                   <p>• 2-8명으로 구성된 그룹 단위로 매칭이 진행됩니다</p>
                   <p>• 매칭이 성공하면 전용 채팅방이 생성됩니다</p>
                   <p>• 익명 모드로 채팅하거나 실명 모드로 채팅할 수 있습니다</p>
                 </CardContent>
               </Card>

               {/* Statistics Link */}
               <Card>
                 <CardHeader>
                   <CardTitle className="flex items-center gap-2">
                     <BarChart3 className="w-5 h-5" />
                     매칭 통계
                   </CardTitle>
                   <CardDescription>
                     매칭 풀과 제안에 대한 상세 통계를 확인하세요
                   </CardDescription>
                 </CardHeader>
                 <CardContent>
                   <Button
                     variant="outline"
                     className="w-full"
                     onClick={() => navigate({ to: "/matching/stats" })}
                   >
                     <BarChart3 className="w-4 h-4 mr-2" />
                     통계 보기
                   </Button>
                 </CardContent>
               </Card>

        {/* Create Pool Dialog */}
        <Dialog open={isCreating} onOpenChange={setIsCreating}>
          <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>매칭 풀 생성</DialogTitle>
              <DialogDescription>
                그룹 매칭을 위한 정보를 입력해주세요
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="university">학교</Label>
                  <Input
                    id="university"
                    placeholder="부경대학교"
                    value={formData.university || ""}
                    onChange={(e) =>
                      setFormData({ ...formData, university: e.target.value })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="department">학과</Label>
                  <Input
                    id="department"
                    placeholder="컴퓨터공학과"
                    value={formData.department || ""}
                    onChange={(e) =>
                      setFormData({ ...formData, department: e.target.value })
                    }
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="gender">성별 구성</Label>
                  <Select
                    value={formData.gender}
                    onValueChange={(value: "male" | "female" | "mixed") =>
                      setFormData({ ...formData, gender: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="male">남성</SelectItem>
                      <SelectItem value="female">여성</SelectItem>
                      <SelectItem value="mixed">혼성</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="matching_type">매칭 타입</Label>
                  <Select
                    value={formData.matching_type}
                    onValueChange={(value: "blind" | "open") =>
                      setFormData({ ...formData, matching_type: value })
                    }
                  >
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="blind">블라인드</SelectItem>
                      <SelectItem value="open">오픈</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="age_min">최소 나이</Label>
                  <Input
                    id="age_min"
                    type="number"
                    min="18"
                    max="100"
                    value={formData.age_range_min || 18}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        age_range_min: parseInt(e.target.value),
                      })
                    }
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="age_max">최대 나이</Label>
                  <Input
                    id="age_max"
                    type="number"
                    min="18"
                    max="100"
                    value={formData.age_range_max || 30}
                    onChange={(e) =>
                      setFormData({
                        ...formData,
                        age_range_max: parseInt(e.target.value),
                      })
                    }
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">소개 메시지 (선택)</Label>
                <Input
                  id="description"
                  placeholder="안녕하세요! 같이 공부해요"
                  value={formData.description || ""}
                  onChange={(e) =>
                    setFormData({ ...formData, description: e.target.value })
                  }
                />
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button
                  variant="outline"
                  onClick={() => setIsCreating(false)}
                  disabled={createPoolMutation.isPending}
                >
                  취소
                </Button>
                <Button
                  onClick={handleCreatePool}
                  disabled={createPoolMutation.isPending}
                >
                  생성
                </Button>
              </div>
            </div>
          </DialogContent>
        </Dialog>
      </div>
    </PageTransition>
  );
}
