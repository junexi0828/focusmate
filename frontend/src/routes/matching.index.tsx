import { useState } from "react";
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
import { Switch } from "../components/ui/switch";
import {
  Heart,
  Users2,
  UserPlus,
  CheckCircle2,
  XCircle,
  Clock,
  BarChart3,
} from "lucide-react";
import { format } from "date-fns";
import { ko } from "date-fns/locale";
import type {
  MatchingPoolCreate,
  MatchingPool,
  MatchingProposal,
} from "../types/matching";
import {
  VerificationStatus,
  VerificationSettings,
} from "../features/verification";

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
  const [isPinkCampusTrialMode, setIsPinkCampusTrialMode] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [formData, setFormData] = useState<Partial<MatchingPoolCreate>>({
    member_ids: [],
    gender: "mixed",
    matching_type: "open",
    age_range_min: 18,
    age_range_max: 30,
  });

  // 데모 모드: 로컬 상태로 관리되는 매칭 풀 및 제안
  const [demoPool, setDemoPool] = useState<MatchingPool | null>(null);
  const [demoProposals, setDemoProposals] = useState<MatchingProposal[]>([]);
  const demoStats = {
    total_waiting: 5,
    average_wait_time_hours: 2.5,
    by_member_count: { "3": 2, "4": 2, "5": 1 },
  };

  const { data: stats } = useQuery({
    queryKey: ["matching", "stats"],
    queryFn: () => matchingApi.getPoolStats(),
    initialData: initialData.stats,
    enabled: !isPinkCampusTrialMode, // 데모 모드에서는 API 호출 안 함
  });

  const { data: myPool, refetch: refetchPool } = useQuery({
    queryKey: ["matching", "myPool"],
    queryFn: () => matchingApi.getMyPool().catch(() => null),
    initialData: initialData.myPool,
    enabled: !isPinkCampusTrialMode, // 데모 모드에서는 API 호출 안 함
  });

  const { data: proposals = [], refetch: refetchProposals } = useQuery({
    queryKey: ["matching", "proposals"],
    queryFn: () => matchingApi.getMyProposals(),
    initialData: initialData.proposals,
    enabled: !isPinkCampusTrialMode, // 데모 모드에서는 API 호출 안 함
  });

  // 데모 모드와 실제 모드 분리
  const displayStats = isPinkCampusTrialMode ? demoStats : stats;
  const displayMyPool = isPinkCampusTrialMode ? demoPool : myPool;
  const displayProposals = isPinkCampusTrialMode ? demoProposals : proposals;

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
      const errorObj = error as { response?: { data?: { detail?: unknown } } };
      const detail = errorObj?.response?.data?.detail;
      const message =
        typeof detail === "string"
          ? detail
          : Array.isArray(detail)
            ? detail
                .map((e: { msg?: string } | string) =>
                  typeof e === "string" ? e : e.msg || String(e)
                )
                .join(", ")
            : "매칭 풀 생성에 실패했습니다";
      toast.error(message);
    },
  });

  // 데모 모드: 매칭 풀 생성
  const handleDemoCreatePool = () => {
    if (!formData.university || !formData.department) {
      toast.error("학교와 학과를 입력해주세요");
      return;
    }

    const user = authService.getCurrentUser();
    const newPool: MatchingPool = {
      pool_id: `demo-${Date.now()}`,
      creator_id: user?.id || "demo-user",
      member_ids: [user?.id || "demo-user"],
      member_count: formData.member_ids?.length || 1,
      gender: formData.gender || "mixed",
      department: formData.department,
      grade: "3",
      preferred_match_type: formData.matching_type || "open",
      preferred_categories: [],
      matching_type: formData.matching_type || "open",
      message: formData.description || null,
      status: "waiting",
      created_at: new Date().toISOString(),
      expires_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
      updated_at: new Date().toISOString(),
    };

    setDemoPool(newPool);
    setIsCreating(false);
    toast.success("데모 매칭 풀이 생성되었습니다!");

    // 2초 후 샘플 제안 생성 시뮬레이션
    setTimeout(() => {
      const sampleProposal: MatchingProposal = {
        proposal_id: `demo-proposal-${Date.now()}`,
        pool_id_a: newPool.pool_id,
        pool_id_b: `demo-pool-other-${Date.now()}`,
        group_a_status: "pending",
        group_b_status: "pending",
        final_status: "pending",
        chat_room_id: null,
        created_at: new Date().toISOString(),
        expires_at: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(),
        matched_at: null,
        pool_a: newPool,
        pool_b: {
          pool_id: `demo-pool-other-${Date.now()}`,
          creator_id: "demo-other-user",
          member_ids: ["demo-other-user"],
          member_count: formData.member_ids?.length || 1,
          gender: formData.gender || "mixed",
          department: formData.department || "컴퓨터공학과",
          grade: "3",
          preferred_match_type: formData.matching_type || "open",
          preferred_categories: [],
          matching_type: formData.matching_type || "open",
          message: "안녕하세요! 같이 공부해요",
          status: "waiting",
          created_at: new Date().toISOString(),
          expires_at: new Date(
            Date.now() + 7 * 24 * 60 * 60 * 1000
          ).toISOString(),
          updated_at: new Date().toISOString(),
        },
      };
      setDemoProposals((prev) => [sampleProposal, ...prev]);
      toast.info("새로운 매칭 제안이 도착했습니다!");
    }, 2000);

    setFormData({
      member_ids: [],
      gender: "mixed",
      matching_type: "open",
      age_range_min: 18,
      age_range_max: 30,
    });
  };

  // 데모 모드: 매칭 풀 취소
  const handleDemoCancelPool = () => {
    setDemoPool(null);
    setDemoProposals([]);
    toast.success("데모 매칭 풀이 취소되었습니다");
  };

  // 데모 모드: 제안 응답
  const handleDemoRespondToProposal = (
    proposalId: string,
    action: "accept" | "reject"
  ) => {
    setDemoProposals((prev) =>
      prev.map((proposal) => {
        if (proposal.proposal_id === proposalId) {
          if (action === "accept") {
            return {
              ...proposal,
              group_a_status: "accepted",
              final_status: "matched",
              matched_at: new Date().toISOString(),
              chat_room_id: `demo-chat-${Date.now()}`,
            };
          } else {
            return {
              ...proposal,
              group_a_status: "rejected",
              final_status: "rejected",
            };
          }
        }
        return proposal;
      })
    );

    if (action === "accept") {
      toast.success("매칭이 성사되었습니다! 데모 채팅방이 생성되었습니다.");
    } else {
      toast.info("제안이 거절되었습니다");
    }
  };

  const handleCreatePool = () => {
    if (isPinkCampusTrialMode) {
      handleDemoCreatePool();
      return;
    }

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
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold tracking-tight flex items-center gap-3">
              <Heart className="w-10 h-10 text-[#F9A8D4]" />
              핑크캠퍼스
            </h1>
            <p className="text-muted-foreground mt-2">
              같은 학교 친구들과 그룹 매칭을 통해 함께 공부하세요
            </p>
          </div>

          {/* 핑크 캠퍼스 체험하기 토글 */}
          <div className="flex items-center gap-2 px-3 py-2 rounded-lg border bg-gradient-to-r from-pink-50 to-rose-50 dark:from-pink-950/20 dark:to-rose-950/20 border-pink-200 dark:border-pink-800 hover:bg-gradient-to-r hover:from-pink-100 hover:to-rose-100 dark:hover:from-pink-950/30 dark:hover:to-rose-950/30 transition-colors">
            <Switch
              id="pink-campus-trial-mode"
              checked={isPinkCampusTrialMode}
              onCheckedChange={(checked: boolean) => {
                setIsPinkCampusTrialMode(checked);
                if (!checked) {
                  // 체험 모드 종료 시 데모 데이터 초기화
                  setDemoPool(null);
                  setDemoProposals([]);
                }
              }}
            />
            <Label
              htmlFor="pink-campus-trial-mode"
              className="cursor-pointer font-medium"
            >
              <span className="text-pink-600 dark:text-pink-400">
                핑크 캠퍼스
              </span>{" "}
              체험하기
            </Label>
          </div>
        </div>

        {/* 체험 모드 안내 */}
        {isPinkCampusTrialMode && (
          <Card className="border-pink-200 dark:border-pink-800 bg-gradient-to-r from-pink-50 to-rose-50 dark:from-pink-950/20 dark:to-rose-950/20">
            <CardContent className="pt-6">
              <div className="flex items-center gap-3">
                <div className="p-2 rounded-lg bg-pink-100 dark:bg-pink-900/30">
                  <Heart className="w-5 h-5 text-pink-600 dark:text-pink-400" />
                </div>
                <div className="flex-1">
                  <p className="font-semibold text-pink-900 dark:text-pink-100">
                    핑크 캠퍼스 체험하기 모드
                  </p>
                  <p className="text-sm text-pink-700 dark:text-pink-300 mt-1">
                    학교 인증 없이 핑크캠퍼스의 매칭 기능을 체험해보세요. DB
                    연동 없이 작동하는 데모 모드입니다.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Verification Status */}
        <VerificationStatus />

        {/* Stats */}
        {displayStats && (
          <div className="grid gap-4 md:grid-cols-4">
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>대기 중인 풀</CardDescription>
                <CardTitle className="text-3xl">
                  {displayStats.total_waiting}
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>평균 대기 시간</CardDescription>
                <CardTitle className="text-3xl">
                  {displayStats.average_wait_time_hours.toFixed(1)}h
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>그룹별 통계</CardDescription>
                <CardTitle className="text-2xl">
                  {Object.keys(displayStats.by_member_count).length > 0
                    ? Object.keys(displayStats.by_member_count).length
                    : "0"}{" "}
                  타입
                </CardTitle>
              </CardHeader>
            </Card>
            <Card>
              <CardHeader className="pb-2">
                <CardDescription>내 상태</CardDescription>
                <CardTitle className="text-2xl">
                  {displayMyPool ? (
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
              <Users2 className="w-5 h-5" />내 매칭 풀
            </CardTitle>
            <CardDescription>현재 참여 중인 매칭 풀 정보입니다</CardDescription>
          </CardHeader>
          <CardContent>
            {displayMyPool ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="font-medium">
                      {displayMyPool.member_count}명 그룹 매칭
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {displayMyPool.department || "학과 미지정"} ·{" "}
                      {displayMyPool.grade || "학년 미지정"} ·{" "}
                      {displayMyPool.gender || "성별 미지정"}
                    </p>
                    {displayMyPool.message && (
                      <p className="text-sm text-muted-foreground mt-2">
                        "{displayMyPool.message}"
                      </p>
                    )}
                  </div>
                  <Badge
                    variant={
                      displayMyPool.status === "waiting"
                        ? "default"
                        : "secondary"
                    }
                  >
                    {displayMyPool.status === "waiting"
                      ? "대기 중"
                      : displayMyPool.status}
                  </Badge>
                </div>
                <Button
                  variant="destructive"
                  size="sm"
                  onClick={() => {
                    if (isPinkCampusTrialMode) {
                      handleDemoCancelPool();
                    } else if (displayMyPool?.pool_id) {
                      cancelPoolMutation.mutate(displayMyPool.pool_id);
                    }
                  }}
                  disabled={
                    !isPinkCampusTrialMode && cancelPoolMutation.isPending
                  }
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
              <Heart className="w-5 h-5 text-[#F9A8D4]" />
              매칭 제안
            </CardTitle>
            <CardDescription>
              받은 매칭 제안을 확인하고 수락/거절하세요
            </CardDescription>
          </CardHeader>
          <CardContent>
            {displayProposals.length > 0 ? (
              <div className="space-y-4">
                {displayProposals.map((proposal) => (
                  <div
                    key={proposal.proposal_id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50 transition-colors cursor-pointer"
                    onClick={() =>
                      navigate({
                        to: "/matching/proposals/$proposalId",
                        params: { proposalId: proposal.proposal_id },
                      })
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
                        {format(
                          new Date(proposal.created_at),
                          "yyyy년 M월 d일 HH:mm",
                          {
                            locale: ko,
                          }
                        )}
                      </p>
                    </div>
                    <div
                      className="flex gap-2"
                      onClick={(e) => e.stopPropagation()}
                    >
                      {proposal.final_status === "pending" && (
                        <>
                          <Button
                            size="sm"
                            onClick={() => {
                              if (isPinkCampusTrialMode) {
                                handleDemoRespondToProposal(
                                  proposal.proposal_id,
                                  "accept"
                                );
                              } else {
                                respondToProposalMutation.mutate({
                                  proposalId: proposal.proposal_id,
                                  action: { action: "accept" },
                                });
                              }
                            }}
                            disabled={
                              !isPinkCampusTrialMode &&
                              respondToProposalMutation.isPending
                            }
                          >
                            <CheckCircle2 className="w-4 h-4 mr-1" />
                            수락
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              if (isPinkCampusTrialMode) {
                                handleDemoRespondToProposal(
                                  proposal.proposal_id,
                                  "reject"
                                );
                              } else {
                                respondToProposalMutation.mutate({
                                  proposalId: proposal.proposal_id,
                                  action: { action: "reject" },
                                });
                              }
                            }}
                            disabled={
                              !isPinkCampusTrialMode &&
                              respondToProposalMutation.isPending
                            }
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
                          navigate({
                            to: "/matching/proposals/$proposalId",
                            params: { proposalId: proposal.proposal_id },
                          })
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
        <Card className="border-[#F9A8D4]/30 bg-[#FCE7F5] dark:bg-[#F9A8D4]/20">
          <CardHeader>
            <CardTitle className="text-[#F9A8D4] dark:text-[#F9A8D4]">
              핑크캠퍼스란?
            </CardTitle>
          </CardHeader>
          <CardContent className="text-sm text-[#F9A8D4] dark:text-[#F9A8D4] space-y-2">
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
