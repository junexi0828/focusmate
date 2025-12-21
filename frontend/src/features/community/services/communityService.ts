import { BaseApiClient, ApiResponse } from '../../../lib/api/base';

export interface Post {
  id: string;
  user_id: string;
  title: string;
  content: string;
  category: string;
  likes: number;
  comment_count: number;
  is_pinned: boolean;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  author_username: string | null;
  is_liked?: boolean; // Whether current user liked this post
  is_read?: boolean; // Whether current user has read this post
}

export interface Comment {
  id: string;
  post_id: string;
  user_id: string;
  content: string;
  parent_comment_id: string | null;
  likes: number;
  is_deleted: boolean;
  created_at: string;
  updated_at: string;
  author_username: string | null;
  is_liked?: boolean; // Whether current user liked this comment
  replies: Comment[];
}

export interface PostCreateRequest {
  title: string;
  content: string;
  category: 'tips' | 'achievement' | 'question' | 'general';
}

export interface PostUpdateRequest {
  title?: string;
  content?: string;
  category?: 'tips' | 'achievement' | 'question' | 'general';
}

export interface CommentCreateRequest {
  content: string;
  parent_comment_id?: string;
}

export interface PostListResponse {
  posts: Post[];
  total: number;
  limit: number;
  offset: number;
}

class CommunityService extends BaseApiClient {
  async getPosts(params?: {
    limit?: number;
    offset?: number;
    category?: string;
    search?: string;
    user_id?: string;
    author_username?: string;
    date_from?: string;
    date_to?: string;
    sort_by?: string;
  }): Promise<ApiResponse<PostListResponse>> {
    const queryParams = new URLSearchParams();
    if (params?.limit) queryParams.append('limit', String(params.limit));
    if (params?.offset) queryParams.append('offset', String(params.offset));
    if (params?.category) queryParams.append('category', params.category);
    if (params?.search) queryParams.append('search', params.search);
    if (params?.user_id) queryParams.append('user_id', params.user_id);
    if (params?.author_username) queryParams.append('author_username', params.author_username);
    if (params?.date_from) queryParams.append('date_from', params.date_from);
    if (params?.date_to) queryParams.append('date_to', params.date_to);
    if (params?.sort_by) queryParams.append('sort_by', params.sort_by);

    const query = queryParams.toString();
    return this.request<PostListResponse>(`/community/posts${query ? `?${query}` : ''}`);
  }

  async getPost(postId: string): Promise<ApiResponse<Post>> {
    return this.request<Post>(`/community/posts/${postId}`);
  }

  async createPost(
    userId: string,
    data: PostCreateRequest
  ): Promise<ApiResponse<Post>> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);
    return this.request<Post>(`/community/posts?${queryParams.toString()}`, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async updatePost(
    postId: string,
    userId: string,
    data: PostUpdateRequest
  ): Promise<ApiResponse<Post>> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);
    return this.request<Post>(`/community/posts/${postId}?${queryParams.toString()}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async deletePost(postId: string, userId: string): Promise<ApiResponse<void>> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);
    return this.request<void>(`/community/posts/${postId}?${queryParams.toString()}`, {
      method: 'DELETE',
    });
  }

  async likePost(postId: string, userId: string): Promise<ApiResponse<{ success: boolean; liked: boolean; new_count: number }>> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);
    return this.request<{ success: boolean; liked: boolean; new_count: number }>(
      `/community/posts/${postId}/like?${queryParams.toString()}`,
      {
        method: 'POST',
      }
    );
  }

  async getComments(postId: string): Promise<ApiResponse<Comment[]>> {
    return this.request<Comment[]>(`/community/posts/${postId}/comments`);
  }

  async createComment(
    postId: string,
    userId: string,
    data: CommentCreateRequest
  ): Promise<ApiResponse<Comment>> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);
    return this.request<Comment>(
      `/community/posts/${postId}/comments?${queryParams.toString()}`,
      {
        method: 'POST',
        body: JSON.stringify(data),
      }
    );
  }

  async updateComment(
    commentId: string,
    userId: string,
    content: string
  ): Promise<ApiResponse<Comment>> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);
    return this.request<Comment>(`/community/comments/${commentId}?${queryParams.toString()}`, {
      method: 'PUT',
      body: JSON.stringify({ content }),
    });
  }

  async deleteComment(commentId: string, userId: string): Promise<ApiResponse<void>> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);
    return this.request<void>(`/community/comments/${commentId}?${queryParams.toString()}`, {
      method: 'DELETE',
    });
  }

  async likeComment(commentId: string, userId: string): Promise<ApiResponse<{ success: boolean; liked: boolean; new_count: number }>> {
    const queryParams = new URLSearchParams();
    queryParams.append('user_id', userId);
    return this.request<{ success: boolean; liked: boolean; new_count: number }>(
      `/community/comments/${commentId}/like?${queryParams.toString()}`,
      {
        method: 'POST',
      }
    );
  }
}

export const communityService = new CommunityService();

