import { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button-enhanced";
import { TabsContent } from "../components/ui/tabs";
import { Label } from "../components/ui/label";
import { User } from "../types/user";
import {
  User as UserIcon,
  Mail,
  Calendar,
  Target,
  Award,
  MessageSquare,
  CheckCircle2,
} from "lucide-react";
import { achievementIcons, type AchievementId } from "../assets/achievements";
import { toast } from "sonner";
import {
  ProfileHeader,
  ProfileTabs,
  ProfileEditDialog,
} from "../features/profile/components";
import { StatCard } from "../features/stats/components";
import { useNavigate } from "@tanstack/react-router";
import { formatDistanceToNow } from "date-fns";
import { ko } from "date-fns/locale";
import { Badge } from "../components/ui/badge";
import { Progress } from "../components/ui/progress";
import type { AchievementProgress } from "../features/achievements/services/achievementService";
import type { Post } from "../features/community/services/communityService";
import { NotificationSettings } from "../features/notification/components/NotificationSettings";
import { celebrateAchievement } from "../utils/confetti";

interface ProfilePageProps {
  user: User;
  achievements?: AchievementProgress[];
  userPosts?: Post[];
  onUpdateProfile: (updates: Partial<User>) => void;
  onLogout: () => void;
}

export function ProfilePage({
  user,
  achievements = [],
  userPosts = [],
  onUpdateProfile,
  onLogout,
}: ProfilePageProps) {
  const navigate = useNavigate();
  const [isEditDialogOpen, setIsEditDialogOpen] = useState(false);
  const [currentUser, setCurrentUser] = useState(user);
  const [activeTab, setActiveTab] = useState("overview");

  const handleUpdateProfile = (updatedUser: User) => {
    setCurrentUser(updatedUser);
    onUpdateProfile(updatedUser);
    toast.success("프로필이 업데이트되었습니다");
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="space-y-6">
      {/* Profile Header (Dashboard 스타일로 통일) */}
      <ProfileHeader
        user={currentUser}
        isOwnProfile={true}
        onEdit={() => setIsEditDialogOpen(true)}
        onUpdate={handleUpdateProfile}
      />

      {/* Profile Tabs (Discourse 스타일) */}
      <ProfileTabs activeTab={activeTab} onTabChange={setActiveTab}>
        {/* Overview Tab */}
        <TabsContent value="overview" className="mt-6">
          <div className="grid lg:grid-cols-3 gap-6">
            {/* Profile Info Card */}
            <div className="lg:col-span-2">
              <Card>
                <CardHeader>
                  <CardTitle>프로필 정보</CardTitle>
                  <CardDescription>개인 정보를 확인하세요</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div>
                    <Label className="text-muted-foreground">소개</Label>
                    <p className="mt-1">
                      {currentUser.bio || "아직 소개를 작성하지 않았습니다."}
                    </p>
                  </div>

                  {currentUser.school && (
                    <div>
                      <Label className="text-muted-foreground">학교</Label>
                      <p className="mt-1">{currentUser.school}</p>
                    </div>
                  )}

                  <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                    <div
                      key="email-info"
                      className="flex items-center gap-2 text-sm"
                    >
                      <Mail className="w-4 h-4 text-muted-foreground" />
                      <span className="text-muted-foreground">이메일:</span>
                      <span>{currentUser.email}</span>
                    </div>
                    <div
                      key="join-date-info"
                      className="flex items-center gap-2 text-sm"
                    >
                      <Calendar className="w-4 h-4 text-muted-foreground" />
                      <span className="text-muted-foreground">가입일:</span>
                      <span>{formatDate(currentUser.createdAt)}</span>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>

            {/* Stats Summary (Discourse 스타일) */}
            <div className="space-y-6">
              <div className="grid gap-4">
                {[
                  {
                    key: "total-focus-time",
                    title: "총 집중 시간",
                    value: `${Math.floor(currentUser.totalFocusTime / 60)}시간 ${currentUser.totalFocusTime % 60}분`,
                    icon: Target,
                    variant: "primary" as const,
                  },
                  {
                    key: "total-sessions",
                    title: "완료한 세션",
                    value: `${currentUser.totalSessions}개`,
                    icon: Award,
                    variant: "secondary" as const,
                  },
                  {
                    key: "avg-session-time",
                    title: "평균 세션 시간",
                    value: `${
                      currentUser.totalSessions > 0
                        ? Math.round(
                            currentUser.totalFocusTime /
                              currentUser.totalSessions
                          )
                        : 0
                    }분`,
                    icon: UserIcon,
                    variant: "default" as const,
                  },
                ].map((stat) => (
                  <StatCard
                    key={stat.key}
                    title={stat.title}
                    value={stat.value}
                    icon={stat.icon}
                    variant={stat.variant}
                  />
                ))}
              </div>

              <Card>
                <CardHeader>
                  <CardTitle>업적 미리보기</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {achievements
                    .filter((a) => a.is_unlocked)
                    .slice(0, 3)
                    .map((achievement, index) => {
                      const achievementId = achievement.achievement_id as AchievementId;
                      const iconSrc = achievementIcons[achievementId] || achievementIcons['first-session'];

                      return (
                      <div
                        key={
                          achievement.achievement_id || `achievement-${index}`
                        }
                        className="flex items-center gap-3 p-3 rounded-lg bg-muted/50 cursor-pointer hover:bg-muted transition-colors"
                        onClick={() => celebrateAchievement()}
                        role="button"
                        tabIndex={0}
                        aria-label={`${achievement.achievement_name} 업적 축하하기`}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' || e.key === ' ') {
                            e.preventDefault();
                            celebrateAchievement();
                          }
                        }}
                      >
                        <div className="w-10 h-10 flex items-center justify-center" aria-hidden="true">
                          <img src={iconSrc} alt="" className="w-10 h-10" />
                        </div>
                        <div className="flex-1 min-w-0">
                          <p className="text-sm font-medium truncate">
                            {achievement.achievement_name}
                          </p>
                          <p className="text-xs text-muted-foreground truncate">
                            {achievement.achievement_description}
                          </p>
                        </div>
                      </div>
                    );
                    })}
                  {achievements.filter((a) => a.is_unlocked).length === 0 && (
                    <p className="text-sm text-muted-foreground text-center py-4">
                      아직 획득한 업적이 없습니다
                    </p>
                  )}
                  {achievements.filter((a) => a.is_unlocked).length > 3 && (
                    <Button
                      variant="ghost"
                      size="sm"
                      className="w-full"
                      onClick={() => setActiveTab("achievements")}
                    >
                      모든 업적 보기
                    </Button>
                  )}
                </CardContent>
              </Card>
            </div>
          </div>
        </TabsContent>

        {/* Activity Tab */}
        <TabsContent value="activity" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>최근 활동</CardTitle>
              <CardDescription>최근 게시글 및 댓글</CardDescription>
            </CardHeader>
            <CardContent>
              {userPosts.length === 0 ? (
                <p className="text-muted-foreground text-center py-8">
                  활동 내역이 없습니다
                </p>
              ) : (
                <div className="space-y-4">
                  {userPosts.map((post) => (
                    <div
                      key={post.id}
                      className="flex items-start gap-4 p-4 rounded-lg border hover:bg-muted/50 transition-colors cursor-pointer"
                      onClick={() => navigate({ to: `/community/${post.id}` })}
                    >
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2">
                          <Badge variant="outline" className="text-xs">
                            {post.category === "tips" && "팁"}
                            {post.category === "question" && "질문"}
                            {post.category === "achievement" && "성취"}
                            {post.category === "general" && "일반"}
                          </Badge>
                          <span className="text-xs text-muted-foreground">
                            {formatDistanceToNow(new Date(post.created_at), {
                              addSuffix: true,
                              locale: ko,
                            })}
                          </span>
                        </div>
                        <h3 className="font-semibold mb-1 line-clamp-1">
                          {post.title}
                        </h3>
                        <p className="text-sm text-muted-foreground line-clamp-2">
                          {post.content}
                        </p>
                        <div className="flex items-center gap-4 mt-2 text-xs text-muted-foreground">
                          <span className="flex items-center gap-1">
                            <MessageSquare className="w-3 h-3" />
                            {post.comment_count}
                          </span>
                          <span className="flex items-center gap-1">
                            <Award className="w-3 h-3" />
                            {post.likes}
                          </span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Stats Tab */}
        <TabsContent value="stats" className="mt-6">
          <Card>
            <CardHeader>
              <CardTitle>상세 통계</CardTitle>
              <CardDescription>집중 시간 및 세션 분석</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid sm:grid-cols-2 gap-4">
                {[
                  {
                    key: "stats-total-focus-time",
                    title: "총 집중 시간",
                    value: `${Math.floor(currentUser.totalFocusTime / 60)}시간 ${currentUser.totalFocusTime % 60}분`,
                    icon: Target,
                    variant: "primary" as const,
                  },
                  {
                    key: "stats-total-sessions",
                    title: "완료한 세션",
                    value: `${currentUser.totalSessions}개`,
                    icon: Award,
                    variant: "secondary" as const,
                  },
                ].map((stat) => (
                  <StatCard
                    key={stat.key}
                    title={stat.title}
                    value={stat.value}
                    icon={stat.icon}
                    variant={stat.variant}
                  />
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Achievements Tab */}
        <TabsContent value="achievements" className="mt-6">
          <div className="space-y-6">
            {/* Unlocked Achievements */}
            <Card>
              <CardHeader>
                <CardTitle>획득한 업적</CardTitle>
                <CardDescription>
                  {achievements.filter((a) => a.is_unlocked).length}개의 업적을
                  획득했습니다
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {achievements
                  .filter((a) => a.is_unlocked)
                  .map((achievement, index) => {
                    const achievementId = achievement.achievement_id as AchievementId;
                    const iconSrc = achievementIcons[achievementId] || achievementIcons['first-session'];

                    return (
                    <div
                      key={
                        achievement.achievement_id ||
                        `unlocked-achievement-${index}`
                      }
                      className="flex items-center gap-4 p-4 rounded-lg bg-primary/5 border border-primary/20"
                    >
                      <div className="w-16 h-16 flex items-center justify-center flex-shrink-0">
                        <img src={iconSrc} alt={achievement.achievement_name} className="w-16 h-16" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-semibold">
                            {achievement.achievement_name}
                          </p>
                          <Badge variant="secondary" className="text-xs">
                            {achievement.achievement_category}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground">
                          {achievement.achievement_description}
                        </p>
                        {achievement.unlocked_at && (
                          <p className="text-xs text-muted-foreground mt-1">
                            획득일:{" "}
                            {formatDistanceToNow(
                              new Date(achievement.unlocked_at),
                              {
                                addSuffix: true,
                                locale: ko,
                              }
                            )}
                          </p>
                        )}
                      </div>
                      <CheckCircle2 className="w-5 h-5 text-primary flex-shrink-0" />
                    </div>
                  );
                  })}
                {achievements.filter((a) => a.is_unlocked).length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    아직 획득한 업적이 없습니다
                  </p>
                )}
              </CardContent>
            </Card>

            {/* In Progress Achievements */}
            <Card>
              <CardHeader>
                <CardTitle>진행 중인 업적</CardTitle>
                <CardDescription>
                  {achievements.filter((a) => !a.is_unlocked).length}개의 업적을
                  진행 중입니다
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {achievements
                  .filter((a) => !a.is_unlocked)
                  .map((achievement, index) => {
                    const achievementId = achievement.achievement_id as AchievementId;
                    const iconSrc = achievementIcons[achievementId] || achievementIcons['first-session'];

                    return (
                    <div
                      key={
                        achievement.achievement_id ||
                        `locked-achievement-${index}`
                      }
                      className="flex items-start gap-4 p-4 rounded-lg bg-muted/50 border"
                    >
                      <div className="w-16 h-16 flex items-center justify-center flex-shrink-0">
                        <img src={iconSrc} alt={achievement.achievement_name} className="w-16 h-16 opacity-30 grayscale" />
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-1">
                          <p className="font-semibold">
                            {achievement.achievement_name}
                          </p>
                          <Badge variant="outline" className="text-xs">
                            {achievement.achievement_category}
                          </Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">
                          {achievement.achievement_description}
                        </p>
                        <div className="space-y-2">
                          <div className="flex items-center justify-between text-xs">
                            <span className="text-muted-foreground">
                              진행률: {achievement.current_progress} /{" "}
                              {achievement.requirement_value}
                            </span>
                            <span className="font-medium">
                              {achievement.progress_percentage.toFixed(0)}%
                            </span>
                          </div>
                          <Progress
                            value={achievement.progress_percentage}
                            className="h-2"
                          />
                        </div>
                      </div>
                    </div>
                  );
                  })}
                {achievements.filter((a) => !a.is_unlocked).length === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-8">
                    모든 업적을 획득했습니다! 🎉
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Settings Tab */}
        <TabsContent value="settings" className="mt-6">
          <div className="space-y-6">
            {/* Profile Edit Card */}
            <Card>
              <CardHeader>
                <CardTitle>프로필 수정</CardTitle>
                <CardDescription>개인 정보를 관리하세요</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <Button onClick={() => setIsEditDialogOpen(true)}>
                  프로필 수정
                </Button>
                <ProfileEditDialog
                  user={currentUser}
                  open={isEditDialogOpen}
                  onOpenChange={setIsEditDialogOpen}
                  onUpdate={handleUpdateProfile}
                />
              </CardContent>
            </Card>

            {/* Notification Settings */}
            <NotificationSettings />

            {/* Account Management */}
            <Card>
              <CardHeader>
                <CardTitle>계정 관리</CardTitle>
                <CardDescription>계정 관련 설정</CardDescription>
              </CardHeader>
              <CardContent>
                <Button variant="destructive" onClick={onLogout}>
                  로그아웃
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </ProfileTabs>
    </div>
  );
}
