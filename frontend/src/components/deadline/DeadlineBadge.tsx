import { Calendar, Clock, AlertTriangle } from 'lucide-react'
import { clsx } from 'clsx'
import { getDeadlineUrgency, getDeadlineDisplay, getDaysUntil, getUrgencyColors } from '@/utils/deadline'

interface DeadlineBadgeProps {
  deadline: string | null
  showCountdown?: boolean
  size?: 'sm' | 'md'
}

export default function DeadlineBadge({ deadline, showCountdown = false, size = 'sm' }: DeadlineBadgeProps) {
  const urgency = getDeadlineUrgency(deadline)
  const colors = getUrgencyColors(urgency)
  const display = getDeadlineDisplay(deadline)
  const days = getDaysUntil(deadline)

  const isCritical = urgency === 'critical' || urgency === 'urgent'

  const Icon = isCritical ? AlertTriangle : urgency === 'expired' ? Clock : Calendar

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 rounded-full border font-mono',
        size === 'sm' ? 'px-2.5 py-1 text-xs' : 'px-3 py-1.5 text-sm',
        colors.text,
        colors.bg,
        colors.border,
        colors.glow,
        isCritical && 'animate-pulse'
      )}
    >
      <Icon className={size === 'sm' ? 'w-3 h-3' : 'w-4 h-4'} />
      <span>{display}</span>
      {showCountdown && days !== null && days > 0 && days <= 7 && (
        <span className="opacity-70">({days}d)</span>
      )}
    </span>
  )
}
