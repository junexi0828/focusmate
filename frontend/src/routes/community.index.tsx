import React, { useState } from "react";
import { createFileRoute, redirect, useNavigate } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { CommunityPage } from "../pages/Community";
import { authService } from "../features/auth/services/authService";
import { communityService } from "../features/community/services/communityService";
import { PageTransition } from "../components/PageTransition";
import { CreatePostDialog } from "../features/community/components/CreatePostDialog";
import { toast } from "sonner";
import { z } from "zod";

const communitySearchSchema = z.object({
  category: z.string().optional(),
  search: z.string().optional(),
  author_username: z.string().optional(),
  date_from: z.string().optional(),
  date_to: z.string().optional(),
  page: z.number().int().min(1).optional().default(1),
});

export const Route = createFileRoute("/community/")({
  validateSearch: communitySearchSchema,
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  loaderDeps: ({ search }) => ({
    category: search.category,
    search: search.search,
    author_username: search.author_username,
    date_from: search.date_from,
    date_to: search.date_to,
    page: search.page,
  }),
  loader: async ({ deps }) => {
    const limit = 20;
    const offset = (deps.page - 1) * limit;
    const response = await communityService.getPosts({
      limit,
      offset,
      category: deps.category,
      search: deps.search,
      author_username: deps.author_username,
      date_from: deps.date_from,
      date_to: deps.date_to,
    });
    if (response.status === "error") {
      throw new Error(response.error?.message || "Failed to load posts");
    }
    return response.data!;
  },
  component: CommunityComponent,
});

function CommunityComponent() {
  const navigate = useNavigate();
  const { category, search: searchQuery, author_username, date_from, date_to, page } = Route.useSearch();
  const initialData = Route.useLoaderData();
  const queryClient = useQueryClient();
  const user = authService.getCurrentUser();

  const { data, isLoading, error } = useQuery({
    queryKey: ["community", "posts", category, searchQuery, author_username, date_from, date_to, page],
    queryFn: async () => {
      const limit = 20;
      const offset = (page - 1) * limit;
      const response = await communityService.getPosts({
        limit,
        offset,
        category,
        search: searchQuery,
        author_username,
        date_from,
        date_to,
      });
      if (response.status === "error") {
        throw new Error(response.error?.message || "Failed to load posts");
      }
      return response.data!;
    },
    initialData,
    staleTime: 1000 * 30, // 30 seconds
  });

  const likeMutation = useMutation({
    mutationFn: (postId: string) => {
      if (!user?.id) throw new Error("User not authenticated");
      return communityService.likePost(postId, user.id);
    },
    onSuccess: (response, postId) => {
      if (response.status === "success") {
        queryClient.invalidateQueries({ queryKey: ["community", "posts"] });
      }
    },
  });

  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);

  const createPostMutation = useMutation({
    mutationFn: async (data: {
      title: string;
      content: string;
      category: "general" | "tips" | "question" | "achievement";
    }) => {
      if (!user?.id) throw new Error("User not authenticated");
      return communityService.createPost(user.id, data);
    },
    onSuccess: (response) => {
      if (response.status === "success") {
        queryClient.invalidateQueries({ queryKey: ["community", "posts"] });
        toast.success("게시글이 작성되었습니다!");
        setIsCreateDialogOpen(false);
      } else {
        toast.error(response.error?.message || "게시글 작성에 실패했습니다");
      }
    },
    onError: (error) => {
      toast.error(
        error instanceof Error ? error.message : "게시글 작성에 실패했습니다"
      );
    },
  });

  const handleCreatePost = () => {
    setIsCreateDialogOpen(true);
  };

  const handleSubmitPost = async (data: {
    title: string;
    content: string;
    category: "general" | "tips" | "question" | "achievement";
  }) => {
    await createPostMutation.mutateAsync(data);
  };

  const handleViewPost = (postId: string) => {

    navigate({ to: "/community/$postId", params: { postId } });
  };

  const handleLike = (postId: string) => {
    likeMutation.mutate(postId);
  };

  const handleAuthorUsernameChange = (value: string) => {
    navigate({
      search: (prev) => ({
        ...prev,
        author_username: value || undefined,
        page: 1, // Reset to first page when filter changes
      }),
    });
  };

  const handleDateFromChange = (value: string) => {
    navigate({
      search: (prev) => ({
        ...prev,
        date_from: value || undefined,
        page: 1,
      }),
    });
  };

  const handleDateToChange = (value: string) => {
    navigate({
      search: (prev) => ({
        ...prev,
        date_to: value || undefined,
        page: 1,
      }),
    });
  };

  const handleClearAdvancedFilters = () => {
    navigate({
      search: (prev) => ({
        ...prev,
        author_username: undefined,
        date_from: undefined,
        date_to: undefined,
        page: 1,
      }),
    });
  };

  if (isLoading && !data) {
    return (
      <div className="min-h-screen bg-muted/30 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-muted/30 flex items-center justify-center">
        <div className="text-center">
          <p className="text-destructive">게시글을 불러오는데 실패했습니다</p>
          <p className="text-sm text-muted-foreground mt-2">
            {error instanceof Error ? error.message : "알 수 없는 오류"}
          </p>
        </div>
      </div>
    );
  }

  // Transform API posts to UI format
  const uiPosts = (data?.posts || []).map((post) => ({
    id: post.id,
    authorId: post.user_id,
    authorName: post.author_username || "익명",
    title: post.title,
    content: post.content,
    category: post.category as "general" | "tips" | "question" | "achievement",
    createdAt: new Date(post.created_at),
    likes: post.likes,
    comments: post.comment_count,
    isLiked: post.is_liked || false,
    isRead: post.is_read || false, // Whether current user has read this post
  }));

  return (
    <PageTransition>
      <CommunityPage
        posts={uiPosts}
        onCreatePost={handleCreatePost}
        onViewPost={handleViewPost}
        onLike={handleLike}
        authorUsername={author_username || ""}
        dateFrom={date_from || ""}
        dateTo={date_to || ""}
        onAuthorUsernameChange={handleAuthorUsernameChange}
        onDateFromChange={handleDateFromChange}
        onDateToChange={handleDateToChange}
        onClearAdvancedFilters={handleClearAdvancedFilters}
      />
      <CreatePostDialog
        open={isCreateDialogOpen}
        onOpenChange={setIsCreateDialogOpen}
        onSubmit={handleSubmitPost}
      />
    </PageTransition>
  );
}
