/**
 * TypeScript types for matching system.
 */

export interface UserVerification {
  verification_id: string;
  user_id: string;
  student_id?: string;
  university?: string;
  school_name?: string;
  department: string;
  student_id_image_url?: string | null;
  status: "pending" | "approved" | "rejected";
  rejection_reason?: string | null;
  verified_at?: string | null;
  created_at?: string;
  updated_at?: string;
  badge_visible?: boolean;
  department_visible?: boolean;
  message?: string;
}

export interface VerificationSubmit {
  school_name: string;
  department: string;
  major_category?: string;
  grade: string;
  student_id?: string;
  gender: "male" | "female" | "other";
  documents: string[];
}

export interface VerificationSettings {
  badge_visible?: boolean;
  department_visible?: boolean;
}

export interface MatchingPool {
  pool_id: string;
  creator_id: string;
  member_ids: string[];
  member_count: number;
  gender: string;
  university: string;
  department: string;
  grade: string;
  description?: string;
  age_range_min?: number;
  age_range_max?: number;
  preferred_match_type: string;
  preferred_categories: string[] | null;
  matching_type: string;
  message: string | null;
  status: "waiting" | "matched" | "expired" | "cancelled";
  created_at: string;
  expires_at: string;
  updated_at: string;
}

export interface MatchingPoolCreate {
  member_ids: string[];
  gender: "male" | "female" | "mixed";
  university: string;
  department: string;
  age_range_min: number;
  age_range_max: number;
  matching_type: "blind" | "open";
  preferred_universities?: string[];
  preferred_departments?: string[];
  preferred_age_min?: number;
  preferred_age_max?: number;
  description?: string;
}

export interface MatchingProposal {
  proposal_id: string;
  pool_id_a: string;
  pool_id_b: string;
  group_a_status: "pending" | "accepted" | "rejected";
  group_b_status: "pending" | "accepted" | "rejected";
  final_status: "pending" | "matched" | "rejected";
  chat_room_id: string | null;
  created_at: string;
  expires_at: string;
  matched_at: string | null;
  pool_a?: MatchingPool | null;
  pool_b?: MatchingPool | null;
}


export interface ProposalAction {
  action: "accept" | "reject";
}

export interface MatchingPoolStats {
  total_waiting: number;
  total_all: number;
  total_matched: number;
  total_expired: number;
  by_status: Record<string, number>;
  by_member_count: Record<string, number>;
  by_gender: Record<string, number>;
  by_department: Record<string, number>;
  by_matching_type: Record<string, number>;
  average_wait_time_hours: number;
}

export interface ComprehensiveMatchingStats {
  pools: MatchingPoolStats;
  proposals: {
    total_proposals: number;
    by_status: Record<string, number>;
    matched_count: number;
    success_rate: number;
    acceptance_rate: number;
    rejection_rate: number;
    pending_count: number;
    average_matching_time_hours: number;
    min_matching_time_hours: number;
    max_matching_time_hours: number;
    daily_matches: Array<{ date: string; count: number }>;
    weekly_matches: Array<{ week: string; count: number }>;
    monthly_matches: Array<{ month: string; count: number }>;
  };
}
