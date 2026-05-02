// Exact mirror of backend constants.py enums
export type OpportunityType = 'internship' | 'scholarship' | 'project' | 'course' | 'postdoc'

// Backend uses "Data Science" and "Software Engineering" with spaces
export type OpportunityCategory =
  | 'AI'
  | 'Data Science'
  | 'Cybersecurity'
  | 'Software Engineering'
  | 'Other'

export type UserLevel = 'bachelor' | 'master' | 'phd' | 'professional'

export type NotificationStatus = 'unread' | 'read' | 'dismissed'

// Matches OpportunityRead schema exactly
export interface Opportunity {
  id: string                    // UUID
  title: string
  type: OpportunityType
  category: OpportunityCategory
  description: string | null
  skills_required: string[]
  location: string | null
  eligibility: string | null
  deadline: string | null       // "YYYY-MM-DD" date string
  source: string
  url: string
  cluster_id: number | null
  cluster_label: string | null
  created_at: string            // ISO datetime
  updated_at: string            // ISO datetime
}

// Matches UserRead schema exactly
export interface User {
  user_id: string               // UUID
  name: string
  email: string
  skills: string[]
  interests: string[]
  level: UserLevel
  created_at: string
}

// Matches RecommendationRead schema exactly
export interface Recommendation {
  recommendation_id: string     // UUID
  score: number                 // 0.0 to 1.0
  match_reasons: string[]
  opportunity: Opportunity      // fully nested
  created_at: string
}

// Matches NotificationRead schema exactly
export interface Notification {
  notification_id: string       // UUID
  message: string
  status: NotificationStatus
  timestamp: string             // ISO datetime
  opportunity: Opportunity      // fully nested
}

// Matches TokenResponse schema exactly
export interface TokenResponse {
  access_token: string
  token_type: 'bearer'
  user: User
}

// For API filters
export interface OpportunityFilters {
  type?: OpportunityType
  category?: OpportunityCategory
  keyword?: string
  cluster_id?: number
  expiring_in_days?: number
}

// For registration form
export interface RegisterData {
  name: string
  email: string
  password: string
  skills: string[]
  interests: string[]
  level: UserLevel
}

// API error shape
export interface ApiError {
  detail: string
  type?: string
}

// Pipeline status from GET /pipeline/status
export interface PipelineStatus {
  pipeline: string
  status: string
  run_number: number
  duration_sec: number
  raw_collected: number
  cleaned: number
  classified: number
  clustered: number
  recommendations_generated: number
  agent_reports: Record<string, unknown>[]
  pipeline_errors: string[]
}

export type PipelineStatusResponse = PipelineStatus | { status: 'never_run' }

export type ViewMode = 'grid' | 'list'

export type DeadlineUrgency = 'safe' | 'upcoming' | 'soon' | 'urgent' | 'critical' | 'expired'
