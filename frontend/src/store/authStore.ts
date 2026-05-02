import { create } from 'zustand'
import type { User } from '@/types'

const STORAGE_KEY = 'observatory_auth'

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
}

interface AuthActions {
  login: (token: string, user: User) => void
  logout: () => void
  loadFromStorage: () => void
  updateUser: (user: User) => void
}

type AuthStore = AuthState & AuthActions

export const useAuthStore = create<AuthStore>((set) => ({
  user: null,
  token: null,
  isAuthenticated: false,

  login: (token, user) => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify({ token, user }))
    set({ token, user, isAuthenticated: true })
  },

  logout: () => {
    localStorage.removeItem(STORAGE_KEY)
    set({ token: null, user: null, isAuthenticated: false })
  },

  loadFromStorage: () => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (raw) {
        const { token, user } = JSON.parse(raw) as { token: string; user: User }
        if (token && user) {
          set({ token, user, isAuthenticated: true })
        }
      }
    } catch {
      localStorage.removeItem(STORAGE_KEY)
    }
  },

  updateUser: (user) => {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw) as { token: string; user: User }
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...parsed, user }))
    }
    set({ user })
  },
}))
