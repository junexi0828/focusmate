/**
 * Authentication service
 */

import api from "../../../api/client";
import type { AxiosResponse } from "axios";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username: string;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetVerify {
  token: string;
}

export interface PasswordResetComplete {
  token: string;
  new_password: string;
}

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  is_active: boolean;
  is_verified: boolean;
  is_admin: boolean;
  bio?: string | null;
  school?: string | null;
  profile_image?: string | null;
  total_focus_time: number;
  total_sessions: number;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface ProfileUpdateRequest {
  username?: string;
  bio?: string;
  school?: string;
  profile_image?: string;
}

export interface ApiResponse<T> {
  status: "success" | "error";
  data?: T;
  error?: {
    message: string;
    code?: string;
  };
}

class AuthService {
  async login(data: LoginRequest): Promise<ApiResponse<TokenResponse>> {
    try {
      const response: AxiosResponse<TokenResponse> = await api.post("/auth/login", data);
      if (response.data) {
        this.setToken(response.data.access_token);
        this.setCurrentUser(response.data.user);
      }
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          message: error?.response?.data?.detail || "로그인에 실패했습니다",
        },
      };
    }
  }

  async register(data: RegisterRequest): Promise<ApiResponse<TokenResponse>> {
    try {
      const response: AxiosResponse<TokenResponse> = await api.post("/auth/register", data);
      if (response.data) {
        this.setToken(response.data.access_token);
        this.setCurrentUser(response.data.user);
      }
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          message: error?.response?.data?.detail || "회원가입에 실패했습니다",
        },
      };
    }
  }

  async requestPasswordReset(
    data: PasswordResetRequest
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await api.post("/auth/password-reset/request", data);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          message: error?.response?.data?.detail || "요청에 실패했습니다",
        },
      };
    }
  }

  async verifyPasswordResetToken(
    data: PasswordResetVerify
  ): Promise<ApiResponse<{ valid: boolean; message: string }>> {
    try {
      const response = await api.post("/auth/password-reset/verify", data);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          message: error?.response?.data?.detail || "토큰 검증에 실패했습니다",
        },
      };
    }
  }

  async completePasswordReset(
    data: PasswordResetComplete
  ): Promise<ApiResponse<{ message: string }>> {
    try {
      const response = await api.post("/auth/password-reset/complete", data);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          message: error?.response?.data?.detail || "비밀번호 재설정에 실패했습니다",
        },
      };
    }
  }

  async getNaverLoginUrl(): Promise<
    ApiResponse<{ auth_url: string; state: string }>
  > {
    try {
      const response = await api.get("/auth/naver/login");
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          message: error?.response?.data?.detail || "네이버 로그인 URL을 가져오는데 실패했습니다",
        },
      };
    }
  }

  async naverOAuthCallback(code: string, state?: string): Promise<ApiResponse<TokenResponse>> {
    try {
      const response: AxiosResponse<TokenResponse> = await api.post("/auth/naver/callback", { code, state });
      if (response.data) {
        this.setToken(response.data.access_token);
        this.setCurrentUser(response.data.user);
      }
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          message: error?.response?.data?.detail || "네이버 로그인에 실패했습니다",
        },
      };
    }
  }

  async getProfile(userId: string): Promise<ApiResponse<UserResponse>> {
    try {
      const response = await api.get(`/auth/profile/${userId}`);
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          message: error?.response?.data?.detail || "프로필을 가져오는데 실패했습니다",
        },
      };
    }
  }

  async updateProfile(
    userId: string,
    data: ProfileUpdateRequest
  ): Promise<ApiResponse<UserResponse>> {
    try {
      const response = await api.put(`/auth/profile/${userId}`, data);
      if (response.data) {
        this.setCurrentUser(response.data);
      }
      return { status: "success", data: response.data };
    } catch (error: any) {
      return {
        status: "error",
        error: {
          message: error?.response?.data?.detail || "프로필 업데이트에 실패했습니다",
        },
      };
    }
  }

  getToken(): string | null {
    return localStorage.getItem("access_token");
  }

  setToken(token: string): void {
    localStorage.setItem("access_token", token);
  }

  removeToken(): void {
    localStorage.removeItem("access_token");
  }

  getCurrentUser(): UserResponse | null {
    const userStr = localStorage.getItem("user");
    if (!userStr) return null;
    try {
      return JSON.parse(userStr);
    } catch {
      return null;
    }
  }

  setCurrentUser(user: UserResponse): void {
    localStorage.setItem("user", JSON.stringify(user));
  }

  removeCurrentUser(): void {
    localStorage.removeItem("user");
  }

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  isTokenExpired(): boolean {
    const token = this.getToken();
    if (!token) return true;

    try {
      // Decode JWT token (base64 decode the payload)
      const payload = JSON.parse(atob(token.split('.')[1]));
      const exp = payload.exp;

      if (!exp) return false; // No expiration claim

      // Check if token is expired (exp is in seconds, Date.now() is in milliseconds)
      return Date.now() >= exp * 1000;
    } catch (error) {
      console.error('Failed to decode token:', error);
      return true; // Treat invalid tokens as expired
    }
  }

  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.is_admin || false;
  }

  logout(): void {
    this.removeToken();
    this.removeCurrentUser();
  }
}

export const authService = new AuthService();
