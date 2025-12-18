/**
 * 공통 API 클라이언트 베이스
 * 모든 API 요청의 기본 인프라 제공
 */

// eslint-disable-next-line @typescript-eslint/no-explicit-any
const getEnvVar = (key: string, defaultValue: string): string => {
  const env = (import.meta as any).env;
  return env?.[key] || defaultValue;
};

const API_BASE_URL = getEnvVar(
  "VITE_API_BASE_URL",
  "http://localhost:8000/api/v1"
);

export interface ApiResponse<T> {
  status: "success" | "error";
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: unknown;
  };
  message?: string;
}

export class BaseApiClient {
  protected baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  protected async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;

    // Get auth token
    const token = localStorage.getItem("access_token");

    // Check if body is FormData - if so, don't set Content-Type (browser will set it with boundary)
    const isFormData = options.body instanceof FormData;

    const headers: HeadersInit = {
      ...(isFormData ? {} : { "Content-Type": "application/json" }),
      ...options.headers,
    };

    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Handle 204 No Content (success with no body)
      if (response.status === 204) {
        return {
          status: "success",
        } as ApiResponse<T>;
      }

      // Check content type for JSON responses
      const contentType = response.headers.get("content-type");
      const isJson = contentType && contentType.includes("application/json");

      // If response is not OK and not JSON, return error immediately
      if (!response.ok && !isJson) {
        return {
          status: "error",
          error: {
            code: "HTTP_ERROR",
            message: `HTTP ${response.status}: ${response.statusText}`,
          },
        };
      }

      // Try to parse JSON response
      let data;
      try {
        // For non-JSON successful responses, return success
        if (response.ok && !isJson) {
          return {
            status: "success",
          } as ApiResponse<T>;
        }

        // Parse JSON (for both success and error responses)
        const text = await response.text();
        if (!text || text.trim() === "") {
          // Empty response
          if (response.ok) {
            return {
              status: "success",
            } as ApiResponse<T>;
          } else {
            return {
              status: "error",
              error: {
                code: "EMPTY_RESPONSE",
                message: `HTTP ${response.status}: ${response.statusText}`,
              },
            };
          }
        }
        data = JSON.parse(text);
      } catch (jsonError) {
        // If response is not JSON, return error
        return {
          status: "error",
          error: {
            code: "INVALID_JSON",
            message: response.ok
              ? "서버 응답을 파싱할 수 없습니다"
              : `HTTP ${response.status}: ${response.statusText}`,
          },
        };
      }

      if (!response.ok) {
        // FastAPI error format: {detail: "error message"} or {detail: {code: "...", message: "..."}}
        const errorDetail = data.detail || data.error || data;
        const errorMessage =
          typeof errorDetail === "string"
            ? errorDetail
            : errorDetail?.message ||
              errorDetail?.detail ||
              `HTTP ${response.status}: ${response.statusText}`;
        const errorCode =
          errorDetail?.code || this.getErrorCodeFromStatus(response.status);

        // If 401 Unauthorized, clear token and redirect to login
        if (response.status === 401) {
          console.log("[API] 401 Unauthorized - Token expired or invalid");
          localStorage.removeItem("access_token");
          localStorage.removeItem("user");

          // Trigger auth state change event
          window.dispatchEvent(new Event("auth:logout"));

          // Redirect to login if not already there
          if (window.location.pathname !== "/login") {
            window.location.href = "/login";
          }
        }

        return {
          status: "error",
          error: {
            code: errorCode,
            message: errorMessage,
            details: typeof errorDetail === "object" ? errorDetail : undefined,
          },
        };
      }

      // FastAPI returns data directly, wrap it in ApiResponse format
      return {
        status: "success",
        data: data,
      };
    } catch (error) {
      // Network error or fetch failed
      if (error instanceof TypeError && error.message === "Failed to fetch") {
        return {
          status: "error",
          error: {
            code: "NETWORK_ERROR",
            message: "서버에 연결할 수 없습니다. 네트워크 연결을 확인해주세요.",
          },
        };
      }

      return {
        status: "error",
        error: {
          code: "UNKNOWN_ERROR",
          message:
            error instanceof Error
              ? error.message
              : "알 수 없는 오류가 발생했습니다",
        },
      };
    }
  }

  private getErrorCodeFromStatus(status: number): string {
    switch (status) {
      case 400:
        return "BAD_REQUEST";
      case 401:
        return "UNAUTHORIZED";
      case 403:
        return "FORBIDDEN";
      case 404:
        return "NOT_FOUND";
      case 409:
        return "CONFLICT";
      case 422:
        return "VALIDATION_ERROR";
      case 500:
        return "INTERNAL_SERVER_ERROR";
      case 503:
        return "SERVICE_UNAVAILABLE";
      default:
        return "UNKNOWN_ERROR";
    }
  }

  async healthCheck(): Promise<
    ApiResponse<{ status: string; timestamp: string; version: string }>
  > {
    return this.request("/health");
  }
}

export const baseApiClient = new BaseApiClient();
