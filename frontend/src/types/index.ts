export type OpportunityType =
  | "internship"
  | "scholarship"
  | "project"
  | "course"
  | "postdoc";

export type OpportunityCategory =
  | "AI"
  | "Data_Science"
  | "Cybersecurity"
  | "Software_Engineering"
  | "Other";

export type UserLevel = "bachelor" | "master" | "phd" | "professional";

export type NotificationStatus = "unread" | "read" | "dismissed";

export interface Opportunity {
  id: string;
  title: string;
  type: OpportunityType;
  category: OpportunityCategory;
  description: string;
  skills_required: string[];
  location: string;
  eligibility: string;
  deadline: string;
  source: string;
  url: string;
  cluster_id?: number | null;
  cluster_label?: string | null;
}

export interface User {
  id: string;
  name: string;
  email: string;
  skills: string[];
  interests: string[];
  level: UserLevel;
  created_at?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Recommendation {
  score: number;
  match_reasons: string[];
  opportunity: Opportunity;
}

export interface NotificationItem {
  id: string;
  user_id: string;
  opportunity_id?: string | null;
  title: string;
  message: string;
  status: NotificationStatus;
  created_at: string;
}

export interface PipelineStatus {
  status: "idle" | "running" | "completed" | "failed";
  last_run?: string | null;
  last_success?: string | null;
  message?: string | null;
}

export interface OpportunityFilterParams {
  type?: OpportunityType;
  category?: OpportunityCategory;
  keyword?: string;
  cluster_id?: number;
  expiring_in_days?: number;
  skip?: number;
  limit?: number;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
  skills: string[];
  interests: string[];
  level: UserLevel;
}

export interface LoginPayload {
  email: string;
  password: string;
}
