import { api } from "./api";
import type {
  AuthResponse,
  LoginPayload,
  NotificationItem,
  Opportunity,
  OpportunityFilterParams,
  PipelineStatus,
  Recommendation,
  RegisterPayload,
  User,
} from "@/types";

// Public
export async function fetchOpportunities(params: OpportunityFilterParams = {}): Promise<Opportunity[]> {
  const { data } = await api.get<Opportunity[]>("/opportunities", { params });
  return data;
}

export async function fetchOpportunity(id: string): Promise<Opportunity> {
  const { data } = await api.get<Opportunity>(`/opportunities/${id}`);
  return data;
}

export async function searchOpportunities(keyword: string): Promise<Opportunity[]> {
  const { data } = await api.get<Opportunity[]>("/opportunities/search", { params: { keyword } });
  return data;
}

export async function fetchExpiringOpportunities(days = 7): Promise<Opportunity[]> {
  const { data } = await api.get<Opportunity[]>("/opportunities/expiring", { params: { days } });
  return data;
}

// Auth
export async function registerUser(payload: RegisterPayload): Promise<User> {
  const { data } = await api.post<User>("/users/register", payload);
  return data;
}

export async function loginUser(payload: LoginPayload): Promise<AuthResponse> {
  const { data } = await api.post<AuthResponse>("/users/login", payload);
  return data;
}

// Protected — user
export async function fetchMe(): Promise<User> {
  const { data } = await api.get<User>("/users/me");
  return data;
}

export async function updateMe(payload: Partial<Pick<User, "name" | "email" | "level">>): Promise<User> {
  const { data } = await api.put<User>("/users/me", payload);
  return data;
}

export async function updateMySkills(skills: string[]): Promise<User> {
  const { data } = await api.put<User>("/users/me/skills", { skills });
  return data;
}

export async function updateMyInterests(interests: string[]): Promise<User> {
  const { data } = await api.put<User>("/users/me/interests", { interests });
  return data;
}

// Recommendations
export async function fetchRecommendations(top_n = 10): Promise<Recommendation[]> {
  const { data } = await api.get<Recommendation[]>("/recommendations", { params: { top_n } });
  return data;
}

export async function refreshRecommendations(): Promise<Recommendation[]> {
  const { data } = await api.post<Recommendation[]>("/recommendations/refresh");
  return data;
}

// Notifications
export async function fetchNotifications(): Promise<NotificationItem[]> {
  const { data } = await api.get<NotificationItem[]>("/notifications");
  return data;
}

export async function fetchUnreadNotifications(): Promise<NotificationItem[]> {
  const { data } = await api.get<NotificationItem[]>("/notifications/unread");
  return data;
}

export async function fetchUnreadCount(): Promise<number> {
  const { data } = await api.get<{ count: number } | number>("/notifications/unread/count");
  if (typeof data === "number") return data;
  return data.count;
}

export async function markNotificationRead(id: string): Promise<void> {
  await api.put(`/notifications/${id}/read`);
}

export async function markAllNotificationsRead(): Promise<void> {
  await api.put("/notifications/read-all");
}

// Pipeline
export async function runPipeline(): Promise<PipelineStatus> {
  const { data } = await api.post<PipelineStatus>("/pipeline/run");
  return data;
}

export async function fetchPipelineStatus(): Promise<PipelineStatus> {
  const { data } = await api.get<PipelineStatus>("/pipeline/status");
  return data;
}
