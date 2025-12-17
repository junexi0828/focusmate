export interface User {
  id: string;
  email: string;
  name: string;
  avatar?: string;
  bio?: string;
  school?: string;
  profile_image?: string;
  createdAt: Date;
  totalFocusTime: number; // in minutes
  totalSessions: number;
}

export interface AuthState {
  isAuthenticated: boolean;
  user: User | null;
}
