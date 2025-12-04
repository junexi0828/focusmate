import React, { useState } from "react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "../components/ui/card";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";
import { Textarea } from "../components/ui/textarea";
import { Avatar, AvatarFallback } from "../components/ui/avatar";
import { User } from "../types/user";
import {
  User as UserIcon,
  Mail,
  Calendar,
  TrendingUp,
  Target,
  Award,
} from "lucide-react";
import { toast } from "sonner";

interface ProfilePageProps {
  user: User;
  onUpdateProfile: (updates: Partial<User>) => void;
  onLogout: () => void;
}

export function ProfilePage({
  user,
  onUpdateProfile,
  onLogout,
}: ProfilePageProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user.name);
  const [bio, setBio] = useState(user.bio || "");

  const handleSave = () => {
    onUpdateProfile({ name, bio });
    setIsEditing(false);
    toast.success("프로필이 업데이트되었습니다");
  };

  const handleCancel = () => {
    setName(user.name);
    setBio(user.bio || "");
    setIsEditing(false);
  };

  const getInitials = (name: string) => {
    const words = name.trim().split(" ");
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString("ko-KR", {
      year: "numeric",
      month: "long",
      day: "numeric",
    });
  };

  return (
    <div className="min-h-screen bg-muted/30">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* Header */}
        <div className="mb-8">
          <h1>마이페이지</h1>
          <p className="text-muted-foreground">프로필 및 활동 정보</p>
        </div>

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Profile Card */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>프로필 정보</CardTitle>
                <CardDescription>개인 정보를 관리하세요</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                {/* Avatar */}
                <div className="flex items-center gap-6">
                  <Avatar className="w-24 h-24">
                    <AvatarFallback className="bg-primary text-primary-foreground text-2xl">
                      {getInitials(user.name)}
                    </AvatarFallback>
                  </Avatar>
                  {!isEditing && (
                    <div>
                      <h3>{user.name}</h3>
                      <p className="text-sm text-muted-foreground">
                        {user.email}
                      </p>
                    </div>
                  )}
                </div>

                {/* Form Fields */}
                {isEditing ? (
                  <div className="space-y-4">
                    <div className="space-y-2">
                      <Label htmlFor="profile-name">이름</Label>
                      <Input
                        id="profile-name"
                        value={name}
                        onChange={(e) => setName(e.target.value)}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="profile-bio">소개</Label>
                      <Textarea
                        id="profile-bio"
                        value={bio}
                        onChange={(e) => setBio(e.target.value)}
                        placeholder="자신을 소개해주세요"
                        rows={4}
                      />
                    </div>

                    <div className="flex gap-2">
                      <Button onClick={handleSave}>저장</Button>
                      <Button variant="outline" onClick={handleCancel}>
                        취소
                      </Button>
                    </div>
                  </div>
                ) : (
                  <div className="space-y-4">
                    <div>
                      <Label className="text-muted-foreground">소개</Label>
                      <p className="mt-1">
                        {user.bio || "아직 소개를 작성하지 않았습니다."}
                      </p>
                    </div>

                    <div className="grid grid-cols-2 gap-4 pt-4 border-t">
                      <div className="flex items-center gap-2 text-sm">
                        <Mail className="w-4 h-4 text-muted-foreground" />
                        <span className="text-muted-foreground">이메일:</span>
                        <span>{user.email}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm">
                        <Calendar className="w-4 h-4 text-muted-foreground" />
                        <span className="text-muted-foreground">가입일:</span>
                        <span>{formatDate(user.createdAt)}</span>
                      </div>
                    </div>

                    <Button onClick={() => setIsEditing(true)}>
                      프로필 수정
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>

            {/* Logout */}
            <Card className="mt-6">
              <CardHeader>
                <CardTitle>계정 관리</CardTitle>
              </CardHeader>
              <CardContent>
                <Button variant="destructive" onClick={onLogout}>
                  로그아웃
                </Button>
              </CardContent>
            </Card>
          </div>

          {/* Stats Summary */}
          <div className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <TrendingUp className="w-5 h-5" />
                  활동 통계
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="p-4 rounded-lg bg-primary/10 border border-primary/20">
                  <div className="flex items-center gap-2 mb-2">
                    <Target className="w-4 h-4 text-primary" />
                    <p className="text-sm text-muted-foreground">
                      총 집중 시간
                    </p>
                  </div>
                  <p className="text-2xl text-primary">
                    {Math.floor(user.totalFocusTime / 60)}시간{" "}
                    {user.totalFocusTime % 60}분
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-secondary/10 border border-secondary/20">
                  <div className="flex items-center gap-2 mb-2">
                    <Award className="w-4 h-4 text-secondary" />
                    <p className="text-sm text-muted-foreground">완료한 세션</p>
                  </div>
                  <p className="text-2xl text-secondary">
                    {user.totalSessions}개
                  </p>
                </div>

                <div className="p-4 rounded-lg bg-muted border">
                  <div className="flex items-center gap-2 mb-2">
                    <UserIcon className="w-4 h-4" />
                    <p className="text-sm text-muted-foreground">
                      평균 세션 시간
                    </p>
                  </div>
                  <p className="text-2xl">
                    {user.totalSessions > 0
                      ? Math.round(user.totalFocusTime / user.totalSessions)
                      : 0}
                    분
                  </p>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>업적</CardTitle>
              </CardHeader>
              <CardContent className="space-y-3">
                {user.totalSessions >= 10 && (
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <div className="w-10 h-10 rounded-full bg-yellow-500 flex items-center justify-center">
                      🏆
                    </div>
                    <div>
                      <p className="text-sm font-medium">초보 집중러</p>
                      <p className="text-xs text-muted-foreground">
                        10개 세션 달성
                      </p>
                    </div>
                  </div>
                )}

                {user.totalFocusTime >= 300 && (
                  <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                    <div className="w-10 h-10 rounded-full bg-blue-500 flex items-center justify-center">
                      ⭐
                    </div>
                    <div>
                      <p className="text-sm font-medium">5시간 마스터</p>
                      <p className="text-xs text-muted-foreground">
                        5시간 집중 달성
                      </p>
                    </div>
                  </div>
                )}

                {user.totalSessions === 0 && (
                  <p className="text-sm text-muted-foreground text-center py-4">
                    아직 획득한 업적이 없습니다
                  </p>
                )}
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
}
