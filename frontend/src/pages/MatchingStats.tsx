import React from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import {
  TrendingUp,
  Users,
  Clock,
  CheckCircle2,
  XCircle,
  Hourglass,
  BarChart3,
  PieChart,
  Calendar,
  Activity,
} from "lucide-react";
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart as RechartsPieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from "recharts";

interface MatchingStatsPageProps {
  stats: {
    pools: {
      total_waiting: number;
      total_all: number;
      total_matched: number;
      total_expired: number;
      by_status: Record<string, number>;
      by_member_count: Record<string, number>;
      by_gender: Record<string, number>;
      by_department: Record<string, number>;
      by_matching_type: Record<string, number>;
      average_wait_time_hours: number;
    };
    proposals: {
      total_proposals: number;
      by_status: Record<string, number>;
      matched_count: number;
      success_rate: number;
      acceptance_rate: number;
      rejection_rate: number;
      pending_count: number;
      average_matching_time_hours: number;
      min_matching_time_hours: number;
      max_matching_time_hours: number;
      daily_matches: Array<{ date: string; count: number }>;
      weekly_matches: Array<{ week: string; count: number }>;
      monthly_matches: Array<{ month: string; count: number }>;
    };
  };
}

const COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

export function MatchingStatsPage({ stats }: MatchingStatsPageProps) {
  // Prepare chart data
  const statusData = Object.entries(stats.pools.by_status).map(([name, value]) => ({
    name: name === "waiting" ? "대기 중" : name === "matched" ? "매칭 완료" : name === "expired" ? "만료됨" : name === "cancelled" ? "취소됨" : name,
    value,
  }));

  const genderData = Object.entries(stats.pools.by_gender).map(([name, value]) => ({
    name: name === "male" ? "남성" : name === "female" ? "여성" : "혼성",
    value,
  }));

  const memberCountData = Object.entries(stats.pools.by_member_count)
    .map(([name, value]) => ({
      name: `${name}명`,
      value,
    }))
    .sort((a, b) => parseInt(a.name) - parseInt(b.name));

  const dailyMatchesData = stats.proposals.daily_matches
    .slice(-30)
    .reverse()
    .map((item) => ({
      date: new Date(item.date).toLocaleDateString("ko-KR", {
        month: "short",
        day: "numeric",
      }),
      count: item.count,
    }));

  const weeklyMatchesData = stats.proposals.weekly_matches
    .slice(-12)
    .reverse()
    .map((item) => ({
      week: new Date(item.week).toLocaleDateString("ko-KR", {
        month: "short",
        day: "numeric",
      }),
      count: item.count,
    }));

  const departmentData = Object.entries(stats.pools.by_department)
    .map(([name, value]) => ({ name, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 10);

  return (
    <div className="min-h-screen bg-muted/30">
      <div className="container mx-auto px-4 py-6 max-w-7xl">
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-3xl font-bold mb-2">매칭 통계</h1>
          <p className="text-muted-foreground">
            매칭 풀과 제안에 대한 종합 통계를 확인하세요
          </p>
        </div>

        {/* Key Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>매칭 성공률</CardDescription>
              <CardTitle className="text-3xl">
                {stats.proposals.success_rate.toFixed(1)}%
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <CheckCircle2 className="w-4 h-4" />
                <span>
                  {stats.proposals.matched_count} / {stats.proposals.total_proposals} 제안
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>평균 대기 시간</CardDescription>
              <CardTitle className="text-3xl">
                {stats.pools.average_wait_time_hours.toFixed(1)}h
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Clock className="w-4 h-4" />
                <span>현재 대기 중인 풀 기준</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>활성 매칭 풀</CardDescription>
              <CardTitle className="text-3xl">
                {stats.pools.total_waiting}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Users className="w-4 h-4" />
                <span>총 {stats.pools.total_all}개 중</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>평균 매칭 시간</CardDescription>
              <CardTitle className="text-3xl">
                {stats.proposals.average_matching_time_hours.toFixed(1)}h
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Activity className="w-4 h-4" />
                <span>
                  최소 {stats.proposals.min_matching_time_hours.toFixed(1)}h ~ 최대{" "}
                  {stats.proposals.max_matching_time_hours.toFixed(1)}h
                </span>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Pool Statistics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <PieChart className="w-5 h-5" />
                풀 상태 분포
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <RechartsPieChart>
                  <Pie
                    data={statusData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) =>
                      `${name} ${(percent * 100).toFixed(0)}%`
                    }
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {statusData.map((entry, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={COLORS[index % COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip />
                </RechartsPieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                성별 분포
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={genderData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Proposal Statistics */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <TrendingUp className="w-5 h-5" />
                일일 매칭 추이 (최근 30일)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={dailyMatchesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="count"
                    stroke="#3b82f6"
                    name="매칭 수"
                  />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Calendar className="w-5 h-5" />
                주간 매칭 추이 (최근 12주)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={weeklyMatchesData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="week" />
                  <YAxis />
                  <Tooltip />
                  <Bar dataKey="count" fill="#10b981" name="매칭 수" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </div>

        {/* Detailed Statistics */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Users className="w-5 h-5" />
                인원별 분포
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {memberCountData.map((item) => (
                  <div key={item.name} className="flex items-center justify-between">
                    <span className="text-sm">{item.name}</span>
                    <Badge variant="secondary">{item.value}개</Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5" />
                제안 상태
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                    <span className="text-sm">매칭 완료</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">
                      {stats.proposals.matched_count}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      ({stats.proposals.success_rate.toFixed(1)}%)
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <XCircle className="w-4 h-4 text-red-500" />
                    <span className="text-sm">거절됨</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">
                      {stats.proposals.by_status.rejected || 0}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      ({stats.proposals.rejection_rate.toFixed(1)}%)
                    </span>
                  </div>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <Hourglass className="w-4 h-4 text-yellow-500" />
                    <span className="text-sm">대기 중</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <span className="font-medium">
                      {stats.proposals.pending_count}
                    </span>
                    <span className="text-sm text-muted-foreground">
                      (
                      {stats.proposals.total_proposals > 0
                        ? (
                            (stats.proposals.pending_count /
                              stats.proposals.total_proposals) *
                            100
                          ).toFixed(1)
                        : 0}
                      %)
                    </span>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Activity className="w-5 h-5" />
                학과별 분포 (상위 10)
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {departmentData.map((item) => (
                  <div key={item.name} className="flex items-center justify-between">
                    <span className="text-sm truncate flex-1">{item.name}</span>
                    <Badge variant="outline" className="ml-2">
                      {item.value}
                    </Badge>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <Card>
            <CardHeader className="pb-2">
              <CardDescription>총 매칭 풀</CardDescription>
              <CardTitle className="text-2xl">{stats.pools.total_all}</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                매칭 완료: {stats.pools.total_matched} | 만료:{" "}
                {stats.pools.total_expired}
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>총 제안 수</CardDescription>
              <CardTitle className="text-2xl">
                {stats.proposals.total_proposals}
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                수락률: {stats.proposals.acceptance_rate.toFixed(1)}%
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader className="pb-2">
              <CardDescription>매칭 타입</CardDescription>
              <CardTitle className="text-2xl">
                {Object.keys(stats.pools.by_matching_type).length}종류
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-sm text-muted-foreground">
                블라인드: {stats.pools.by_matching_type.blind || 0} | 공개:{" "}
                {stats.pools.by_matching_type.open || 0}
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}

