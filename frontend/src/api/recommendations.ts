import apiClient from './client'
import type { Recommendation } from '@/types'

export async function getRecommendations(topN = 10): Promise<Recommendation[]> {
  const res = await apiClient.get<Recommendation[]>('/recommendations/', {
    params: { top_n: topN },
  })
  return res.data
}

export async function refreshRecommendations(): Promise<{ message: string; count: number }> {
  const res = await apiClient.post<{ message: string; count: number }>('/recommendations/refresh')
  return res.data
}
