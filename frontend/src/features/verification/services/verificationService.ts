/**
 * Verification service for user verification API calls.
 */

import { BaseApiClient, ApiResponse } from "../../../lib/api/base";

export interface VerificationSubmit {
  school_name: string;
  department: string;
  major_category?: string;
  grade: string;
  student_id?: string;
  gender: "male" | "female" | "other";
  documents: string[];
}

export interface VerificationStatus {
  verification_id?: string;
  status?: "pending" | "approved" | "rejected" | null;
  school_name?: string;
  department?: string;
  major_category?: string;
  grade?: string;
  gender?: string;
  badge_visible?: boolean;
  department_visible?: boolean;
  verified_at?: string;
  message?: string;
}

export interface VerificationSettings {
  badge_visible?: boolean;
  department_visible?: boolean;
}

export interface VerificationResponse {
  verification_id: string;
  status: string;
  submitted_at: string;
  message: string;
}

class VerificationService extends BaseApiClient {
  /**
   * Submit verification request.
   */
  async submitVerification(data: VerificationSubmit): Promise<ApiResponse<VerificationResponse>> {
    return this.request<VerificationResponse>("/verification/submit", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  /**
   * Get current user's verification status.
   */
  async getStatus(): Promise<ApiResponse<VerificationStatus>> {
    const response = await this.request<VerificationStatus>("/verification/status");
    // FastAPI returns data directly, but BaseApiClient wraps it
    // If response has data field, use it; otherwise use response itself
    if (response.status === "success" && response.data) {
      return response;
    }
    // If error, return as is
    return response;
  }

  /**
   * Update verification display settings.
   */
  async updateSettings(settings: VerificationSettings): Promise<ApiResponse<{ message: string }>> {
    return this.request<{ message: string }>("/verification/settings", {
      method: "PATCH",
      body: JSON.stringify(settings),
    });
  }

  /**
   * Upload verification documents.
   */
  async uploadDocuments(files: File[]): Promise<ApiResponse<{ uploaded_files: string[]; count: number; encrypted: boolean }>> {
    const formData = new FormData();
    files.forEach((file) => {
      formData.append("files", file);
    });

    return this.request<{ uploaded_files: string[]; count: number; encrypted: boolean }>(
      "/verification/upload",
      {
        method: "POST",
        body: formData,
        // Content-Type will be automatically removed by BaseApiClient for FormData
      }
    );
  }
}

export const verificationService = new VerificationService();

