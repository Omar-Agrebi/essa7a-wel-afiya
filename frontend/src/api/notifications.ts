import apiClient from './client'
import type { Notification } from '@/types'

export async function getNotifications(): Promise<Notification[]> {
  const res = await apiClient.get<Notification[]>('/notifications/')
  return res.data
}

export async function getUnreadNotifications(): Promise<Notification[]> {
  const res = await apiClient.get<Notification[]>('/notifications/unread')
  return res.data
}

export async function getUnreadCount(): Promise<{ count: number }> {
  const res = await apiClient.get<{ count: number }>('/notifications/unread/count')
  return res.data
}

export async function markAsRead(id: string): Promise<Notification> {
  const res = await apiClient.put<Notification>(`/notifications/${id}/read`)
  return res.data
}

export async function markAllRead(): Promise<{ updated: number }> {
  const res = await apiClient.put<{ updated: number }>('/notifications/read-all')
  return res.data
}
