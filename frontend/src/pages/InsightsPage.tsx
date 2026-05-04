import { useEffect, useState, useRef, useCallback } from 'react'
import { motion, useInView, AnimatePresence } from 'framer-motion'
import { Link, useNavigate } from 'react-router-dom'
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, ResponsiveContainer,
  ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip,
  Cell, ReferenceLine, CartesianGrid,
} from 'recharts'
import {
  Brain, Hexagon, Target, Zap, ArrowRight, Lock,
  GitBranch, CheckCircle2, AlertCircle, Circle,
  ChevronRight, Activity, Layers, TrendingUp,
  Clock, GraduationCap, Cpu, RefreshCw,
} from 'lucide-react'
import { clsx } from 'clsx'
import { useAuthStore } from '@/store/authStore'
import { getPublicInsights, getPersonalInsights } from '@/api/insights'
import { getPipelineStatus } from '@/api/pipeline'
import type { PublicInsights, PersonalInsights } from '@/api/insights'
import type { PipelineStatusResponse } from '@/types'
import PageWrapper from '@/components/layout/PageWrapper'
import { GlassCard, GlowButton, LoadingSpinner } from '@/components/ui'
import { getTypeColor } from '@/utils/formatting'

// ── Colour maps ───────────────────────────────────────────────────────────────
const CLUSTER_COLORS = ['#7c3aed', '#0ea5e9', '#ef4444', '#10b981', '#f59e0b']
const TYPE_COLORS: Record<string, string> = {
  internship: '#3b82f6',
  scholarship: '#10b981',
  project: '#8b5cf6',
  course:  '#f59e0b',
  postdoc: '#f97316',
}
const CLUSTER_SHORT: Record<string, string> = {
  'machine learning phd research':    'ML / AI',
  'data science statistics analysis': 'Data Science',
  'security network cryptography':    'Cybersecurity',
  'software engineering api backend': 'Engineering',
  'scholarship funding stipend':      'Funding',
}
const STATUS_CFG = {
  matched:    { dot: 'bg-emerald-500', text: 'text-emerald-300', border: 'border-emerald-500/50', tile: 'bg-emerald-900/20', label: 'You have it' },
  gap:        { dot: 'bg-amber-400',   text: 'text-amber-300',   border: 'border-amber-500/50',   tile: 'bg-amber-900/15',  label: 'Gap in your cluster' },
  irrelevant: { dot: 'bg-slate-600',   text: 'text-slate-500',   border: 'border-slate-700/40',   tile: 'bg-slate-800/20',  label: 'Outside your cluster' },
}

// ── Shared section reveal wrapper ─────────────────────────────────────────────
function Reveal({ children, delay = 0, className = '' }: { children: React.ReactNode; delay?: number; className?: string }) {
  const ref = useRef<HTMLDivElement>(null)
  const inView = useInView(ref, { once: true, margin: '-50px' })
  return (
    <motion.div
      ref={ref}
      initial={{ opacity: 0, y: 28 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.55, ease: 'easeOut', delay }}
      className={className}
    >
      {children}
    </motion.div>
  )
}

function SectionHeader({
  icon, tag, title, sub,
}: { icon: React.ReactNode; tag: string; title: string; sub?: string }) {
  return (
    <div className="mb-6">
      <div className="flex items-center gap-2 mb-1.5">
        <span className="text-observatory-accent">{icon}</span>
        <span className="font-mono text-xs tracking-[0.2em] text-observatory-textMuted uppercase">{tag}</span>
      </div>
      <h2 className="font-display font-bold text-2xl sm:text-3xl text-observatory-textPrimary leading-tight">{title}</h2>
      {sub && <p className="text-sm text-observatory-textSecondary mt-1.5 max-w-xl leading-relaxed">{sub}</p>}
    </div>
  )
}

// ════════════════════════════════════════════════════════════════════════════════
// SECTION 1 — Skill Genome
// ════════════════════════════════════════════════════════════════════════════════
function SkillGenome({ personal }: { personal: PersonalInsights }) {
  const [filter, setFilter] = useState<'all' | 'matched' | 'gap' | 'irrelevant'>('all')

  const counts = {
    matched:    personal.skill_genome.filter(s => s.status === 'matched').length,
    gap:        personal.skill_genome.filter(s => s.status === 'gap').length,
    irrelevant: personal.skill_genome.filter(s => s.status === 'irrelevant').length,
  }
  const visible = personal.skill_genome.filter(s => filter === 'all' || s.status === filter)

  return (
    <Reveal>
      <SectionHeader
        icon={<Hexagon className="w-5 h-5" />}
        tag="01 — Skill Genome"
        title="Your Skill DNA"
        sub="Every skill required across all 29 opportunities, colour-coded by whether you bring it."
      />

      {/* Coverage KPI strip */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
        <GlassCard className="p-5 text-center border-observatory-accent/30">
          <p className="font-mono text-[10px] text-observatory-textMuted tracking-widest mb-1">TOP CLUSTER COVERAGE</p>
          <p className="font-display font-black text-5xl bg-gradient-to-br from-observatory-primaryLight to-observatory-accentLight bg-clip-text text-transparent">
            {personal.top_cluster.coverage_pct}%
          </p>
          <p className="text-xs text-observatory-textMuted mt-1.5 leading-snug">
            {personal.top_cluster.matched}/{personal.top_cluster.total} skills matched in<br />
            <em className="not-italic text-observatory-accentLight">"{personal.top_cluster.label}"</em>
          </p>
        </GlassCard>
        <GlassCard className="p-5 text-center border-emerald-800/40">
          <p className="font-mono text-[10px] text-observatory-textMuted tracking-widest mb-1">CONFIRMED SKILLS</p>
          <p className="font-display font-black text-5xl text-emerald-400">{counts.matched}</p>
          <p className="text-xs text-observatory-textMuted mt-1.5">already in your arsenal</p>
        </GlassCard>
        <GlassCard className="p-5 text-center border-amber-800/40">
          <p className="font-mono text-[10px] text-observatory-textMuted tracking-widest mb-1">CLUSTER GAPS</p>
          <p className="font-display font-black text-5xl text-amber-400">{counts.gap}</p>
          <p className="text-xs text-observatory-textMuted mt-1.5">skills your top cluster demands</p>
        </GlassCard>
      </div>

      {/* Filter row */}
      <div className="flex flex-wrap gap-2 mb-4">
        {([
          { key: 'all',       label: `All  (${personal.skill_genome.length})` },
          { key: 'matched',   label: `✓ Have it  (${counts.matched})` },
          { key: 'gap',       label: `⚡ Gaps  (${counts.gap})` },
          { key: 'irrelevant',label: `○ Other  (${counts.irrelevant})` },
        ] as const).map(({ key, label }) => (
          <button
            key={key}
            onClick={() => setFilter(key)}
            className={clsx(
              'px-3 py-1.5 rounded-lg text-xs font-mono font-medium border transition-all',
              filter === key
                ? 'bg-observatory-accent/20 border-observatory-accent text-observatory-accentLight'
                : 'border-observatory-border text-observatory-textMuted hover:border-observatory-primary'
            )}
          >
            {label}
          </button>
        ))}
      </div>

      {/* Hexagon tile grid */}
      <GlassCard className="p-5 sm:p-6">
        <div className="flex flex-wrap gap-2">
          <AnimatePresence mode="popLayout">
            {visible.map((item, i) => {
              const cfg = STATUS_CFG[item.status]
              const big = item.frequency > 10
              return (
                <motion.div
                  key={item.skill}
                  layout
                  initial={{ opacity: 0, scale: 0.7 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.5 }}
                  transition={{ delay: i * 0.01, duration: 0.22 }}
                  title={`${item.skill} — required in ${item.frequency} opportunit${item.frequency === 1 ? 'y' : 'ies'} · ${cfg.label}`}
                  className={clsx(
                    'inline-flex items-center gap-1.5 rounded-lg border cursor-default select-none',
                    'transition-transform hover:scale-105',
                    cfg.text, cfg.border, cfg.tile,
                    big ? 'px-3 py-2 text-sm font-medium' : 'px-2.5 py-1.5 text-xs'
                  )}
                >
                  {item.status === 'matched'    && <CheckCircle2 className="w-3 h-3 flex-shrink-0" />}
                  {item.status === 'gap'        && <AlertCircle  className="w-3 h-3 flex-shrink-0" />}
                  {item.status === 'irrelevant' && <Circle       className="w-3 h-3 flex-shrink-0 opacity-40" />}
                  <span className="font-mono">{item.skill}</span>
                  {item.frequency > 5 && (
                    <span className="opacity-40 text-[10px]">×{item.frequency}</span>
                  )}
                </motion.div>
              )
            })}
          </AnimatePresence>
        </div>

        {/* Legend */}
        <div className="flex flex-wrap gap-5 mt-5 pt-4 border-t border-observatory-border">
          {Object.entries(STATUS_CFG).map(([k, v]) => (
            <span key={k} className="flex items-center gap-1.5 text-xs text-observatory-textMuted">
              <span className={clsx('w-2.5 h-2.5 rounded-full', v.dot)} />
              {v.label}
            </span>
          ))}
          <span className="text-xs text-observatory-textMuted">· ×N = appears in N opportunities</span>
        </div>
      </GlassCard>
    </Reveal>
  )
}

// ════════════════════════════════════════════════════════════════════════════════
// SECTION 2 — Skill Gap Radar
// ════════════════════════════════════════════════════════════════════════════════
function RadarTip({ payload }: { payload?: { name: string; value: number }[] }) {
  if (!payload?.length) return null
  return (
    <div className="rounded-lg border border-observatory-border px-3 py-2 text-xs"
         style={{ background: 'rgba(15,23,42,0.97)' }}>
      {payload.map(p => (
        <div key={p.name} className={p.name === 'user_coverage' ? 'text-observatory-accentLight' : 'text-observatory-textMuted'}>
          {p.name === 'user_coverage' ? 'Your coverage' : 'Ideal'}: <strong>{p.value}%</strong>
        </div>
      ))}
    </div>
  )
}

function SkillGapRadar({ personal }: { personal: PersonalInsights }) {
  const radarData = personal.radar_data.map(d => ({
    ...d,
    cluster: CLUSTER_SHORT[d.cluster] ?? d.cluster,
  }))

  return (
    <Reveal>
      <SectionHeader
        icon={<Target className="w-5 h-5" />}
        tag="02 — Skill Gap Radar"
        title="Domain Coverage"
        sub="How your skills spread across every thematic cluster. The ghost polygon is 100% coverage."
      />
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-5">
        {/* Radar chart */}
        <GlassCard className="lg:col-span-3 p-5 sm:p-6">
          <ResponsiveContainer width="100%" height={310}>
            <RadarChart data={radarData} margin={{ top: 8, right: 28, bottom: 8, left: 28 }}>
              <PolarGrid stroke="#1e3a5f" />
              <PolarAngleAxis
                dataKey="cluster"
                tick={{ fill: '#94a3b8', fontSize: 11, fontFamily: 'JetBrains Mono' }}
              />
              <Radar name="ideal" dataKey="ideal" stroke="#334155" fill="#334155"
                     fillOpacity={0.06} strokeDasharray="4 3" strokeWidth={1} />
              <Radar name="user_coverage" dataKey="user_coverage"
                     stroke="#7c3aed" fill="#7c3aed" fillOpacity={0.3} strokeWidth={2}
                     dot={{ fill: '#9461f5', r: 4, strokeWidth: 0 }} />
              <Tooltip content={<RadarTip />} />
            </RadarChart>
          </ResponsiveContainer>
          <div className="flex justify-center gap-5 mt-1">
            <span className="flex items-center gap-1.5 text-xs text-observatory-textMuted">
              <span className="w-4 h-0.5 bg-observatory-accent rounded inline-block" /> Your profile
            </span>
            <span className="flex items-center gap-1.5 text-xs text-observatory-textMuted">
              <span className="w-4 h-0.5 bg-slate-600 rounded inline-block" style={{ borderStyle: 'dashed' }} /> Ideal (100%)
            </span>
          </div>
        </GlassCard>

        {/* Right column */}
        <div className="lg:col-span-2 flex flex-col gap-4">
          {/* Skills that unlock the most */}
          <GlassCard className="p-5 border-observatory-accent/20 flex-1">
            <p className="font-mono text-[10px] tracking-widest text-observatory-accent mb-4">
              SKILLS THAT UNLOCK THE MOST
            </p>
            <div className="space-y-3">
              {personal.skill_gaps.slice(0, 5).map((gap, i) => (
                <motion.div
                  key={gap.skill}
                  initial={{ opacity: 0, x: 14 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.1 + i * 0.07 }}
                  className="flex items-center justify-between gap-3"
                >
                  <div className="flex items-center gap-2.5 min-w-0">
                    <span className="font-mono text-xs text-observatory-textMuted w-5 flex-shrink-0">
                      {String(i + 1).padStart(2, '0')}
                    </span>
                    <span className="text-sm text-observatory-textPrimary font-mono truncate">{gap.skill}</span>
                  </div>
                  <div className="flex items-center gap-1 flex-shrink-0">
                    <span className="text-sm font-mono font-bold text-amber-400">+{gap.unlocks}</span>
                    <span className="text-xs text-observatory-textMuted">opps</span>
                  </div>
                </motion.div>
              ))}
              {personal.skill_gaps.length === 0 && (
                <p className="text-xs text-observatory-textMuted italic">No unmatched skill gaps found — great coverage!</p>
              )}
            </div>
          </GlassCard>

          {/* Per-cluster bar breakdown */}
          <GlassCard className="p-5">
            <p className="font-mono text-[10px] tracking-widest text-observatory-textMuted mb-3">
              COVERAGE PER DOMAIN
            </p>
            <div className="space-y-2.5">
              {personal.radar_data.map((d, i) => (
                <div key={d.cluster_id}>
                  <div className="flex justify-between text-xs mb-1">
                    <span className="text-observatory-textSecondary truncate">
                      {CLUSTER_SHORT[d.cluster] ?? d.cluster}
                    </span>
                    <span className="font-mono font-bold ml-2 flex-shrink-0"
                          style={{ color: CLUSTER_COLORS[i] ?? '#7c3aed' }}>
                      {d.user_coverage}%
                    </span>
                  </div>
                  <div className="h-1.5 bg-observatory-surfaceLight rounded-full overflow-hidden">
                    <motion.div
                      className="h-full rounded-full"
                      style={{ backgroundColor: CLUSTER_COLORS[i] ?? '#7c3aed' }}
                      initial={{ width: 0 }}
                      animate={{ width: `${d.user_coverage}%` }}
                      transition={{ duration: 1.1, ease: 'easeOut', delay: i * 0.1 }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </GlassCard>
        </div>
      </div>
    </Reveal>
  )
}

// ════════════════════════════════════════════════════════════════════════════════
// SECTION 3 — Score Anatomy
// ════════════════════════════════════════════════════════════════════════════════
function Gauge({ value, label, color, icon }: { value: number; label: string; color: string; icon: React.ReactNode }) {
  const pct = Math.round(Math.min(1, Math.max(0, value)) * 100)
  const r = 36
  const circ = 2 * Math.PI * r
  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative w-24 h-24">
        <svg className="w-full h-full -rotate-90" viewBox="0 0 80 80">
          <circle cx="40" cy="40" r={r} fill="none" stroke="#1e293b" strokeWidth="7" />
          <motion.circle
            cx="40" cy="40" r={r} fill="none"
            stroke={color} strokeWidth="7" strokeLinecap="round"
            strokeDasharray={`${circ}`}
            initial={{ strokeDashoffset: circ }}
            animate={{ strokeDashoffset: circ - (pct / 100) * circ }}
            transition={{ duration: 1.2, ease: 'easeOut' }}
            style={{ filter: `drop-shadow(0 0 5px ${color}88)` }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="font-display font-black text-lg" style={{ color }}>{pct}%</span>
        </div>
      </div>
      <div className="text-center">
        <div className="flex justify-center mb-0.5" style={{ color }}>{icon}</div>
        <p className="font-mono text-[10px] text-observatory-textMuted tracking-wider leading-tight">{label}</p>
      </div>
    </div>
  )
}

function ScoreAnatomySection({ personal }: { personal: PersonalInsights }) {
  const [idx, setIdx] = useState(0)
  const rec = personal.score_anatomy[idx]
  if (!rec) return null

  const deadlineColor = rec.deadline_days === null ? '#64748b'
    : rec.deadline_days < 0  ? '#64748b'
    : rec.deadline_days <= 7 ? '#ef4444'
    : rec.deadline_days <= 30 ? '#f59e0b'
    : '#10b981'

  return (
    <Reveal>
      <SectionHeader
        icon={<Cpu className="w-5 h-5" />}
        tag="03 — Score Anatomy"
        title="Why You're Getting These Matches"
        sub="The scoring formula decomposed live. Click any of your top 3 recommendations to inspect it."
      />

      {/* Formula */}
      <GlassCard className="p-4 mb-5 border-observatory-primary/30 overflow-x-auto">
        <p className="font-mono text-xs text-center text-observatory-textMuted whitespace-nowrap">
          <span className="text-observatory-textPrimary font-bold">final_score</span>
          {' = '}
          <span className="text-violet-400 font-bold">0.5</span>
          <span className="text-observatory-textSecondary"> × semantic_similarity </span>
          {' + '}
          <span className="text-cyan-400 font-bold">0.3</span>
          <span className="text-observatory-textSecondary"> × level_alignment </span>
          {' + '}
          <span className="text-emerald-400 font-bold">0.2</span>
          <span className="text-observatory-textSecondary"> × deadline_recency</span>
        </p>
      </GlassCard>

      {/* Rec selector tabs */}
      <div className="flex gap-2 mb-5 flex-wrap">
        {personal.score_anatomy.map((r, i) => (
          <button
            key={r.opportunity_id}
            onClick={() => setIdx(i)}
            className={clsx(
              'flex-1 min-w-[130px] p-3.5 rounded-xl border text-left transition-all',
              i === idx
                ? 'border-observatory-accent bg-observatory-accent/10 shadow-[0_0_14px_rgba(124,58,237,0.2)]'
                : 'border-observatory-border hover:border-observatory-primary'
            )}
          >
            <p className="font-mono text-[10px] text-observatory-textMuted mb-1">RANK #{i + 1}</p>
            <p className="text-sm font-medium text-observatory-textPrimary line-clamp-2 leading-snug">{r.title}</p>
            <p className="font-display font-bold text-xl mt-1" style={{ color: '#9461f5' }}>
              {Math.round(r.total_score * 100)}%
            </p>
          </button>
        ))}
      </div>

      <GlassCard className="p-6">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Gauges */}
          <div>
            <p className="font-mono text-[10px] text-observatory-textMuted tracking-widest mb-5 text-center truncate">
              {rec.title.slice(0, 40)}{rec.title.length > 40 ? '…' : ''}
            </p>
            <div className="flex justify-around gap-2">
              <Gauge value={rec.components.semantic_similarity} label="SEMANTIC MATCH"  color="#7c3aed" icon={<Brain className="w-4 h-4" />} />
              <Gauge value={rec.components.level_alignment}     label="LEVEL ALIGNMENT" color="#0ea5e9" icon={<GraduationCap className="w-4 h-4" />} />
              <Gauge value={rec.components.deadline_recency}    label="DEADLINE RECENCY" color="#10b981" icon={<Clock className="w-4 h-4" />} />
            </div>

            {/* Stacked total bar */}
            <div className="mt-6 pt-4 border-t border-observatory-border">
              <div className="flex justify-between font-mono text-xs mb-1.5">
                <span className="text-observatory-textMuted">WEIGHTED TOTAL</span>
                <span className="text-observatory-textPrimary font-bold">{Math.round(rec.total_score * 100)}%</span>
              </div>
              <div className="h-2.5 bg-observatory-surfaceLight rounded-full overflow-hidden flex gap-px">
                {[
                  { w: 0.5, v: rec.components.semantic_similarity, c: '#7c3aed' },
                  { w: 0.3, v: rec.components.level_alignment,     c: '#0ea5e9' },
                  { w: 0.2, v: rec.components.deadline_recency,    c: '#10b981' },
                ].map(({ w, v, c }, i) => (
                  <motion.div key={i} className="h-full first:rounded-l-full last:rounded-r-full"
                    style={{ backgroundColor: c }}
                    initial={{ width: 0 }}
                    animate={{ width: `${w * v * 100}%` }}
                    transition={{ duration: 1.0, ease: 'easeOut', delay: i * 0.15 }}
                  />
                ))}
              </div>
              <div className="flex justify-between text-[10px] text-observatory-textMuted mt-1 font-mono">
                <span>sim ×0.5</span><span>level ×0.3</span><span>recency ×0.2</span>
              </div>
            </div>
          </div>

          {/* Qualitative details */}
          <div className="space-y-4">
            {/* Level alignment */}
            <div>
              <p className="font-mono text-[10px] text-observatory-textMuted tracking-wider mb-2">ACADEMIC LEVEL ALIGNMENT</p>
              <div className="flex flex-wrap gap-1.5">
                {['bachelor', 'master', 'phd', 'postdoc'].map(lvl => {
                  const elig = (rec.eligibility ?? '').toLowerCase()
                  const isUser   = lvl === personal.user.level
                  const isTarget = elig.includes(lvl) || elig.includes('all') || elig.includes('any')
                  return (
                    <span key={lvl} className={clsx(
                      'px-2.5 py-1 rounded-lg text-xs font-mono border transition-all',
                      isUser && isTarget ? 'border-emerald-500 bg-emerald-900/30 text-emerald-300 font-bold' :
                      isUser            ? 'border-yellow-600 bg-yellow-900/20 text-yellow-300' :
                      isTarget          ? 'border-cyan-700 bg-cyan-900/20 text-cyan-400' :
                                          'border-observatory-border text-observatory-textMuted opacity-40'
                    )}>
                      {isUser && isTarget && '✓ '}{lvl}
                    </span>
                  )
                })}
              </div>
              {rec.eligibility && (
                <p className="text-[11px] text-observatory-textMuted mt-1.5 italic">"{rec.eligibility}"</p>
              )}
            </div>

            {/* Deadline pressure bar */}
            <div>
              <p className="font-mono text-[10px] text-observatory-textMuted tracking-wider mb-2">DEADLINE PRESSURE</p>
              {rec.deadline_days !== null ? (
                <>
                  <div className="h-2 bg-observatory-surfaceLight rounded-full overflow-hidden mb-1.5">
                    <motion.div className="h-full rounded-full" style={{ backgroundColor: deadlineColor }}
                      initial={{ width: 0 }}
                      animate={{ width: `${rec.deadline_days <= 0 ? 5 : Math.min(100, Math.max(5, (1 - Math.min(rec.deadline_days, 365) / 365) * 100))}%` }}
                      transition={{ duration: 1.0, ease: 'easeOut' }}
                    />
                  </div>
                  <p className="font-mono text-xs font-bold" style={{ color: deadlineColor }}>
                    {rec.deadline_days < 0  ? 'Expired'
                     : rec.deadline_days === 0 ? 'Closes TODAY'
                     : `${rec.deadline_days} days remaining`}
                  </p>
                </>
              ) : (
                <p className="text-xs text-observatory-textMuted">No deadline — neutral recency score (0.3)</p>
              )}
            </div>

            {/* Matching skills */}
            {rec.skill_overlap.length > 0 && (
              <div>
                <p className="font-mono text-[10px] text-observatory-textMuted tracking-wider mb-2">MATCHING SKILLS</p>
                <div className="flex flex-wrap gap-1.5">
                  {rec.skill_overlap.map(s => (
                    <span key={s} className="px-2 py-0.5 rounded-full text-xs bg-violet-900/30 text-violet-300 border border-violet-700/50 font-mono">
                      {s}
                    </span>
                  ))}
                </div>
              </div>
            )}

            <Link to={`/opportunities/${rec.opportunity_id}`}
              className="inline-flex items-center gap-1.5 text-xs text-observatory-accent hover:text-observatory-accentLight font-mono transition-colors">
              View full opportunity <ChevronRight className="w-3 h-3" />
            </Link>
          </div>
        </div>
      </GlassCard>
    </Reveal>
  )
}

// ════════════════════════════════════════════════════════════════════════════════
// SECTION 4 — Opportunity Landscape (scatter)
// ════════════════════════════════════════════════════════════════════════════════
function LandscapeTip({ active, payload }: {
  active?: boolean
  payload?: { payload: { id: string; title: string; type: string; score: number; deadline_days: number; skill_match_count: number } }[]
}) {
  const navigate = useNavigate()
  if (!active || !payload?.length) return null
  const d = payload[0].payload
  const tc = getTypeColor(d.type as never)
  return (
    <div className="rounded-xl border border-observatory-border p-3 max-w-[210px]"
         style={{ background: 'rgba(15,23,42,0.97)' }}>
      <p className="text-xs font-medium text-observatory-textPrimary leading-snug mb-2">{d.title}</p>
      <div className="flex flex-wrap gap-1 mb-2">
        <span className={clsx('px-1.5 py-0.5 rounded text-xs border', tc.text, tc.bg, tc.border)}>{d.type}</span>
        <span className="text-xs font-mono text-observatory-textMuted">{Math.round(d.score * 100)}% match</span>
      </div>
      <p className="text-xs text-observatory-textMuted mb-2">
        {d.deadline_days >= 365 ? 'No deadline' : `${d.deadline_days}d left`}
        {' · '}{d.skill_match_count} skill{d.skill_match_count !== 1 ? 's' : ''} match
      </p>
      <button
        onClick={() => navigate(`/opportunities/${d.id}`)}
        className="text-xs text-observatory-accent hover:text-observatory-accentLight font-mono transition-colors">
        View opportunity →
      </button>
    </div>
  )
}

function OpportunityLandscape({ personal }: { personal: PersonalInsights }) {
  const navigate = useNavigate()
  const types = [...new Set(personal.landscape.map(d => d.type))]
  return (
    <Reveal>
      <SectionHeader
        icon={<TrendingUp className="w-5 h-5" />}
        tag="04 — Opportunity Landscape"
        title="Your Match Universe"
        sub="Every recommendation plotted by urgency vs fit. Top-left = act now. Top-right = prepare well."
      />
      <GlassCard className="p-4 sm:p-6">
        <div className="relative">
          {/* Quadrant labels */}
          <div className="absolute top-1 left-14 text-[10px] font-mono text-red-400 opacity-70 pointer-events-none z-10">⚡ ACT NOW</div>
          <div className="absolute top-1 right-4 text-[10px] font-mono text-emerald-400 opacity-70 pointer-events-none z-10">PREPARE →</div>
          <div className="absolute bottom-10 left-14 text-[10px] font-mono text-observatory-textMuted opacity-50 pointer-events-none z-10">LOW MATCH</div>

          <ResponsiveContainer width="100%" height={340}>
            <ScatterChart margin={{ top: 20, right: 24, bottom: 28, left: 20 }}>
              <CartesianGrid stroke="#1e293b" strokeDasharray="4 4" />
              <XAxis type="number" dataKey="deadline_days" domain={[0, 365]} name="Days remaining"
                label={{ value: 'Days until deadline →', position: 'insideBottom', offset: -10, fill: '#475569', fontSize: 11, fontFamily: 'JetBrains Mono' }}
                tick={{ fill: '#475569', fontSize: 10, fontFamily: 'JetBrains Mono' }} />
              <YAxis type="number" dataKey="score" domain={[0, 1]} name="Match score"
                tickFormatter={(v: number) => `${Math.round(v * 100)}%`}
                label={{ value: 'Match ↑', angle: -90, position: 'insideLeft', offset: 14, fill: '#475569', fontSize: 11, fontFamily: 'JetBrains Mono' }}
                tick={{ fill: '#475569', fontSize: 10, fontFamily: 'JetBrains Mono' }} />
              <ZAxis type="number" dataKey="skill_match_count" range={[80, 400]} />
              <ReferenceLine x={30}  stroke="#ef444428" strokeDasharray="5 3" />
              <ReferenceLine y={0.4} stroke="#3b82f628" strokeDasharray="5 3" />
              <Tooltip content={<LandscapeTip />} cursor={{ strokeDasharray: '4 4', stroke: '#475569' }} />
              {types.map(type => (
                <Scatter
                  key={type}
                  data={personal.landscape.filter(d => d.type === type)}
                  cursor="pointer"
                  onClick={(d: { id: string }) => navigate(`/opportunities/${d.id}`)}
                >
                  {personal.landscape.filter(d => d.type === type).map((_, i) => (
                    <Cell key={i} fill={TYPE_COLORS[type] ?? '#94a3b8'} fillOpacity={0.85} />
                  ))}
                </Scatter>
              ))}
            </ScatterChart>
          </ResponsiveContainer>
        </div>
        <div className="flex flex-wrap gap-4 justify-center mt-1 pt-3 border-t border-observatory-border">
          {types.map(t => (
            <span key={t} className="flex items-center gap-1.5 text-xs text-observatory-textMuted">
              <span className="w-3 h-3 rounded-full" style={{ backgroundColor: TYPE_COLORS[t] ?? '#94a3b8' }} />
              {t}
            </span>
          ))}
          <span className="text-xs text-observatory-textMuted">· dot size = matching skill count</span>
        </div>
      </GlassCard>
    </Reveal>
  )
}

// ════════════════════════════════════════════════════════════════════════════════
// SECTION 5 — Pipeline Transparency
// ════════════════════════════════════════════════════════════════════════════════
const STAGES = [
  { key: 'raw_collected',              label: 'Scrape',    icon: <Activity className="w-4 h-4" />,    color: '#3b82f6' },
  { key: 'cleaned',                    label: 'Clean',     icon: <Layers className="w-4 h-4" />,      color: '#8b5cf6' },
  { key: 'classified',                 label: 'Classify',  icon: <Brain className="w-4 h-4" />,       color: '#7c3aed' },
  { key: 'clustered',                  label: 'Cluster',   icon: <GitBranch className="w-4 h-4" />,   color: '#0ea5e9' },
  { key: 'stored',                     label: 'Store',     icon: <Layers className="w-4 h-4" />,      color: '#f59e0b' },
  { key: 'recommendations_generated',  label: 'Recommend', icon: <Target className="w-4 h-4" />,      color: '#10b981' },
  { key: 'notified',                   label: 'Notify',    icon: <Activity className="w-4 h-4" />,    color: '#ec4899' },
]

function PipelineLog({ pipeline }: { pipeline: PipelineStatusResponse }) {
  const isNever = (pipeline as { status?: string }).status === 'never_run'
  if (isNever) {
    return (
      <Reveal>
        <SectionHeader icon={<GitBranch className="w-5 h-5" />} tag="05 — Pipeline Transparency" title="Data Flow" />
        <GlassCard className="p-10 text-center">
          <Activity className="w-10 h-10 text-observatory-textMuted mx-auto mb-3 opacity-30" />
          <p className="text-observatory-textMuted font-mono text-sm">Pipeline has never run yet.</p>
          <Link to="/dashboard" className="mt-3 inline-flex items-center gap-1.5 text-xs text-observatory-accent font-mono hover:text-observatory-accentLight">
            Trigger a run from the Dashboard <ArrowRight className="w-3 h-3" />
          </Link>
        </GlassCard>
      </Reveal>
    )
  }

  const ps = pipeline as Record<string, number | string | unknown[]>
  const maxVal = Math.max(...STAGES.map(s => Number(ps[s.key] ?? 0)), 1)

  return (
    <Reveal>
      <SectionHeader
        icon={<GitBranch className="w-5 h-5" />}
        tag="05 — Pipeline Transparency"
        title="How the Data Flows"
        sub="Items traced from scraping through to your recommendations. Bar height = volume; yield rate = what survived each filter."
      />
      <GlassCard className="p-5 sm:p-6">
        {/* Flow bar chart */}
        <div className="flex items-end justify-between gap-2 sm:gap-3 mb-6 overflow-x-auto pb-1">
          {STAGES.map((stage, i) => {
            const val = Number(ps[stage.key] ?? 0)
            const barH = Math.max(16, Math.round((val / maxVal) * 100))
            const prev = i > 0 ? Number(ps[STAGES[i - 1].key] ?? 0) : val
            const yieldRate = prev > 0 ? val / prev : 1
            const barColor = yieldRate < 0.7 ? '#ef4444' : yieldRate < 0.9 ? '#f59e0b' : stage.color

            return (
              <div key={stage.key} className="flex flex-col items-center gap-2 flex-1 min-w-[70px]">
                {/* Icon node */}
                <div className="w-9 h-9 rounded-xl flex items-center justify-center border"
                     style={{ borderColor: barColor + '55', background: barColor + '18', color: barColor }}>
                  {stage.icon}
                </div>
                {/* Bar */}
                <p className="font-mono text-xs font-bold" style={{ color: barColor }}>{val}</p>
                <div className="w-full max-w-[44px] bg-observatory-surfaceLight rounded-t overflow-hidden"
                     style={{ height: 100 }}>
                  <motion.div className="w-full rounded-t" style={{ backgroundColor: barColor, opacity: 0.85 }}
                    initial={{ height: 0 }} animate={{ height: barH }}
                    transition={{ duration: 0.9, ease: 'easeOut', delay: i * 0.1 }} />
                </div>
                <p className="font-mono text-[10px] text-observatory-textMuted text-center leading-tight">
                  {stage.label}
                </p>
                {i > 0 && (
                  <span className="font-mono text-[10px]"
                        style={{ color: yieldRate < 0.7 ? '#ef4444' : '#6b7280' }}>
                    {Math.round(yieldRate * 100)}% yield
                  </span>
                )}
              </div>
            )
          })}
        </div>

        {/* Stats row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-4 border-t border-observatory-border">
          {[
            { label: 'DURATION',  value: ps.duration_sec != null ? `${Number(ps.duration_sec).toFixed(1)}s` : '—' },
            { label: 'ERRORS',    value: String(Array.isArray(ps.pipeline_errors) ? ps.pipeline_errors.length : 0) },
            { label: 'RUN #',     value: String(ps.run_number ?? 1) },
            { label: 'STATUS',    value: String(ps.status ?? 'ok').toUpperCase() },
          ].map(({ label, value }) => (
            <div key={label} className="text-center">
              <p className="font-mono text-[10px] text-observatory-textMuted tracking-widest">{label}</p>
              <p className="font-mono text-sm font-bold text-observatory-textPrimary mt-0.5">{value}</p>
            </div>
          ))}
        </div>
      </GlassCard>
    </Reveal>
  )
}

// ════════════════════════════════════════════════════════════════════════════════
// AUTH GATE — shown for personal sections when logged out
// ════════════════════════════════════════════════════════════════════════════════
function AuthGate({ title }: { title: string }) {
  return (
    <GlassCard className="p-10 text-center border-observatory-border/50">
      <Lock className="w-10 h-10 text-observatory-textMuted mx-auto mb-3 opacity-30" />
      <p className="font-display font-semibold text-observatory-textPrimary mb-1">{title}</p>
      <p className="text-sm text-observatory-textMuted mb-5">Sign in to unlock your personalized ML intelligence.</p>
      <div className="flex gap-3 justify-center">
        <Link to="/login"><GlowButton variant="ghost" size="sm">Sign In</GlowButton></Link>
        <Link to="/register"><GlowButton variant="primary" size="sm">Create Account</GlowButton></Link>
      </div>
    </GlassCard>
  )
}

// ════════════════════════════════════════════════════════════════════════════════
// PUBLIC STATS HEADER
// ════════════════════════════════════════════════════════════════════════════════
function PublicStats({ pub }: { pub: PublicInsights }) {
  const ref = useRef<HTMLDivElement>(null)
  const inView = useInView(ref, { once: true })
  return (
    <motion.div ref={ref}
      initial={{ opacity: 0, y: 20 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.5 }}
      className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-14"
    >
      {[
        { label: 'Opportunities',  value: pub.total_opportunities,                      grad: 'from-observatory-primaryLight to-observatory-accentLight' },
        { label: 'Unique Skills',  value: pub.total_unique_skills,                      grad: 'from-violet-400 to-purple-400' },
        { label: 'AI Clusters',    value: pub.clusters.length,                          grad: 'from-cyan-400 to-blue-400' },
        { label: 'Closing in 7d',  value: pub.deadline_distribution['0-7d'] ?? 0,       grad: 'from-orange-400 to-red-400' },
      ].map(({ label, value, grad }, i) => (
        <GlassCard key={label} className="p-4 text-center">
          <motion.p
            className={`font-display font-black text-4xl bg-gradient-to-br ${grad} bg-clip-text text-transparent`}
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: i * 0.1 + 0.3 }}
          >
            {value}
          </motion.p>
          <p className="text-[11px] text-observatory-textMuted mt-1 font-mono">{label}</p>
        </GlassCard>
      ))}
    </motion.div>
  )
}

// ════════════════════════════════════════════════════════════════════════════════
// MAIN PAGE
// ════════════════════════════════════════════════════════════════════════════════
export default function InsightsPage() {
  const { isAuthenticated } = useAuthStore()
  const [pub, setPub]           = useState<PublicInsights | null>(null)
  const [personal, setPersonal] = useState<PersonalInsights | null>(null)
  const [pipeline, setPipeline] = useState<PipelineStatusResponse | null>(null)
  const [loading, setLoading]   = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  const load = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true)
    try {
      // Run all independent calls in parallel; isolate failures so one bad call
      // doesn't wipe out the rest (e.g. a 401 on /pipeline/status shouldn't
      // hide the personal insights for a logged-in user).
      const [pubResult, pipelineResult, personalResult] = await Promise.allSettled([
        getPublicInsights(),
        getPipelineStatus(),
        isAuthenticated ? getPersonalInsights() : Promise.resolve(null),
      ])

      if (pubResult.status === 'fulfilled') setPub(pubResult.value)
      else console.error('Public insights failed:', pubResult.reason)

      if (pipelineResult.status === 'fulfilled') setPipeline(pipelineResult.value)
      else console.error('Pipeline status failed:', pipelineResult.reason)

      if (personalResult.status === 'fulfilled' && personalResult.value !== null)
        setPersonal(personalResult.value)
      else if (personalResult.status === 'rejected')
        console.error('Personal insights failed:', personalResult.reason)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [isAuthenticated])

  useEffect(() => { load() }, [load])

  if (loading) {
    return (
      <PageWrapper>
        <div className="pt-32 flex justify-center">
          <LoadingSpinner size="lg" label="CALIBRATING INTELLIGENCE ENGINE..." />
        </div>
      </PageWrapper>
    )
  }

  return (
    <PageWrapper>
      <div className="pt-20 pb-24 max-w-7xl mx-auto px-4">

        {/* ── PAGE HEADER ─────────────────────────────────────────── */}
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-10"
        >
          <p className="font-mono text-xs tracking-[0.2em] text-observatory-accent mb-2">ML INTELLIGENCE</p>
          <div className="flex items-start justify-between gap-4 flex-wrap">
            <div>
              <h1 className="font-display font-black text-4xl sm:text-5xl text-observatory-textPrimary mb-3 leading-tight">
                Your Academic{' '}
                <span className="bg-gradient-to-r from-observatory-primaryLight via-observatory-accentLight to-observatory-starGold bg-clip-text text-transparent">
                  Signal
                </span>
              </h1>
              <p className="text-observatory-textSecondary max-w-2xl leading-relaxed text-sm sm:text-base">
                The full ML pipeline — classifier, clusterer, and recommender — made visible and personal.
                {isAuthenticated
                  ? ' Every chart below is computed from your real profile and the live database.'
                  : ' Sign in to unlock your personal analysis.'}
              </p>
            </div>
            <button
              onClick={() => load(true)}
              disabled={refreshing}
              className="flex items-center gap-2 px-4 py-2 text-sm font-mono border border-observatory-border rounded-xl text-observatory-textMuted hover:border-observatory-primary hover:text-observatory-textPrimary transition-all disabled:opacity-50 flex-shrink-0"
            >
              <RefreshCw className={clsx('w-4 h-4', refreshing && 'animate-spin')} />
              {refreshing ? 'Refreshing…' : 'Refresh'}
            </button>
          </div>
        </motion.div>

        {/* ── PUBLIC STATS ─────────────────────────────────────────── */}
        {pub && <PublicStats pub={pub} />}

        {/* ── SECTION 1: SKILL GENOME ─────────────────────────────── */}
        <div className="mb-16">
          {personal ? (
            <SkillGenome personal={personal} />
          ) : (
            <>
              <SectionHeader icon={<Hexagon className="w-5 h-5" />} tag="01 — Skill Genome" title="Skill DNA" />
              <AuthGate title="Personalized Skill Genome" />
            </>
          )}
        </div>

        {/* ── SECTION 2: RADAR ────────────────────────────────────── */}
        <div className="mb-16">
          {personal ? (
            <SkillGapRadar personal={personal} />
          ) : (
            <>
              <SectionHeader icon={<Target className="w-5 h-5" />} tag="02 — Skill Gap Radar" title="Domain Coverage" />
              <AuthGate title="Domain Coverage Radar" />
            </>
          )}
        </div>

        {/* ── SECTION 3: SCORE ANATOMY ────────────────────────────── */}
        <div className="mb-16">
          {personal && personal.score_anatomy.length > 0 ? (
            <ScoreAnatomySection personal={personal} />
          ) : (
            <>
              <SectionHeader icon={<Cpu className="w-5 h-5" />} tag="03 — Score Anatomy" title="Score Anatomy" />
              {!isAuthenticated
                ? <AuthGate title="Score Anatomy Panel" />
                : (
                  <GlassCard className="p-8 text-center">
                    <p className="text-observatory-textMuted text-sm">
                      No recommendations yet.{' '}
                      <Link to="/dashboard" className="text-observatory-accent hover:underline">
                        Run the pipeline from your Dashboard
                      </Link>{' '}
                      first.
                    </p>
                  </GlassCard>
                )}
            </>
          )}
        </div>

        {/* ── SECTION 4: LANDSCAPE ────────────────────────────────── */}
        <div className="mb-16">
          {personal && personal.landscape.length > 0 ? (
            <OpportunityLandscape personal={personal} />
          ) : (
            <>
              <SectionHeader icon={<TrendingUp className="w-5 h-5" />} tag="04 — Opportunity Landscape" title="Match Universe" />
              {!isAuthenticated
                ? <AuthGate title="Opportunity Landscape" />
                : (
                  <GlassCard className="p-8 text-center">
                    <p className="text-observatory-textMuted text-sm">Landscape requires recommendations. Run the pipeline first.</p>
                  </GlassCard>
                )}
            </>
          )}
        </div>

        {/* ── SECTION 5: PIPELINE ─────────────────────────────────── */}
        <div className="mb-10">
          {pipeline && <PipelineLog pipeline={pipeline} />}
        </div>

        {/* ── BOTTOM CTA ──────────────────────────────────────────── */}
        <Reveal className="pt-6 border-t border-observatory-border">
          <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <p className="font-display font-semibold text-observatory-textPrimary">
                Ready to act on your intelligence?
              </p>
              <p className="text-sm text-observatory-textMuted mt-0.5">
                Browse all {pub?.total_opportunities} opportunities or head to your dashboard.
              </p>
            </div>
            <div className="flex gap-3 flex-shrink-0">
              <Link to="/opportunities">
                <GlowButton variant="ghost">
                  Browse <ArrowRight className="w-4 h-4" />
                </GlowButton>
              </Link>
              {isAuthenticated && (
                <Link to="/dashboard">
                  <GlowButton variant="primary">
                    Dashboard <Zap className="w-4 h-4" />
                  </GlowButton>
                </Link>
              )}
            </div>
          </div>
        </Reveal>

      </div>
    </PageWrapper>
  )
}
