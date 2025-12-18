/**
 * Common API response types
 */

export interface ApiError {
  code: number;
  message: string;
  details?: any;
}

export interface ApiResponse<T> {
  status: "success" | "error";
  data?: T;
  error?: ApiError;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
  has_more: boolean;
}

export interface ListResponse<T> {
  data: T[];
  total: number;
}
