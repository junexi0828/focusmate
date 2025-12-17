import { useState } from "react";
import { Avatar, AvatarFallback } from "../../../components/ui/avatar";
import { Button } from "../../../components/ui/button";
import { User } from "../../../types/user";
import { Settings, Edit } from "lucide-react";
import { ProfileEditDialog } from "./ProfileEditDialog";
import { useNavigate } from "@tanstack/react-router";

interface ProfileHeaderProps {
  user: User;
  isOwnProfile?: boolean;
  onEdit?: () => void;
  onSettings?: () => void;
  onUpdate?: (user: User) => void;
}

export function ProfileHeader({
  user,
  isOwnProfile = false,
  onEdit,
  onSettings,
  onUpdate,
}: ProfileHeaderProps) {
  const navigate = useNavigate();
  const [editDialogOpen, setEditDialogOpen] = useState(false);

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

  const handleEdit = () => {
    if (onEdit) {
      onEdit();
    } else {
      setEditDialogOpen(true);
    }
  };

  const handleSettings = () => {
    if (onSettings) {
      onSettings();
    } else {
      navigate({ to: "/settings" });
    }
  };

  const handleUpdate = (updatedUser: User) => {
    if (onUpdate) {
      onUpdate(updatedUser);
    }
  };

  return (
    <div className="bg-background border-b">
      <div className="container mx-auto px-4 py-6 max-w-5xl">
        <div className="flex flex-col sm:flex-row gap-6 items-start sm:items-center">
          {/* 아바타 (Discourse 스타일) */}
          <Avatar className="w-20 h-20 sm:w-24 sm:h-24 flex-shrink-0">
            <AvatarFallback className="bg-primary text-primary-foreground text-2xl sm:text-3xl">
              {getInitials(user.name)}
            </AvatarFallback>
          </Avatar>

          {/* 사용자 정보 */}
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between gap-4 mb-2">
              <div className="min-w-0">
                <h1 className="text-2xl sm:text-3xl font-bold truncate">
                  {user.name}
                </h1>
                <p className="text-sm text-muted-foreground mt-1">
                  {user.email}
                </p>
                {user.bio && (
                  <p className="text-sm text-muted-foreground mt-2 line-clamp-2">
                    {user.bio}
                  </p>
                )}
              </div>

              {/* 액션 버튼 (자신의 프로필일 때만) */}
              {isOwnProfile && (
                <div className="flex gap-2 flex-shrink-0">
                  <Button variant="outline" size="sm" onClick={handleEdit}>
                    <Edit className="w-4 h-4 mr-2" />
                    수정
                  </Button>
                  <Button variant="outline" size="sm" onClick={handleSettings}>
                    <Settings className="w-4 h-4 mr-2" />
                    설정
                  </Button>
                </div>
              )}
            </div>

            {/* 메타 정보 (Discourse 스타일) */}
            <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mt-3">
              <span>가입일: {formatDate(user.createdAt)}</span>
              <span>•</span>
              <span>세션: {user.totalSessions}개</span>
              <span>•</span>
              <span>
                집중 시간: {Math.floor(user.totalFocusTime / 60)}시간{" "}
                {user.totalFocusTime % 60}분
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Profile Edit Dialog */}
      <ProfileEditDialog
        user={user}
        open={editDialogOpen}
        onOpenChange={setEditDialogOpen}
        onUpdate={handleUpdate}
      />
    </div>
  );
}

