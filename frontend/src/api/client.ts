/**
 * API client configuration using axios.
 */

import axios, { AxiosInstance, AxiosError } from "axios";

// Get API base URL from environment variable, with fallback
const getApiBaseUrl = () => {
  // Always check for environment variable first (works in both dev and prod)
  const envUrl = import.meta.env.VITE_API_BASE_URL;
  if (envUrl) {
    return envUrl;
  }

  // In production without env var, try to detect if we're on the same domain
  // If backend is on different domain, this will fail - user must set VITE_API_BASE_URL
  if (import.meta.env.PROD) {
    // Try to use same origin (assumes proxy or same domain)
    // Note: This assumes backend is proxied through Vercel or on same domain
    const origin = window.location.origin;
    return `${origin}/api/v1`;
  }

  // In development, use localhost
  return "http://localhost:8000/api/v1";
};

const API_BASE_URL = getApiBaseUrl();

// Create axios instance
export const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
  withCredentials: true,
});

// Request interceptor - Add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token
      localStorage.removeItem("access_token");

      // Only redirect to login if not on home page or login page
      // Home page should be accessible without authentication
      const currentPath = window.location.pathname;
      if (currentPath !== "/" && currentPath !== "/login") {
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
