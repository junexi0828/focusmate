import React from "react";
import { Post } from "../../../types/community";
import { PostCard } from "./PostCard";
import { ScrollArea } from "../../../components/ui/scroll-area";
import { Card, CardContent } from "../../../components/ui/card";
import { MessageSquare } from "lucide-react";

interface PostListProps {
  posts: Post[];
  onViewPost: (postId: string) => void;
  onLike: (postId: string) => void;
  currentUserId?: string;
}

export function PostList({
  posts,
  onViewPost,
  onLike,
  currentUserId,
}: PostListProps) {
  if (posts.length === 0) {
    return (
      <Card>
        <CardContent className="py-16 text-center">
          <MessageSquare className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
          <p className="text-lg font-medium text-muted-foreground mb-2">
            게시글이 없습니다
          </p>
          <p className="text-sm text-muted-foreground">
            첫 번째 게시글을 작성해보세요!
          </p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="bg-background border rounded-lg overflow-hidden">
      {/* 게시글 목록 (Discourse 스타일) */}
      <div className="divide-y">
        {posts.map((post) => (
          <PostCard
            key={post.id}
            post={post}
            onViewPost={onViewPost}
            onLike={onLike}
            currentUserId={currentUserId}
          />
        ))}
      </div>
    </div>
  );
}

