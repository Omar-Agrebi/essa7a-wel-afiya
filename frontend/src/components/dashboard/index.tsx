import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Radio, CheckCircle, Loader2, BellOff, Rocket, Clock } from 'lucide-react'
import type { Recommendation, Notification, PipelineStatusResponse } from '@/types'
import { formatRelativeTime, formatScore, getTypeColor } from '@/utils/formatting'
import { getDeadlineUrgency, getUrgencyColors, getDaysUntil } from '@/utils/deadline'
import { GlassCard, GlowButton, EmptyState } from '@/components/ui'
import { clsx } from 'clsx'
import { triggerFullPipeline } from '@/api/pipeline'
import toast from 'react-hot-toast'

// ─── MissionCard ─────────────────────────────────────────────────────────────
interface MissionCardProps {
  recommendation: Recommendation
  rank: number
  animationDelay?: number
}

export function MissionCard({ recommendation, rank, animationDelay = 0 }: MissionCardProps) {
  const navigate = useNavigate()
  const { opportunity, score, match_reasons } = recommendation
  const typeColors = getTypeColor(opportunity.type)
  const urgency = getDeadlineUrgency(opportunity.deadline)
  const urgencyColors = getUrgencyColors(urgency)
  const days = getDaysUntil(opportunity.deadline)

  const status =
    urgency === 'critical' || urgency === 'urgent'
      ? 'CLOSING SOON'
      : urgency === 'expired'
        ? 'CLOSED'
        : 'OPEN'

  const statusColor =
    status === 'CLOSING SOON' ? 'text-orange-400' :
      status === 'CLOSED' ? 'text-observatory-textMuted' :
        'text-emerald-400'

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: animationDelay, duration: 0.4 }}
    >
      <GlassCard className="p-4 space-y-3 hover:border-observatory-primary hover:shadow-[0_0_16px_rgba(30,64,175,0.25)] transition-all duration-300">
        <div className="flex items-start justify-between gap-2">
          <span className="font-mono text-xs text-observatory-textMuted">
            MISSION #{String(rank).padStart(3, '0')}
          </span>
          <span className={clsx('font-mono text-xs font-bold', statusColor)}>{status}</span>
        </div>

        <h3 className="font-display font-semibold text-sm text-observatory-textPrimary line-clamp-2">
          {opportunity.title}
        </h3>

        <div className="flex items-center gap-2 flex-wrap">
          <span className={clsx('px-2 py-0.5 rounded-full text-xs border', typeColors.text, typeColors.bg, typeColors.border)}>
            {opportunity.type}
          </span>
          {days !== null && days >= 0 && (
            <span className={clsx('text-xs font-mono', urgencyColors.text)}>
              {days === 0 ? 'Today' : `${days}d left`}
            </span>
          )}
        </div>

        {/* Score bar */}
        <div className="space-y-1">
          <div className="flex justify-between text-xs">
            <span className="text-observatory-textMuted font-mono">MATCH</span>
            <span className="font-mono text-observatory-textPrimary font-bold">{formatScore(score)}</span>
          </div>
          <div className="h-1 bg-observatory-surfaceLight rounded-full overflow-hidden">
            <motion.div
              className="h-full rounded-full bg-gradient-to-r from-observatory-primary to-observatory-accent"
              initial={{ width: 0 }}
              animate={{ width: `${Math.round(score * 100)}%` }}
              transition={{ duration: 1, ease: 'easeOut', delay: animationDelay + 0.3 }}
            />
          </div>
        </div>

        {match_reasons.length > 0 && (
          <p className="text-xs text-observatory-textMuted line-clamp-1 italic">{match_reasons[0]}</p>
        )}

        <GlowButton
          variant="ghost"
          size="sm"
          className="w-full"
          onClick={() => navigate(`/opportunities/${opportunity.id}`)}
        >
          <Rocket className="w-3.5 h-3.5" /> Initiate
        </GlowButton>
      </GlassCard>
    </motion.div>
  )
}

// ─── SystemStatus ─────────────────────────────────────────────────────────────
interface SystemStatusProps { pipelineStatus: PipelineStatusResponse }

export function SystemStatus({ pipelineStatus }: SystemStatusProps) {
  const [running, setRunning] = useState(false)
  const isNeverRun = 'status' in pipelineStatus && pipelineStatus.status === 'never_run'
  const status = isNeverRun ? null : (pipelineStatus as Exclude<PipelineStatusResponse, { status: 'never_run' }>)

  const handleRun = async () => {
    setRunning(true)
    try {
      await triggerFullPipeline()
      toast.success('Pipeline sequence initiated')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed to start pipeline')
    } finally {
      setTimeout(() => setRunning(false), 3000)
    }
  }

  const fields = status ? [
    { label: 'LAST RUN', value: formatRelativeTime(String(status.pipeline || '')) || 'Unknown' },
    { label: 'ITEMS SCRAPED', value: String(status.raw_collected ?? 0) },
    { label: 'CLEANED', value: String(status.cleaned ?? 0) },
    { label: 'CLASSIFIED', value: String(status.classified ?? 0) },
    { label: 'RECOMMENDATIONS', value: String(status.recommendations_generated ?? 0) },
    { label: 'DURATION', value: status.duration_sec ? `${status.duration_sec.toFixed(1)}s` : '—' },
  ] : []

  return (
    <GlassCard className="p-4">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="font-mono text-xs font-bold text-observatory-textSecondary tracking-wider">
            SYSTEM STATUS
          </span>
          <span className={clsx('w-2 h-2 rounded-full', isNeverRun ? 'bg-observatory-textMuted' : 'bg-emerald-400 animate-pulse')} />
        </div>
        <GlowButton variant="ghost" size="sm" loading={running} onClick={handleRun}>
          {running ? 'INITIATING...' : 'Run Pipeline'}
        </GlowButton>
      </div>

      {isNeverRun ? (
        <p className="text-xs font-mono text-observatory-textMuted">Pipeline has never been run.</p>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 gap-x-6 gap-y-1">
          {fields.map(({ label, value }) => (
            <div key={label} className="flex items-center justify-between gap-2">
              <span className="text-xs font-mono text-observatory-textMuted">{label}:</span>
              <span className="text-xs font-mono text-emerald-400">{value}</span>
            </div>
          ))}
        </div>
      )}

      {status && status.pipeline_errors?.length > 0 && (
        <div className="mt-3 pt-3 border-t border-observatory-border">
          <p className="text-xs font-mono text-red-400">⚠ {status.pipeline_errors.length} error(s) in last run</p>
        </div>
      )}
    </GlassCard>
  )
}

// ─── TransmissionPanel ────────────────────────────────────────────────────────
interface TransmissionPanelProps {
  notifications: Notification[]
  onMarkRead: (id: string) => void
  onMarkAllRead: () => void
}

export function TransmissionPanel({ notifications, onMarkRead, onMarkAllRead }: TransmissionPanelProps) {
  const navigate = useNavigate()
  const unread = notifications.filter((n) => n.status === 'unread')

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Radio className="w-4 h-4 text-observatory-accent" />
          <span className="font-mono text-xs font-bold text-observatory-textSecondary tracking-wider">
            INCOMING TRANSMISSIONS
          </span>
          {unread.length > 0 && (
            <span className="px-1.5 py-0.5 bg-observatory-accent/20 text-observatory-accentLight text-xs rounded-full font-mono">
              {unread.length}
            </span>
          )}
        </div>
        {unread.length > 0 && (
          <button
            onClick={onMarkAllRead}
            className="text-xs text-observatory-textMuted hover:text-observatory-textSecondary transition-colors font-mono"
          >
            Clear All
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <EmptyState
          icon={<BellOff className="w-10 h-10" />}
          title="No incoming transmissions"
          description="You're all caught up. Check back after the next pipeline run."
        />
      ) : (
        <div className="space-y-2 max-h-[400px] overflow-y-auto pr-1">
          <AnimatePresence>
            {notifications.filter(n => n.opportunity).slice(0, 10).map((notif) => (
              <motion.div
                key={notif.notification_id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                exit={{ opacity: 0, x: 20 }}
                className={clsx(
                  'relative p-3 rounded-lg border transition-all cursor-pointer',
                  notif.status === 'unread'
                    ? 'border-observatory-accent/40 bg-observatory-accent/5 hover:bg-observatory-accent/10'
                    : 'border-observatory-border bg-observatory-surface/50 opacity-60'
                )}
                onClick={() => {
                  if (notif.status === 'unread') onMarkRead(notif.notification_id)
                  if (notif.opportunity) navigate(`/opportunities/${notif.opportunity.id}`)
                }}
              >
                {notif.status === 'unread' && (
                  <div className="absolute left-0 top-2 bottom-2 w-0.5 rounded-full bg-observatory-accent" />
                )}
                <p className="text-xs text-observatory-textPrimary pr-4 leading-relaxed">{notif.message}</p>
                <div className="flex items-center justify-between mt-1.5">
                  <span className="text-xs font-mono text-observatory-accent truncate">{notif.opportunity?.title}</span>
                  <span className="text-xs font-mono text-observatory-textMuted ml-2 flex-shrink-0">
                    {formatRelativeTime(notif.timestamp)}
                  </span>
                </div>
                {notif.status === 'unread' && (
                  <button
                    onClick={(e) => { e.stopPropagation(); onMarkRead(notif.notification_id) }}
                    className="absolute top-2 right-2"
                  >
                    <CheckCircle className="w-3.5 h-3.5 text-observatory-textMuted hover:text-observatory-accent transition-colors" />
                  </button>
                )}
              </motion.div>
            ))}
          </AnimatePresence>
        </div>
      )}
    </div>
  )
}
