import { Post } from "../../../types/community";
import { Avatar, AvatarFallback } from "../../../components/ui/avatar";
import { Badge } from "../../../components/ui/badge";
import { cn } from "../../../components/ui/utils";
import {
  MessageSquare,
  ThumbsUp,
  TrendingUp,
  Award,
  HelpCircle,
  Hash,
  Pin,
} from "lucide-react";

interface PostCardProps {
  post: Post;
  onViewPost: (postId: string) => void;
  onLike: (postId: string) => void;
  currentUserId?: string;
}

export function PostCard({
  post,
  onViewPost,
  onLike,
}: PostCardProps) {
  const getInitials = (name: string) => {
    const words = name.trim().split(" ");
    if (words.length >= 2) {
      return (words[0][0] + words[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const getCategoryIcon = (category: string) => {
    switch (category) {
      case "tips":
        return <TrendingUp className="w-4 h-4" />;
      case "achievement":
        return <Award className="w-4 h-4" />;
      case "question":
        return <HelpCircle className="w-4 h-4" />;
      default:
        return <Hash className="w-4 h-4" />;
    }
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case "tips":
        return "bg-blue-500/10 text-blue-500 border-blue-500/20";
      case "achievement":
        return "bg-yellow-500/10 text-yellow-600 border-yellow-500/20";
      case "question":
        return "bg-purple-500/10 text-purple-500 border-purple-500/20";
      default:
        return "bg-muted text-muted-foreground";
    }
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffInMinutes = Math.floor(
      (now.getTime() - date.getTime()) / (1000 * 60)
    );

    if (diffInMinutes < 1) return "방금";
    if (diffInMinutes < 60) return `${diffInMinutes}분 전`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}시간 전`;
    if (diffInMinutes < 10080)
      return `${Math.floor(diffInMinutes / 1440)}일 전`;
    return date.toLocaleDateString("ko-KR", {
      month: "short",
      day: "numeric",
    });
  };

  // Discourse 스타일: 읽지 않은 게시글 표시 (예시)
  const isUnread = false; // TODO: 실제 읽음 상태 연동

  return (
    <div
      className={cn(
        "group relative flex gap-4 p-4 border-b hover:bg-muted/50 transition-colors cursor-pointer",
        isUnread && "bg-primary/5 border-l-2 border-l-primary"
      )}
      onClick={() => onViewPost(post.id)}
    >
      {/* 좌측: 아바타 + 카테고리 아이콘 (Discourse 스타일) */}
      <div className="flex flex-col items-center gap-2 flex-shrink-0">
        <Avatar className="w-10 h-10">
          <AvatarFallback className="bg-secondary text-secondary-foreground">
            {getInitials(post.authorName)}
          </AvatarFallback>
        </Avatar>
        <div
          className={cn(
            "w-8 h-8 rounded-full flex items-center justify-center border",
            getCategoryColor(post.category)
          )}
        >
          {getCategoryIcon(post.category)}
        </div>
      </div>

      {/* 중앙: 제목 + 미리보기 + 메타 정보 (Discourse 스타일) */}
      <div className="flex-1 min-w-0">
        <div className="flex items-start gap-2 mb-1">
          {/* 카테고리 배지 */}
          <Badge
            variant="outline"
            className={cn("text-xs", getCategoryColor(post.category))}
          >
            {post.category === "tips" && "팁"}
            {post.category === "achievement" && "성취"}
            {post.category === "question" && "질문"}
            {post.category === "general" && "일반"}
          </Badge>

          {/* 핀 고정 아이콘 (예시) */}
          {false && (
            <Pin className="w-3 h-3 text-muted-foreground flex-shrink-0" />
          )}
        </div>

        {/* 제목 */}
        <h3
          className={cn(
            "font-semibold text-base mb-1 line-clamp-2 group-hover:text-primary transition-colors",
            isUnread && "font-bold"
          )}
        >
          {post.title}
        </h3>

        {/* 미리보기 (Discourse 스타일) */}
        <p className="text-sm text-muted-foreground line-clamp-2 mb-2">
          {post.content}
        </p>

        {/* 메타 정보 */}
        <div className="flex items-center gap-3 text-xs text-muted-foreground">
          <span className="truncate">{post.authorName}</span>
          <span>•</span>
          <span className="whitespace-nowrap">
            {formatTimeAgo(post.createdAt)}
          </span>
        </div>
      </div>

      {/* 우측: 통계 (Discourse 스타일) */}
      <div className="flex flex-col items-end gap-2 flex-shrink-0 min-w-[80px]">
        {/* 댓글 수 */}
        <div className="flex items-center gap-1 text-sm text-muted-foreground">
          <MessageSquare className="w-4 h-4" />
          <span>{post.comments}</span>
        </div>

        {/* 좋아요 */}
        <button
          onClick={(e) => {
            e.stopPropagation();
            onLike(post.id);
          }}
          className={cn(
            "flex items-center gap-1 text-sm transition-colors",
            post.isLiked
              ? "text-primary"
              : "text-muted-foreground hover:text-primary"
          )}
        >
          <ThumbsUp className={cn("w-4 h-4", post.isLiked && "fill-current")} />
          <span>{post.likes}</span>
        </button>

        {/* 읽지 않은 게시글 표시 (Discourse 스타일) */}
        {isUnread && <div className="w-2 h-2 rounded-full bg-primary mt-1" />}
      </div>
    </div>
  );
}
