import apiClient from './client'
import type { TokenResponse, User, RegisterData } from '@/types'

export async function login(email: string, password: string): Promise<TokenResponse> {
  const res = await apiClient.post<TokenResponse>('/users/login', { email, password })
  return res.data
}

export async function register(data: RegisterData): Promise<User> {
  const res = await apiClient.post<User>('/users/register', data)
  return res.data
}

export async function getMe(): Promise<User> {
  const res = await apiClient.get<User>('/users/me')
  return res.data
}

export async function updateProfile(data: Partial<Omit<User, 'user_id' | 'created_at'>>): Promise<User> {
  const res = await apiClient.put<User>('/users/me', data)
  return res.data
}

// Backend expects { skills: string[] } body dict
export async function updateSkills(skills: string[]): Promise<User> {
  const res = await apiClient.put<User>('/users/me/skills', { skills })
  return res.data
}

// Backend expects { interests: string[] } body dict
export async function updateInterests(interests: string[]): Promise<User> {
  const res = await apiClient.put<User>('/users/me/interests', { interests })
  return res.data
}
