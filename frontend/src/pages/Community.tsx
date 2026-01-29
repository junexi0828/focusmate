import React, { useState } from "react";
import { Post } from "../types/community";
import { PostListHeader, PostList } from "../features/community/components";

interface CommunityPageProps {
  posts: Post[];
  onCreatePost: () => void;
  onViewPost: (postId: string) => void;
  onLike: (postId: string) => void;
  selectedCategory?: string;
  onCategoryChange?: (category: string) => void;
  sortBy?: string;
  onSortByChange?: (sortBy: string) => void;
  authorUsername: string;
  dateFrom: string;
  dateTo: string;
  onAuthorUsernameChange: (value: string) => void;
  onDateFromChange: (value: string) => void;
  onDateToChange: (value: string) => void;
  onClearAdvancedFilters: () => void;
  searchQuery?: string;
  onSearchChange?: (query: string) => void;
}

export function CommunityPage({
  posts,
  onCreatePost,
  onViewPost,
  onLike,
  selectedCategory = "all",
  onCategoryChange,
  sortBy = "recent",
  onSortByChange,
  authorUsername,
  dateFrom,
  dateTo,
  onAuthorUsernameChange,
  onDateFromChange,
  onDateToChange,
  onClearAdvancedFilters,
  searchQuery: propSearchQuery = "",
  onSearchChange,
}: CommunityPageProps) {
  const [localSearchQuery, setLocalSearchQuery] = useState(propSearchQuery);

  // Sync with prop when it changes
  React.useEffect(() => {
    setLocalSearchQuery(propSearchQuery);
  }, [propSearchQuery]);

  const handleSearchChange = (query: string) => {
    setLocalSearchQuery(query);
    if (onSearchChange) {
      onSearchChange(query);
    }
  };

  // Check if any search or filters are applied
  const hasSearchOrFilters = !!(
    localSearchQuery ||
    selectedCategory !== "all" ||
    authorUsername ||
    dateFrom ||
    dateTo
  );

  return (
    <div className="space-y-6 p-6">
      {/* Header (Dashboard 스타일로 통일) */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">커뮤니티</h1>
          <p className="text-muted-foreground mt-1">
            팁을 공유하고 질문하세요
          </p>
        </div>
      </div>

      {/* 검색 및 필터 헤더 (Discourse 스타일 - 고정) */}
      <PostListHeader
        searchQuery={localSearchQuery}
        onSearchChange={handleSearchChange}
        selectedCategory={selectedCategory}
        onCategoryChange={onCategoryChange || (() => {})}
        sortBy={sortBy}
        onSortByChange={onSortByChange || (() => {})}
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
        <PostList
          posts={posts}
          onViewPost={onViewPost}
          onLike={onLike}
          hasSearchOrFilters={hasSearchOrFilters}
          onClearFilters={onClearAdvancedFilters}
        />
      </div>
    </div>
  );
}
