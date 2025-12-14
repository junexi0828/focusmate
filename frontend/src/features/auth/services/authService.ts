import { BaseApiClient, ApiResponse } from "../../../lib/api/base";

export interface LoginRequest {
  email: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  password: string;
  username: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}

export interface UserResponse {
  id: string;
  email: string;
  username: string;
  bio?: string;
  created_at: string;
  total_focus_time: number;
  total_sessions: number;
  is_active?: boolean;
  is_verified?: boolean;
  is_admin?: boolean;
  updated_at?: string;
}

export interface ProfileUpdateRequest {
  username?: string;
  bio?: string;
}

class AuthService extends BaseApiClient {
  async login(data: LoginRequest): Promise<ApiResponse<TokenResponse>> {
    const response = await this.request<TokenResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify(data),
    });

    if (response.status === "success" && response.data) {
      // Store token
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }

    return response;
  }

  async register(data: RegisterRequest): Promise<ApiResponse<TokenResponse>> {
    const response = await this.request<TokenResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify(data),
    });

    if (response.status === "success" && response.data) {
      // Store token
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("user", JSON.stringify(response.data.user));
    }

    return response;
  }

  async getProfile(userId: string): Promise<ApiResponse<UserResponse>> {
    return this.request<UserResponse>(`/auth/profile/${userId}`);
  }

  async updateProfile(
    userId: string,
    data: ProfileUpdateRequest
  ): Promise<ApiResponse<UserResponse>> {
    const response = await this.request<UserResponse>(
      `/auth/profile/${userId}`,
      {
        method: "PUT",
        body: JSON.stringify(data),
      }
    );

    if (response.status === "success" && response.data) {
      // Update stored user
      localStorage.setItem("user", JSON.stringify(response.data));
    }

    return response;
  }

  logout(): void {
    localStorage.removeItem("access_token");
    localStorage.removeItem("user");
  }

  getToken(): string | null {
    return localStorage.getItem("access_token");
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

  isAuthenticated(): boolean {
    return !!this.getToken();
  }

  isAdmin(): boolean {
    const user = this.getCurrentUser();
    return user?.is_admin === true;
  }

  /**
   * Check if JWT token is expired
   */
  isTokenExpired(): boolean {
    const token = this.getToken();
    if (!token) return true;

    try {
      // JWT token format: header.payload.signature
      const parts = token.split(".");
      if (parts.length !== 3) return true;

      // Decode payload (base64url)
      const payload = JSON.parse(
        atob(parts[1].replace(/-/g, "+").replace(/_/g, "/"))
      );

      // Check expiration
      if (!payload.exp) return true;
      const expirationTime = payload.exp * 1000; // Convert to milliseconds
      const now = Date.now();

      // Consider token expired if less than 1 minute remaining
      return now >= expirationTime - 60000;
    } catch (error) {
      console.error("Error checking token expiration:", error);
      return true;
    }
  }
}

export const authService = new AuthService();
