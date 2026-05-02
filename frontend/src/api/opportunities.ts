import apiClient from './client'
import type { Opportunity, OpportunityFilters } from '@/types'

export async function getOpportunities(
  filters?: OpportunityFilters,
  skip = 0,
  limit = 50
): Promise<Opportunity[]> {
  const params: Record<string, string | number | undefined> = { skip, limit }
  if (filters?.type) params.type = filters.type
  if (filters?.category) params.category = filters.category
  if (filters?.keyword) params.keyword = filters.keyword
  if (filters?.cluster_id !== undefined) params.cluster_id = filters.cluster_id
  if (filters?.expiring_in_days !== undefined) params.expiring_in_days = filters.expiring_in_days

  const res = await apiClient.get<Opportunity[]>('/opportunities/', { params })
  return res.data
}

export async function getOpportunity(id: string): Promise<Opportunity> {
  const res = await apiClient.get<Opportunity>(`/opportunities/${id}`)
  return res.data
}

export async function searchOpportunities(keyword: string): Promise<Opportunity[]> {
  const res = await apiClient.get<Opportunity[]>('/opportunities/search', {
    params: { keyword },
  })
  return res.data
}

export async function getExpiringSoon(days = 7): Promise<Opportunity[]> {
  const res = await apiClient.get<Opportunity[]>('/opportunities/expiring', {
    params: { days },
  })
  return res.data
}

export async function createOpportunity(
  data: Partial<Opportunity>
): Promise<Opportunity> {
  const res = await apiClient.post<Opportunity>('/opportunities/', data)
  return res.data
}
