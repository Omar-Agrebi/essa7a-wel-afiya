import { useEffect, useState, useCallback } from 'react'
import { motion } from 'framer-motion'
import { RefreshCw, Clock, Bell, Rocket, ChevronDown, ChevronUp, AlertTriangle } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { getRecommendations, refreshRecommendations } from '@/api/recommendations'
import { getUnreadNotifications, markAsRead, markAllRead } from '@/api/notifications'
import { getPipelineStatus } from '@/api/pipeline'
import type { Recommendation, Notification, PipelineStatusResponse } from '@/types'
import { getDaysUntil } from '@/utils/deadline'
import PageWrapper from '@/components/layout/PageWrapper'
import { MissionCard, SystemStatus, TransmissionPanel } from '@/components/dashboard'
import { GlassCard, GlowButton, EmptyState, LoadingSpinner, CountUpNumber } from '@/components/ui'
import { triggerFullPipeline } from '@/api/pipeline'
import toast from 'react-hot-toast'

export default function DashboardPage() {
  const { user } = useAuthStore()
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [notifications, setNotifications] = useState<Notification[]>([])
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatusResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)
  const [statusOpen, setStatusOpen] = useState(false)

  const load = useCallback(async () => {
    try {
      const [recs, notifs, status] = await Promise.all([
        getRecommendations(10),
        getUnreadNotifications(),
        getPipelineStatus(),
      ])
      setRecommendations(recs)
      setNotifications(notifs)
      setPipelineStatus(status)
    } catch {
      // silently handle partial failures
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const handleRefresh = async () => {
    setRefreshing(true)
    try {
      await refreshRecommendations()
      const recs = await getRecommendations(10)
      setRecommendations(recs)
      toast.success('Mission briefings updated')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Refresh failed')
    } finally {
      setRefreshing(false)
    }
  }

  const handleMarkRead = async (id: string) => {
    try {
      await markAsRead(id)
      setNotifications((n) => n.filter((x) => x.notification_id !== id))
    } catch { /* ignore */ }
  }

  const handleMarkAllRead = async () => {
    try {
      await markAllRead()
      setNotifications([])
    } catch { /* ignore */ }
  }

  const urgentCount = recommendations.filter((r) => {
    const days = getDaysUntil(r.opportunity.deadline)
    return days !== null && days >= 0 && days <= 7
  }).length

  const handleLaunchPipeline = async () => {
    try {
      await triggerFullPipeline()
      toast.success('Pipeline sequence initiated')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed')
    }
  }

  if (loading) {
    return (
      <PageWrapper>
        <div className="pt-32 flex justify-center">
          <LoadingSpinner size="lg" label="LOADING MISSION CONTROL..." />
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      <div className="pt-20 pb-16 max-w-7xl mx-auto px-4">
        {/* ── COMMAND HEADER ── */}
        <div className="mb-8">
          <p className="font-mono text-xs text-observatory-accent tracking-widest mb-1">MISSION CONTROL</p>
          <h1 className="font-display font-bold text-3xl text-observatory-textPrimary">
            Welcome back, {user?.name?.split(' ')[0]}
          </h1>
          {urgentCount > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -8 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-4 flex items-center gap-3 p-3 rounded-xl border border-orange-700 bg-orange-900/20"
            >
              <AlertTriangle className="w-5 h-5 text-orange-400 flex-shrink-0 animate-pulse" />
              <span className="text-sm text-orange-300">
                {urgentCount} opportunity{urgentCount > 1 ? 'ies' : 'y'} closing this week — act fast.
              </span>
            </motion.div>
          )}
        </div>

        {/* ── STATS ROW ── */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <GlassCard className="p-5 flex items-center gap-4">
            <div className="w-10 h-10 rounded-xl bg-observatory-accent/20 flex items-center justify-center">
              <Rocket className="w-5 h-5 text-observatory-accent" />
            </div>
            <div>
              <p className="font-mono text-xs text-observatory-textMuted">ACTIVE MISSIONS</p>
              <p className="font-display font-bold text-3xl text-observatory-textPrimary">
                <CountUpNumber value={recommendations.length} />
              </p>
            </div>
          </GlassCard>

          <GlassCard className="p-5 flex items-center gap-4">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${urgentCount > 0 ? 'bg-orange-900/30' : 'bg-observatory-surfaceLight'}`}>
              <Clock className={`w-5 h-5 ${urgentCount > 0 ? 'text-orange-400' : 'text-observatory-textMuted'}`} />
            </div>
            <div>
              <p className="font-mono text-xs text-observatory-textMuted">CLOSING THIS WEEK</p>
              <p className={`font-display font-bold text-3xl ${urgentCount > 0 ? 'text-orange-400' : 'text-observatory-textPrimary'}`}>
                <CountUpNumber value={urgentCount} />
              </p>
            </div>
          </GlassCard>

          <GlassCard className="p-5 flex items-center gap-4">
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${notifications.length > 0 ? 'bg-observatory-accent/20' : 'bg-observatory-surfaceLight'}`}>
              <Bell className={`w-5 h-5 ${notifications.length > 0 ? 'text-observatory-accent' : 'text-observatory-textMuted'}`} />
            </div>
            <div>
              <p className="font-mono text-xs text-observatory-textMuted">TRANSMISSIONS</p>
              <p className={`font-display font-bold text-3xl ${notifications.length > 0 ? 'text-observatory-accentLight' : 'text-observatory-textPrimary'}`}>
                <CountUpNumber value={notifications.length} />
              </p>
            </div>
          </GlassCard>
        </div>

        {/* ── MAIN GRID ── */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left: Missions */}
          <div className="lg:col-span-2 space-y-4">
            <div className="flex items-center justify-between">
              <p className="font-mono text-xs font-bold text-observatory-textSecondary tracking-wider">ACTIVE MISSIONS</p>
              <GlowButton variant="ghost" size="sm" loading={refreshing} onClick={handleRefresh}>
                <RefreshCw className="w-3.5 h-3.5" />
                {refreshing ? 'REFRESHING...' : 'Refresh'}
              </GlowButton>
            </div>

            {recommendations.length === 0 ? (
              <GlassCard className="p-8">
                <EmptyState
                  icon={<Rocket className="w-12 h-12" />}
                  title="No active missions"
                  description="Initialize the pipeline to generate personalized mission briefings."
                  action={{ label: 'Launch Pipeline', onClick: handleLaunchPipeline }}
                />
              </GlassCard>
            ) : (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                {recommendations.map((rec, i) => (
                  <MissionCard
                    key={rec.recommendation_id}
                    recommendation={rec}
                    rank={i + 1}
                    animationDelay={i * 0.07}
                  />
                ))}
              </div>
            )}
          </div>

          {/* Right: Transmissions */}
          <div>
            <GlassCard className="p-5">
              <TransmissionPanel
                notifications={notifications}
                onMarkRead={handleMarkRead}
                onMarkAllRead={handleMarkAllRead}
              />
            </GlassCard>
          </div>
        </div>

        {/* ── SYSTEM STATUS (collapsible) ── */}
        <div className="mt-8">
          <button
            onClick={() => setStatusOpen(!statusOpen)}
            className="flex items-center gap-2 text-xs font-mono text-observatory-textMuted hover:text-observatory-textSecondary transition-colors mb-3"
          >
            {statusOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
            SYSTEM STATUS
          </button>
          {statusOpen && pipelineStatus && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
              <SystemStatus pipelineStatus={pipelineStatus} />
            </motion.div>
          )}
        </div>
      </div>
    </PageWrapper>
  )
}
