import { useState, useEffect, useRef } from 'react'
import { getUnreadCount } from '@/api/notifications'
import { useAuthStore } from '@/store/authStore'

export function useUnreadCount(): { count: number; loading: boolean } {
  const [count, setCount] = useState(0)
  const [loading, setLoading] = useState(false)
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const fetchCount = async () => {
    if (!isAuthenticated) return
    try {
      setLoading(true)
      const data = await getUnreadCount()
      setCount(data.count)
    } catch {
      // silently fail polling
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (!isAuthenticated) {
      setCount(0)
      return
    }
    fetchCount()
    intervalRef.current = setInterval(fetchCount, 60_000)
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current)
    }
  }, [isAuthenticated])

  return { count, loading }
}
