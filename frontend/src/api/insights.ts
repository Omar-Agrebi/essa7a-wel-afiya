import apiClient from './client'

// ── Public insights (no auth) ─────────────────────────────────────────────────
export interface SkillFrequency { skill: string; count: number }
export interface ClusterInfo {
  cluster_id: number
  label: string
  total: number
  by_type: Record<string, number>
  by_category: Record<string, number>
  top_skills: string[]
}
export interface PublicInsights {
  total_opportunities: number
  total_unique_skills: number
  skill_frequency: SkillFrequency[]
  clusters: ClusterInfo[]
  deadline_distribution: Record<string, number>
  type_distribution: Record<string, number>
  category_distribution: Record<string, number>
}

// ── Personal insights (auth required) ────────────────────────────────────────
export interface SkillGenomeItem {
  skill: string
  frequency: number
  status: 'matched' | 'gap' | 'irrelevant'
  in_top_cluster: boolean
}
export interface RadarPoint {
  cluster: string
  cluster_id: number
  user_coverage: number
  ideal: number
}
export interface SkillGap {
  skill: string
  unlocks: number
  frequency: number
}
export interface ScoreComponents {
  semantic_similarity: number
  level_alignment: number
  deadline_recency: number
}
export interface ScoreAnatomy {
  opportunity_id: string
  title: string
  type: string
  category: string
  total_score: number
  components: ScoreComponents
  skill_overlap: string[]
  deadline_days: number | null
  eligibility: string | null
  match_reasons: string[]
}
export interface LandscapePoint {
  id: string
  title: string
  type: string
  category: string
  score: number
  deadline_days: number
  skill_match_count: number
  url: string
}
export interface PersonalInsights {
  user: { name: string; level: string; skills: string[]; skill_count: number }
  top_cluster: { cluster_id: number; label: string; coverage_pct: number; matched: number; total: number }
  skill_genome: SkillGenomeItem[]
  radar_data: RadarPoint[]
  skill_gaps: SkillGap[]
  score_anatomy: ScoreAnatomy[]
  landscape: LandscapePoint[]
}

export async function getPublicInsights(): Promise<PublicInsights> {
  const res = await apiClient.get<PublicInsights>('/insights/public')
  return res.data
}

export async function getPersonalInsights(): Promise<PersonalInsights> {
  const res = await apiClient.get<PersonalInsights>('/insights/personal')
  return res.data
}
