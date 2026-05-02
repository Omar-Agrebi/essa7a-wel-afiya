import { useEffect, useState } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowLeft, MapPin, ExternalLink, Copy, Check, CheckCircle, Circle } from 'lucide-react'
import { getOpportunity } from '@/api/opportunities'
import type { Opportunity } from '@/types'
import { useAuthStore } from '@/store/authStore'
import PageWrapper from '@/components/layout/PageWrapper'
import DeadlineBadge from '@/components/deadline/DeadlineBadge'
import { GlassCard, GlowButton, EmptyState, LoadingSpinner } from '@/components/ui'
import { getTypeColor, getCategoryColor, formatDate } from '@/utils/formatting'
import { Telescope } from 'lucide-react'
import { clsx } from 'clsx'

export default function OpportunityDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const { user } = useAuthStore()
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!id) return
    const load = async () => {
      try {
        const data = await getOpportunity(id)
        setOpportunity(data)
      } catch (e) {
        setError(e instanceof Error ? e.message : 'Not found')
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [id])

  const handleCopy = () => {
    navigator.clipboard.writeText(window.location.href)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  if (loading) {
    return (
      <PageWrapper>
        <div className="pt-32 flex justify-center">
          <LoadingSpinner size="lg" label="LOADING MISSION BRIEF..." />
        </div>
      </PageWrapper>
    )
  }

  if (error || !opportunity) {
    return (
      <PageWrapper>
        <div className="pt-32">
          <EmptyState
            icon={<Telescope className="w-14 h-14" />}
            title="Mission Not Found"
            description="This opportunity may have been removed or the link is invalid."
            action={{ label: '← Back to Opportunities', onClick: () => navigate('/opportunities') }}
          />
        </div>
      </PageWrapper>
    )
  }

  const typeColors = getTypeColor(opportunity.type)
  const catColor = getCategoryColor(opportunity.category)
  const userSkills = user?.skills ?? []

  return (
    <PageWrapper>
      <div className="pt-20 pb-16 max-w-6xl mx-auto px-4">
        {/* Back + stamp row */}
        <div className="flex items-start justify-between mb-6 gap-4">
          <button
            onClick={() => navigate(-1)}
            className="flex items-center gap-2 text-sm text-observatory-textMuted hover:text-observatory-textSecondary transition-colors font-mono"
          >
            <ArrowLeft className="w-4 h-4" /> Mission Select
          </button>
          <div className="flex items-center gap-3">
            <span className="font-mono text-xs text-observatory-textMuted">
              OBS-{opportunity.id.slice(0, 8).toUpperCase()}
            </span>
            <motion.div
              initial={{ opacity: 0, rotate: -10, scale: 1.3 }}
              animate={{ opacity: 1, rotate: -4, scale: 1 }}
              transition={{ delay: 0.3, duration: 0.4 }}
              className="px-3 py-1 border-2 border-red-600 text-red-500 font-mono text-xs font-bold tracking-widest rounded"
            >
              CLASSIFIED
            </motion.div>
          </div>
        </div>

        {/* Title section */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-2 mb-3">
            <span className={clsx('px-3 py-1 rounded-full text-sm font-medium border', typeColors.text, typeColors.bg, typeColors.border)}>
              {opportunity.type}
            </span>
            <span className={clsx('px-3 py-1 rounded-full text-sm font-medium border border-observatory-border bg-observatory-surfaceLight', catColor)}>
              {opportunity.category}
            </span>
          </div>
          <h1 className="font-display font-bold text-3xl sm:text-4xl text-observatory-textPrimary mb-3 leading-tight">
            {opportunity.title}
          </h1>
          <div className="flex flex-wrap gap-4 text-sm text-observatory-textMuted">
            {opportunity.location && (
              <span className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4" /> {opportunity.location}
              </span>
            )}
            <span className="font-mono">{opportunity.source}</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* ── LEFT: Main content ── */}
          <div className="lg:col-span-2 space-y-6">
            {/* Description */}
            {opportunity.description && (
              <GlassCard className="p-6">
                <h2 className="font-mono text-xs font-bold text-observatory-textMuted tracking-wider mb-3">
                  MISSION BRIEF
                </h2>
                <p className="text-observatory-textSecondary leading-relaxed whitespace-pre-line">
                  {opportunity.description}
                </p>
              </GlassCard>
            )}

            {/* Skills */}
            {opportunity.skills_required.length > 0 && (
              <GlassCard className="p-6">
                <h2 className="font-mono text-xs font-bold text-observatory-textMuted tracking-wider mb-4">
                  REQUIRED CAPABILITIES
                </h2>
                <ul className="space-y-2">
                  {opportunity.skills_required.map((skill) => {
                    const hasSkill = userSkills.some(
                      (s) => s.toLowerCase() === skill.toLowerCase()
                    )
                    return (
                      <li key={skill} className="flex items-center justify-between gap-2">
                        <div className="flex items-center gap-2">
                          {hasSkill ? (
                            <CheckCircle className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                          ) : (
                            <Circle className="w-4 h-4 text-observatory-textMuted flex-shrink-0" />
                          )}
                          <span className={clsx('text-sm', hasSkill ? 'text-observatory-textPrimary' : 'text-observatory-textMuted')}>
                            {skill}
                          </span>
                        </div>
                        {hasSkill && (
                          <span className="text-xs font-mono text-emerald-400">CONFIRMED</span>
                        )}
                      </li>
                    )
                  })}
                </ul>
                {!user && (
                  <p className="mt-4 text-xs text-observatory-textMuted italic">
                    <Link to="/login" className="text-observatory-accent hover:underline">Sign in</Link> to see which skills you already have.
                  </p>
                )}
              </GlassCard>
            )}

            {/* Eligibility */}
            {opportunity.eligibility && (
              <GlassCard className="p-6">
                <h2 className="font-mono text-xs font-bold text-observatory-textMuted tracking-wider mb-3">
                  ELIGIBILITY CLEARANCE
                </h2>
                <p className="text-observatory-textSecondary leading-relaxed">{opportunity.eligibility}</p>
              </GlassCard>
            )}

            {/* Cluster */}
            {opportunity.cluster_label && (
              <GlassCard className="p-6">
                <h2 className="font-mono text-xs font-bold text-observatory-textMuted tracking-wider mb-2">
                  CLUSTER ASSIGNMENT
                </h2>
                <p className="text-sm text-observatory-textSecondary">
                  This opportunity belongs to cluster:{' '}
                  <span className="text-observatory-accentLight font-medium">{opportunity.cluster_label}</span>
                </p>
              </GlassCard>
            )}
          </div>

          {/* ── RIGHT: Sidebar ── */}
          <div className="space-y-4">
            {/* Deadline card */}
            <GlassCard className="p-5 border-observatory-primary/30">
              <h3 className="font-mono text-xs font-bold text-observatory-textMuted tracking-wider mb-3">
                DEADLINE
              </h3>
              <p className="font-display font-bold text-xl text-observatory-textPrimary mb-2">
                {opportunity.deadline ? formatDate(opportunity.deadline) : 'No deadline set'}
              </p>
              <DeadlineBadge deadline={opportunity.deadline} showCountdown size="md" />
            </GlassCard>

            {/* Source / access */}
            <GlassCard className="p-5">
              <h3 className="font-mono text-xs font-bold text-observatory-textMuted tracking-wider mb-3">
                SOURCE
              </h3>
              <p className="text-sm text-observatory-textSecondary mb-3 font-mono">{opportunity.source}</p>
              <GlowButton
                variant="primary"
                className="w-full"
                onClick={() => window.open(opportunity.url, '_blank', 'noopener,noreferrer')}
              >
                <ExternalLink className="w-4 h-4" /> Authorize Access
              </GlowButton>
            </GlassCard>

            {/* Share */}
            <GlassCard className="p-5">
              <h3 className="font-mono text-xs font-bold text-observatory-textMuted tracking-wider mb-3">
                SHARE
              </h3>
              <GlowButton variant="ghost" className="w-full" onClick={handleCopy}>
                {copied ? <Check className="w-4 h-4 text-emerald-400" /> : <Copy className="w-4 h-4" />}
                {copied ? 'Copied!' : 'Copy Link'}
              </GlowButton>
            </GlassCard>

            {/* Back */}
            <GlowButton
              variant="ghost"
              className="w-full"
              onClick={() => navigate('/opportunities')}
            >
              <ArrowLeft className="w-4 h-4" /> All Opportunities
            </GlowButton>
          </div>
        </div>
      </div>
    </PageWrapper>
  )
}
