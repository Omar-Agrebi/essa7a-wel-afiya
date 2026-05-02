import { differenceInDays, parseISO, isPast, isToday } from 'date-fns'
import type { DeadlineUrgency } from '@/types'

export function getDeadlineUrgency(deadline: string | null): DeadlineUrgency {
  if (!deadline) return 'safe'
  const date = parseISO(deadline)
  if (isPast(date) && !isToday(date)) return 'expired'
  const days = differenceInDays(date, new Date())
  if (days <= 0) return 'critical'
  if (days <= 3) return 'critical'
  if (days <= 7) return 'urgent'
  if (days <= 14) return 'soon'
  if (days <= 30) return 'upcoming'
  return 'safe'
}

export function getDaysUntil(deadline: string | null): number | null {
  if (!deadline) return null
  return differenceInDays(parseISO(deadline), new Date())
}

export function getDeadlineDisplay(deadline: string | null): string {
  if (!deadline) return 'No deadline'
  const date = parseISO(deadline)
  if (isPast(date) && !isToday(date)) return 'Expired'
  const days = getDaysUntil(deadline)
  if (days === null) return 'No deadline'
  if (days === 0) return 'Today'
  if (days < 0) return 'Expired'
  if (days < 14) return `${days} day${days === 1 ? '' : 's'} left`
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

export function getUrgencyColors(urgency: DeadlineUrgency): {
  text: string
  bg: string
  border: string
  glow: string
} {
  switch (urgency) {
    case 'critical':
      return {
        text: 'text-red-300',
        bg: 'bg-red-900/40',
        border: 'border-red-600',
        glow: 'shadow-[0_0_12px_rgba(239,68,68,0.5)]',
      }
    case 'urgent':
      return {
        text: 'text-orange-300',
        bg: 'bg-orange-900/30',
        border: 'border-orange-600',
        glow: 'shadow-[0_0_8px_rgba(249,115,22,0.4)]',
      }
    case 'soon':
      return {
        text: 'text-yellow-300',
        bg: 'bg-yellow-900/20',
        border: 'border-yellow-600',
        glow: 'shadow-[0_0_6px_rgba(234,179,8,0.3)]',
      }
    case 'upcoming':
      return {
        text: 'text-blue-300',
        bg: 'bg-blue-900/20',
        border: 'border-blue-600',
        glow: '',
      }
    case 'expired':
      return {
        text: 'text-observatory-textMuted',
        bg: 'bg-observatory-surfaceLight/30',
        border: 'border-observatory-border',
        glow: '',
      }
    default:
      return {
        text: 'text-observatory-textSecondary',
        bg: 'bg-observatory-surfaceLight/20',
        border: 'border-observatory-border',
        glow: '',
      }
  }
}
