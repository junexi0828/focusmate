import { createFileRoute, useNavigate, redirect } from "@tanstack/react-router";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { communityService } from "../features/community/services/communityService";
import { authService } from "../features/auth/services/authService";
import { PageTransition } from "../components/PageTransition";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardHeader } from "../components/ui/card";
import { Badge } from "../components/ui/badge";
import { Textarea } from "../components/ui/textarea";
import { Avatar, AvatarFallback } from "../components/ui/avatar";
import {
  ArrowLeft,
  Heart,
  MessageSquare,
  Send,
  Trash2,
  Edit,
  Reply,
  MoreVertical,
} from "lucide-react";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "../components/ui/dialog";
import { Input } from "../components/ui/input";
import { toast } from "sonner";
import { formatDistanceToNow } from "date-fns";
import { ko } from "date-fns/locale";

export const Route = createFileRoute("/community/$postId")({
  beforeLoad: () => {
    if (!authService.isAuthenticated()) {
      toast.error("로그인이 필요한 서비스입니다");
      throw redirect({ to: "/login" });
    }
  },
  loader: async ({ params }) => {
    try {
      const response = await communityService.getPost(params.postId);
      const commentsResponse = await communityService.getComments(params.postId);

      if (response.status === "success" && commentsResponse.status === "success") {
        return {
          post: response.data,
          comments: commentsResponse.data,
        };
      }
      // Return null instead of throwing error
      return {
        post: null,
        comments: [],
      };
    } catch (error) {
      console.error("Failed to load post:", error);
      return {
        post: null,
        comments: [],
      };
    }
  },
  component: PostDetailComponent,
  pendingComponent: () => (
    <PageTransition>
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-muted-foreground">로딩 중...</p>
        </div>
      </div>
    </PageTransition>
  ),
  errorComponent: () => (
    <PageTransition>
      <div className="text-center py-12">
        <p className="text-destructive text-lg mb-4">게시글을 불러오는데 실패했습니다</p>
        <Button onClick={() => window.history.back()}>뒤로가기</Button>
      </div>
    </PageTransition>
  ),
});

function PostDetailComponent() {
  const { postId } = Route.useParams();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const initialData = Route.useLoaderData();
  const user = authService.getCurrentUser();

  const [commentContent, setCommentContent] = useState("");
  const [editingPost, setEditingPost] = useState(false);
  const [editPostTitle, setEditPostTitle] = useState("");
  const [editPostContent, setEditPostContent] = useState("");
  const [editingCommentId, setEditingCommentId] = useState<string | null>(null);
  const [editCommentContent, setEditCommentContent] = useState("");
  const [replyingToCommentId, setReplyingToCommentId] = useState<string | null>(null);
  const [replyContent, setReplyContent] = useState("");

  const { data: post } = useQuery({
    queryKey: ["community", "post", postId],
    queryFn: async () => {
      const response = await communityService.getPost(postId);
      return response.status === "success" ? response.data : null;
    },
    initialData: initialData.post,
    staleTime: 1000 * 60, // 1 minute
    enabled: !!postId,
  });

  const { data: comments = [] } = useQuery({
    queryKey: ["community", "comments", postId],
    queryFn: async () => {
      const response = await communityService.getComments(postId);
      return response.status === "success" ? response.data : [];
    },
    initialData: initialData.comments,
    staleTime: 1000 * 60, // 1 minute
    enabled: !!postId,
  });

  const likeMutation = useMutation({
    mutationFn: () => {
      if (!user?.id) throw new Error("User not authenticated");
      return communityService.likePost(postId, user.id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["community", "post", postId] });
      toast.success("좋아요!");
    },
    onError: () => {
      toast.error("좋아요 처리에 실패했습니다");
    },
  });

  const createCommentMutation = useMutation({
    mutationFn: (data: { content: string; parent_comment_id?: string }) => {
      if (!user?.id) throw new Error("User not authenticated");
      return communityService.createComment(postId, user.id, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["community", "comments", postId],
      });
      queryClient.invalidateQueries({ queryKey: ["community", "post", postId] });
      setCommentContent("");
      toast.success("댓글이 작성되었습니다");
    },
    onError: () => {
      toast.error("댓글 작성에 실패했습니다");
    },
  });

  const deleteCommentMutation = useMutation({
    mutationFn: (commentId: string) => communityService.deleteComment(commentId),
    onSuccess: () => {
      queryClient.invalidateQueries({
        queryKey: ["community", "comments", postId],
      });
      queryClient.invalidateQueries({ queryKey: ["community", "post", postId] });
      toast.success("댓글이 삭제되었습니다");
    },
    onError: () => {
      toast.error("댓글 삭제에 실패했습니다");
    },
  });

  const deletePostMutation = useMutation({
    mutationFn: () => {
      if (!user?.id) throw new Error("User not authenticated");
      return communityService.deletePost(postId, user.id);
    },
    onSuccess: () => {
      toast.success("게시글이 삭제되었습니다");
      navigate({ to: "/community" });
    },
    onError: () => {
      toast.error("게시글 삭제에 실패했습니다");
    },
  });

  const updatePostMutation = useMutation({
    mutationFn: (data: { title?: string; content?: string; category?: string }) => {
      if (!user?.id) throw new Error("User not authenticated");
      return communityService.updatePost(postId, user.id, data);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["community", "post", postId] });
      setEditingPost(false);
      toast.success("게시글이 수정되었습니다");
    },
    onError: () => {
      toast.error("게시글 수정에 실패했습니다");
    },
  });

  const updateCommentMutation = useMutation({
    mutationFn: ({ commentId, content }: { commentId: string; content: string }) => {
      if (!user?.id) throw new Error("User not authenticated");
      return communityService.updateComment(commentId, user.id, content);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["community", "comments", postId] });
      setEditingCommentId(null);
      setEditCommentContent("");
      toast.success("댓글이 수정되었습니다");
    },
    onError: () => {
      toast.error("댓글 수정에 실패했습니다");
    },
  });

  const likeCommentMutation = useMutation({
    mutationFn: (commentId: string) => {
      if (!user?.id) throw new Error("User not authenticated");
      return communityService.likeComment(commentId, user.id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["community", "comments", postId] });
      queryClient.invalidateQueries({ queryKey: ["community", "post", postId] });
    },
    onError: () => {
      toast.error("좋아요 처리에 실패했습니다");
    },
  });

  const handleCommentSubmit = () => {
    if (replyingToCommentId) {
      if (!replyContent.trim()) {
        toast.error("답글 내용을 입력해주세요");
        return;
      }
      createCommentMutation.mutate({
        content: replyContent,
        parent_comment_id: replyingToCommentId,
      });
      setReplyingToCommentId(null);
      setReplyContent("");
    } else {
      if (!commentContent.trim()) {
        toast.error("댓글 내용을 입력해주세요");
        return;
      }
      createCommentMutation.mutate({
        content: commentContent,
      });
      setCommentContent("");
    }
  };

  const handleEditPost = () => {
    if (post) {
      setEditPostTitle(post.title);
      setEditPostContent(post.content);
      setEditingPost(true);
    }
  };

  const handleSavePost = () => {
    if (!editPostTitle.trim() || !editPostContent.trim()) {
      toast.error("제목과 내용을 입력해주세요");
      return;
    }
    updatePostMutation.mutate({
      title: editPostTitle,
      content: editPostContent,
    });
  };

  const handleEditComment = (comment: any) => {
    setEditingCommentId(comment.id);
    setEditCommentContent(comment.content);
  };

  const handleSaveComment = () => {
    if (!editCommentContent.trim()) {
      toast.error("댓글 내용을 입력해주세요");
      return;
    }
    if (editingCommentId) {
      updateCommentMutation.mutate({
        commentId: editingCommentId,
        content: editCommentContent,
      });
    }
  };

  const handleReply = (commentId: string) => {
    setReplyingToCommentId(commentId);
    setCommentContent("");
  };

  // Helper function to render nested comments
  const renderComments = (commentList: any[], parentId: string | null = null) => {
    return commentList
      .filter((comment) => comment.parent_comment_id === parentId)
      .map((comment) => {
        const replies = renderComments(commentList, comment.id);
        return { ...comment, replies };
      });
  };

  const nestedComments = renderComments(comments);

  if (!post) {
    return (
      <PageTransition>
        <div className="max-w-4xl mx-auto py-12">
          <Card>
            <CardContent className="text-center py-12">
              <MessageSquare className="w-16 h-16 mx-auto mb-4 text-muted-foreground opacity-50" />
              <h2 className="text-xl font-semibold mb-2">게시글을 찾을 수 없습니다</h2>
              <p className="text-muted-foreground mb-6">
                삭제되었거나 존재하지 않는 게시글입니다.
              </p>
              <Button
                onClick={() => navigate({ to: "/community" })}
                className="gap-2"
              >
                <ArrowLeft className="w-4 h-4" />
                커뮤니티로 돌아가기
              </Button>
            </CardContent>
          </Card>
        </div>
      </PageTransition>
    );
  }

  const categoryColors = {
    general: "bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-100",
    tips: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-100",
    question:
      "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100",
    achievement:
      "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100",
  };

  const categoryLabels = {
    general: "일반",
    tips: "팁",
    question: "질문",
    achievement: "성취",
  };

  return (
    <PageTransition>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <Button
            variant="ghost"
            onClick={() => navigate({ to: "/community" })}
            className="gap-2"
          >
            <ArrowLeft className="w-4 h-4" />
            목록으로
          </Button>
          {user?.id === post.user_id && (
            <div className="flex gap-2">
              <Button
                variant="outline"
                size="sm"
                onClick={handleEditPost}
              >
                <Edit className="w-4 h-4 mr-1" />
                수정
              </Button>
              <Button
                variant="destructive"
                size="sm"
                onClick={() => {
                  if (confirm("정말 삭제하시겠습니까?")) {
                    deletePostMutation.mutate();
                  }
                }}
                disabled={deletePostMutation.isPending}
              >
                <Trash2 className="w-4 h-4 mr-1" />
                삭제
              </Button>
            </div>
          )}
        </div>

        {/* Post Content */}
        <Card>
          <CardHeader>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-3">
                  <Badge className={categoryColors[post.category as keyof typeof categoryColors]}>
                    {categoryLabels[post.category as keyof typeof categoryLabels]}
                  </Badge>
                  {post.is_pinned && (
                    <Badge variant="secondary">📌 고정</Badge>
                  )}
                </div>
                <h1 className="text-3xl font-bold mb-4">{post.title}</h1>
                <div className="flex items-center gap-3 text-sm text-muted-foreground">
                  <div className="flex items-center gap-2">
                    <Avatar className="w-6 h-6">
                      <AvatarFallback>
                        {post.author_username?.[0]?.toUpperCase() || "?"}
                      </AvatarFallback>
                    </Avatar>
                    <span>{post.author_username || "익명"}</span>
                  </div>
                  <span>•</span>
                  <span>
                    {formatDistanceToNow(new Date(post.created_at), {
                      addSuffix: true,
                      locale: ko,
                    })}
                  </span>
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="prose dark:prose-invert max-w-none mb-6">
              <p className="whitespace-pre-wrap">{post.content}</p>
            </div>
            <div className="flex items-center gap-4 pt-4 border-t">
              <Button
                variant="ghost"
                size="sm"
                onClick={() => likeMutation.mutate()}
                disabled={likeMutation.isPending || !user}
                className="gap-2"
              >
                <Heart className={`w-4 h-4 ${post.is_liked ? "fill-red-500 text-red-500" : ""}`} />
                {post.likes}
              </Button>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <MessageSquare className="w-4 h-4" />
                {post.comment_count}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Comments Section */}
        <Card>
          <CardHeader>
            <h2 className="text-xl font-semibold">
              댓글 {comments.length}개
            </h2>
          </CardHeader>
          <CardContent className="space-y-4">
            {/* Comment Input */}
            {user && !replyingToCommentId && (
              <div className="flex gap-2">
                <Textarea
                  placeholder="댓글을 작성하세요..."
                  value={commentContent}
                  onChange={(e) => setCommentContent(e.target.value)}
                  className="min-h-[80px]"
                />
                <Button
                  onClick={handleCommentSubmit}
                  disabled={createCommentMutation.isPending || !commentContent.trim()}
                  className="shrink-0"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </div>
            )}

            {/* Reply Input */}
            {user && replyingToCommentId && (
              <div className="flex gap-2 p-3 bg-muted rounded-lg">
                <Textarea
                  placeholder="답글을 작성하세요..."
                  value={replyContent}
                  onChange={(e) => setReplyContent(e.target.value)}
                  className="min-h-[60px]"
                />
                <div className="flex flex-col gap-2">
                  <Button
                    onClick={handleCommentSubmit}
                    disabled={createCommentMutation.isPending || !replyContent.trim()}
                    className="shrink-0"
                  >
                    <Send className="w-4 h-4" />
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => {
                      setReplyingToCommentId(null);
                      setReplyContent("");
                    }}
                  >
                    취소
                  </Button>
                </div>
              </div>
            )}

            {/* Comments List */}
            <div className="space-y-4">
              {nestedComments.length === 0 ? (
                <p className="text-center text-muted-foreground py-8">
                  아직 댓글이 없습니다
                </p>
              ) : (
                nestedComments.map((comment) => (
                  <CommentItem
                    key={comment.id}
                    comment={comment}
                    user={user}
                    onEdit={handleEditComment}
                    onDelete={(id) => {
                      if (confirm("정말 삭제하시겠습니까?")) {
                        deleteCommentMutation.mutate(id);
                      }
                    }}
                    onLike={(id) => likeCommentMutation.mutate(id)}
                    onReply={handleReply}
                    editingCommentId={editingCommentId}
                    editCommentContent={editCommentContent}
                    onEditContentChange={setEditCommentContent}
                    onSaveEdit={handleSaveComment}
                    onCancelEdit={() => {
                      setEditingCommentId(null);
                      setEditCommentContent("");
                    }}
                    replyingToCommentId={replyingToCommentId}
                  />
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Edit Post Dialog */}
      <Dialog open={editingPost} onOpenChange={setEditingPost}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>게시글 수정</DialogTitle>
            <DialogDescription>
              게시글 제목과 내용을 수정하세요
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">제목</label>
              <Input
                value={editPostTitle}
                onChange={(e) => setEditPostTitle(e.target.value)}
                placeholder="제목을 입력하세요"
              />
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">내용</label>
              <Textarea
                value={editPostContent}
                onChange={(e) => setEditPostContent(e.target.value)}
                placeholder="내용을 입력하세요"
                className="min-h-[200px]"
              />
            </div>
            <div className="flex justify-end gap-2">
              <Button
                variant="outline"
                onClick={() => setEditingPost(false)}
              >
                취소
              </Button>
              <Button
                onClick={handleSavePost}
                disabled={updatePostMutation.isPending}
              >
                저장
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </PageTransition>
  );
}

// Comment Item Component with nested replies
interface CommentItemProps {
  comment: any;
  user: any;
  onEdit: (comment: any) => void;
  onDelete: (id: string) => void;
  onLike: (id: string) => void;
  onReply: (id: string) => void;
  editingCommentId: string | null;
  editCommentContent: string;
  onEditContentChange: (content: string) => void;
  onSaveEdit: () => void;
  onCancelEdit: () => void;
  replyingToCommentId: string | null;
}

function CommentItem({
  comment,
  user,
  onEdit,
  onDelete,
  onLike,
  onReply,
  editingCommentId,
  editCommentContent,
  onEditContentChange,
  onSaveEdit,
  onCancelEdit,
  replyingToCommentId,
}: CommentItemProps) {
  const isEditing = editingCommentId === comment.id;

  return (
    <div className="space-y-2">
      <div
        className={`flex gap-3 p-4 rounded-lg bg-muted/50 ${
          comment.parent_comment_id ? "ml-8 border-l-2 border-primary/20" : ""
        }`}
      >
        <Avatar className="w-8 h-8">
          <AvatarFallback>
            {comment.author_username?.[0]?.toUpperCase() || "?"}
          </AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <div className="flex items-center justify-between mb-1">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">
                {comment.author_username || "익명"}
              </span>
              <span className="text-xs text-muted-foreground">
                {formatDistanceToNow(new Date(comment.created_at), {
                  addSuffix: true,
                  locale: ko,
                })}
              </span>
            </div>
            {user?.id === comment.user_id && (
              <div className="flex gap-1">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onEdit(comment)}
                  className="h-6 px-2"
                >
                  <Edit className="w-3 h-3" />
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => onDelete(comment.id)}
                  className="h-6 px-2"
                >
                  <Trash2 className="w-3 h-3" />
                </Button>
              </div>
            )}
          </div>
          {isEditing ? (
            <div className="space-y-2">
              <Textarea
                value={editCommentContent}
                onChange={(e) => onEditContentChange(e.target.value)}
                className="min-h-[80px]"
              />
              <div className="flex gap-2">
                <Button
                  size="sm"
                  onClick={onSaveEdit}
                >
                  저장
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  onClick={onCancelEdit}
                >
                  취소
                </Button>
              </div>
            </div>
          ) : (
            <>
              <p className="text-sm whitespace-pre-wrap">{comment.content}</p>
              <div className="flex items-center gap-3 mt-2">
                <Button
                  variant="ghost"
                  size="sm"
                  className="h-6 px-2"
                  onClick={() => onLike(comment.id)}
                  disabled={!user}
                >
                  <Heart className={`w-3 h-3 mr-1 ${comment.is_liked ? "fill-red-500 text-red-500" : ""}`} />
                  {comment.likes}
                </Button>
                {user && (
                  <Button
                    variant="ghost"
                    size="sm"
                    className="h-6 px-2"
                    onClick={() => onReply(comment.id)}
                  >
                    <Reply className="w-3 h-3 mr-1" />
                    답글
                  </Button>
                )}
              </div>
            </>
          )}
        </div>
      </div>
      {/* Nested Replies */}
      {comment.replies && comment.replies.length > 0 && (
        <div className="ml-8 space-y-2">
          {comment.replies.map((reply: any) => (
            <CommentItem
              key={reply.id}
              comment={reply}
              user={user}
              onEdit={onEdit}
              onDelete={onDelete}
              onLike={onLike}
              onReply={onReply}
              editingCommentId={editingCommentId}
              editCommentContent={editCommentContent}
              onEditContentChange={onEditContentChange}
              onSaveEdit={onSaveEdit}
              onCancelEdit={onCancelEdit}
              replyingToCommentId={replyingToCommentId}
            />
          ))}
        </div>
      )}
    </div>
  );
}
