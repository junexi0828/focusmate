import React, { useState } from "react";
import { Post } from "../types/community";
import { PostListHeader, PostList } from "../features/community/components";
import { EmptyState } from "../components/EmptyState";
import { Button } from "../components/ui/button-enhanced";
import { Users } from "lucide-react";

interface CommunityPageProps {
  posts: Post[];
  onCreatePost: () => void;
  onViewPost: (postId: string) => void;
  onLike: (postId: string) => void;
  selectedCategory?: string;
  onCategoryChange?: (category: string) => void;
  authorUsername: string;
  dateFrom: string;
  dateTo: string;
  onAuthorUsernameChange: (value: string) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onClearAdvancedFilters: () => void;
}

export function CommunityPage({
  posts,
  onCreatePost,
  onViewPost,
  onLike,
  selectedCategory = "all",
  onCategoryChange,
  authorUsername,
  dateFrom,
  dateTo,
  onAuthorUsernameChange,
  onDateFromChange,
  onDateToChange,
  onClearAdvancedFilters,
}: CommunityPageProps) {
  const [searchQuery, setSearchQuery] = useState("");

  return (
    <div className="min-h-full bg-muted/30 flex flex-col">
      {/* Header (Discourse 스타일) */}
      <div className="bg-background border-b">
        <div className="container mx-auto px-4 py-6 max-w-6xl">
          <div className="mb-2">
            <h1 className="text-2xl font-bold">커뮤니티</h1>
            <p className="text-muted-foreground mt-1">
              팁을 공유하고 질문하세요
            </p>
          </div>
        </div>
      </div>

      {/* 검색 및 필터 헤더 (Discourse 스타일 - 고정) */}
      <PostListHeader
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        selectedCategory={selectedCategory}
        onCategoryChange={onCategoryChange || (() => {})}
        onCreatePost={onCreatePost}
        authorUsername={authorUsername || ""}
        dateFrom={dateFrom || ""}
        dateTo={dateTo || ""}
        onAuthorUsernameChange={onAuthorUsernameChange}
        onDateFromChange={onDateFromChange}
        onDateToChange={onDateToChange}
        onClearAdvancedFilters={onClearAdvancedFilters}
      />

      {/* 게시글 목록 (Discourse 스타일) */}
      <div className="flex-1 container mx-auto px-4 py-6 max-w-6xl">
        {posts.length === 0 ? (
          <EmptyState
            icon={Users}
            title="게시글이 없습니다"
            description="첫 게시글을 작성하여 커뮤니티를 시작해보세요!"
            action={
              <Button variant="primary" onClick={onCreatePost}>
                게시글 작성하기
              </Button>
            }
          />
        ) : (
          <PostList posts={posts} onViewPost={onViewPost} onLike={onLike} />
        )}
      </div>
    </div>
  );
}
