/**
 * Reports API client functions
 */

import api from "./client";

export interface ReportCreate {
  reported_user_id?: string;
  proposal_id?: string;
  pool_id?: string;
  report_type: "inappropriate_behavior" | "spam" | "harassment" | "fake_profile" | "other";
  reason: string;
}

export interface Report {
  report_id: string;
  reporter_id: string;
  reported_user_id?: string | null;
  proposal_id?: string | null;
  pool_id?: string | null;
  report_type: string;
  reason: string;
  status: "pending" | "reviewed" | "resolved" | "dismissed";
  admin_note?: string | null;
  reviewed_by?: string | null;
  reviewed_at?: string | null;
  created_at: string;
}

// Create a new report
export const createReport = async (data: ReportCreate): Promise<Report> => {
  const response = await api.post<Report>("/reports", data);
  return response.data;
};

// Get my reports
export const getMyReports = async (limit: number = 50): Promise<Report[]> => {
  const response = await api.get<Report[]>(`/reports/my?limit=${limit}`);
  return response.data;
};

// Get report by ID
export const getReport = async (reportId: string): Promise<Report> => {
  const response = await api.get<Report>(`/reports/${reportId}`);
  return response.data;
};

