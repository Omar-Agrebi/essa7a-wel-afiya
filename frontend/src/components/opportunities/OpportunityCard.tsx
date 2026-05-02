import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { MapPin, ChevronDown, ArrowRight, Zap, GraduationCap, Clock, Target, CheckCircle, ExternalLink } from 'lucide-react'
import { clsx } from 'clsx'
import type { Opportunity } from '@/types'
import { getTypeColor, getCategoryColor, getMatchReasonIcon } from '@/utils/formatting'
import DeadlineBadge from '@/components/deadline/DeadlineBadge'

interface OpportunityCardProps {
  opportunity: Opportunity
  showScore?: boolean
  score?: number
  matchReasons?: string[]
  animationDelay?: number
}

const REASON_ICONS: Record<string, React.ComponentType<{ className?: string }>> = {
  Zap, GraduationCap, Clock, Target, CheckCircle,
}

export default function OpportunityCard({
  opportunity,
  showScore = false,
  score,
  matchReasons = [],
  animationDelay = 0,
}: OpportunityCardProps) {
  const navigate = useNavigate()
  const [reasonsOpen, setReasonsOpen] = useState(false)

  const typeColors = getTypeColor(opportunity.type)
  const catColor = getCategoryColor(opportunity.category)
  const MAX_SKILLS = 4
  const displaySkills = opportunity.skills_required.slice(0, MAX_SKILLS)
  const extraSkills = opportunity.skills_required.length - MAX_SKILLS

  const scorePercent = score !== undefined ? Math.round(score * 100) : 0
  const scoreColor =
    scorePercent >= 70 ? 'from-emerald-500 to-emerald-400' :
    scorePercent >= 40 ? 'from-yellow-500 to-yellow-400' :
    'from-red-500 to-red-400'

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: animationDelay, duration: 0.4 }}
      className="group rounded-xl border border-observatory-border p-5 flex flex-col gap-3 hover:border-observatory-primary hover:shadow-[0_0_20px_rgba(30,64,175,0.3)] transition-all duration-300"
      style={{ background: 'rgba(15,23,42,0.85)' }}
    >
      {/* Top row: type + category badges */}
      <div className="flex items-center justify-between gap-2 flex-wrap">
        <span className={clsx('px-2.5 py-0.5 rounded-full text-xs font-medium border', typeColors.text, typeColors.bg, typeColors.border)}>
          {opportunity.type}
        </span>
        <span className={clsx('text-xs font-mono', catColor)}>
          {opportunity.category}
        </span>
      </div>

      {/* Title */}
      <h3 className="font-display font-semibold text-observatory-textPrimary leading-snug line-clamp-2">
        {opportunity.title}
      </h3>

      {/* Location + Deadline */}
      <div className="flex flex-col gap-1.5">
        {opportunity.location && (
          <div className="flex items-center gap-1.5 text-xs text-observatory-textMuted">
            <MapPin className="w-3 h-3 flex-shrink-0" />
            <span className="truncate">{opportunity.location}</span>
          </div>
        )}
        <DeadlineBadge deadline={opportunity.deadline} showCountdown />
      </div>

      {/* Skills */}
      {displaySkills.length > 0 && (
        <div className="flex flex-wrap gap-1.5">
          {displaySkills.map((skill) => (
            <span
              key={skill}
              className="px-2 py-0.5 rounded-full text-xs bg-observatory-surfaceLight text-observatory-textSecondary border border-observatory-border"
            >
              {skill}
            </span>
          ))}
          {extraSkills > 0 && (
            <span className="px-2 py-0.5 rounded-full text-xs bg-observatory-accent/20 text-observatory-accentLight border border-observatory-accent/30">
              +{extraSkills} more
            </span>
          )}
        </div>
      )}

      {/* Match score */}
      {showScore && score !== undefined && (
        <div className="space-y-2">
          <div className="flex items-center justify-between text-xs">
            <span className="text-observatory-textMuted font-mono">MATCH SCORE</span>
            <span className="font-mono font-bold text-observatory-textPrimary">{scorePercent}%</span>
          </div>
          <div className="h-1.5 bg-observatory-surfaceLight rounded-full overflow-hidden">
            <motion.div
              className={clsx('h-full rounded-full bg-gradient-to-r', scoreColor)}
              initial={{ width: 0 }}
              animate={{ width: `${scorePercent}%` }}
              transition={{ duration: 1.2, ease: 'easeOut', delay: animationDelay + 0.3 }}
            />
          </div>

          {/* Match reasons toggle */}
          {matchReasons.length > 0 && (
            <div>
              <button
                onClick={() => setReasonsOpen(!reasonsOpen)}
                className="flex items-center gap-1 text-xs text-observatory-textMuted hover:text-observatory-textSecondary transition-colors"
              >
                <ChevronDown className={clsx('w-3 h-3 transition-transform', reasonsOpen && 'rotate-180')} />
                {reasonsOpen ? 'Hide' : 'Why this match?'}
              </button>
              <AnimatePresence>
                {reasonsOpen && (
                  <motion.ul
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-2 space-y-1 overflow-hidden"
                  >
                    {matchReasons.map((reason, i) => {
                      const iconName = getMatchReasonIcon(reason)
                      const Icon = REASON_ICONS[iconName] ?? CheckCircle
                      return (
                        <li key={i} className="flex items-start gap-1.5 text-xs text-observatory-textSecondary">
                          <Icon className="w-3 h-3 mt-0.5 text-observatory-accent flex-shrink-0" />
                          <span>{reason}</span>
                        </li>
                      )
                    })}
                  </motion.ul>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between pt-1 mt-auto">
        <div className="min-w-0">
          <p className="text-xs font-mono text-observatory-textMuted truncate">{opportunity.source}</p>
          {opportunity.cluster_label && (
            <p className="text-xs italic text-observatory-textMuted">~ {opportunity.cluster_label}</p>
          )}
        </div>
        <div className="flex items-center gap-1.5 ml-2 flex-shrink-0">
          <a
            href={opportunity.url}
            target="_blank"
            rel="noopener noreferrer"
            onClick={(e) => e.stopPropagation()}
            className="p-1.5 rounded-lg text-observatory-textMuted hover:text-observatory-textSecondary hover:bg-observatory-surfaceLight transition-colors"
          >
            <ExternalLink className="w-3.5 h-3.5" />
          </a>
          <button
            onClick={() => navigate(`/opportunities/${opportunity.id}`)}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium border border-observatory-border rounded-lg text-observatory-textSecondary hover:border-observatory-primary hover:text-observatory-textPrimary hover:shadow-[0_0_10px_rgba(30,64,175,0.3)] transition-all"
          >
            Explore <ArrowRight className="w-3 h-3" />
          </button>
        </div>
      </div>
    </motion.div>
  )
}
