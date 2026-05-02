import { formatDistanceToNow, parseISO, format } from 'date-fns'
import type { OpportunityType, OpportunityCategory } from '@/types'

export function formatRelativeTime(dateString: string): string {
  try {
    return formatDistanceToNow(parseISO(dateString), { addSuffix: true })
  } catch {
    return dateString
  }
}

export function formatDate(dateString: string): string {
  try {
    return format(parseISO(dateString), 'MMM d, yyyy')
  } catch {
    return dateString
  }
}

export function formatScore(score: number): string {
  return `${Math.round(score * 100)}%`
}

export function getTypeColor(type: OpportunityType): {
  text: string
  bg: string
  border: string
} {
  switch (type) {
    case 'internship':
      return { text: 'text-blue-300', bg: 'bg-blue-900/50', border: 'border-blue-700' }
    case 'scholarship':
      return { text: 'text-emerald-300', bg: 'bg-emerald-900/50', border: 'border-emerald-700' }
    case 'project':
      return { text: 'text-purple-300', bg: 'bg-purple-900/50', border: 'border-purple-700' }
    case 'course':
      return { text: 'text-yellow-300', bg: 'bg-yellow-900/50', border: 'border-yellow-700' }
    case 'postdoc':
      return { text: 'text-orange-300', bg: 'bg-orange-900/50', border: 'border-orange-700' }
  }
}

export function getCategoryColor(category: OpportunityCategory): string {
  switch (category) {
    case 'AI':
      return 'text-violet-400'
    case 'Data Science':
      return 'text-cyan-400'
    case 'Cybersecurity':
      return 'text-red-400'
    case 'Software Engineering':
      return 'text-green-400'
    default:
      return 'text-observatory-textMuted'
  }
}

export function getMatchReasonIcon(reason: string): string {
  const lower = reason.toLowerCase()
  if (lower.includes('skill')) return 'Zap'
  if (lower.includes('level')) return 'GraduationCap'
  if (lower.includes('deadline') || lower.includes('day')) return 'Clock'
  if (lower.includes('interest') || lower.includes('category')) return 'Target'
  return 'CheckCircle'
}

export function getInitials(name: string): string {
  return name
    .split(' ')
    .map((n) => n[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

export function getLevelLabel(level: string): string {
  switch (level) {
    case 'bachelor': return 'BACHELOR CLEARANCE'
    case 'master': return 'MASTER CLEARANCE'
    case 'phd': return 'PHD CLEARANCE'
    case 'professional': return 'FIELD OPERATIVE'
    default: return level.toUpperCase()
  }
}
