import { Post } from "../../../types/community";
import { PostCard } from "./PostCard";
import { Card, CardContent } from "../../../components/ui/card";
import { MessageSquare, SearchX } from "lucide-react";
import { Button } from "../../../components/ui/button-enhanced";

interface PostListProps {
  posts: Post[];
  onViewPost: (postId: string) => void;
  onLike: (postId: string) => void;
  currentUserId?: string;
  hasSearchOrFilters?: boolean;
  onClearFilters?: () => void;
}

export function PostList({
  posts,
  onViewPost,
  onLike,
  currentUserId,
  hasSearchOrFilters = false,
  onClearFilters,
}: PostListProps) {
  if (posts.length === 0) {
    if (hasSearchOrFilters) {
      // Empty state for search/filter results
      return (
        <Card>
          <CardContent className="py-16 text-center">
            <SearchX className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
            <p className="text-lg font-medium text-muted-foreground mb-2">
              검색 결과가 없습니다
            </p>
            <p className="text-sm text-muted-foreground mb-4">
              다른 검색어를 시도하거나 필터를 변경해보세요
            </p>
            {onClearFilters && (
              <Button variant="outline" onClick={onClearFilters}>
                검색 초기화
              </Button>
            )}
          </CardContent>
        </Card>
      );
    }

    // Default empty state (no posts at all)
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

