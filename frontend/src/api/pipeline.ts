import apiClient from './client'
import type { PipelineStatusResponse } from '@/types'

export async function triggerFullPipeline(): Promise<{ message: string; mode: string }> {
  const res = await apiClient.post<{ message: string; mode: string }>('/pipeline/run')
  return res.data
}

export async function triggerScraping(): Promise<{ message: string }> {
  const res = await apiClient.post<{ message: string }>('/pipeline/run/scraping')
  return res.data
}

export async function triggerRecommendations(userId?: string): Promise<{ message: string }> {
  const res = await apiClient.post<{ message: string }>('/pipeline/run/recommendations', null, {
    params: userId ? { user_id: userId } : {},
  })
  return res.data
}

export async function getPipelineStatus(): Promise<PipelineStatusResponse> {
  const res = await apiClient.get<PipelineStatusResponse>('/pipeline/status')
  return res.data
}

export async function checkHealth(): Promise<{ status: string; version: string; environment: string; scraper_mode: string }> {
  const res = await apiClient.get('/health/')
  return res.data
}
