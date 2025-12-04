export interface Post {
  id: string;
  authorId: string;
  authorName: string;
  title: string;
  content: string;
  category: "general" | "tips" | "question" | "achievement";
  createdAt: Date;
  likes: number;
  comments: number;
  isLiked?: boolean;
}

export interface Comment {
  id: string;
  postId: string;
  authorId: string;
  authorName: string;
  content: string;
  createdAt: Date;
  likes: number;
}
