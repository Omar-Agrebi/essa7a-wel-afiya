import { useEffect, useState, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, useInView } from 'framer-motion'
import { Telescope, ArrowRight, GraduationCap, Search, Target, Zap } from 'lucide-react'
import { getOpportunities } from '@/api/opportunities'
import type { Opportunity, OpportunityType } from '@/types'
import { useAuthStore } from '@/store/authStore'
import PageWrapper from '@/components/layout/PageWrapper'
import OpportunityCard from '@/components/opportunities/OpportunityCard'
import { GlassCard, CountUpNumber, SkeletonCard, GlowButton } from '@/components/ui'

const TYPE_COUNTS: { type: OpportunityType; label: string; icon: string }[] = [
  { type: 'internship', label: 'Internships', icon: '💼' },
  { type: 'scholarship', label: 'Scholarships', icon: '🎓' },
  { type: 'project', label: 'Research Projects', icon: '🔬' },
  { type: 'postdoc', label: 'Postdocs', icon: '🧪' },
]

export default function HomePage() {
  const navigate = useNavigate()
  const { isAuthenticated } = useAuthStore()
  const [recent, setRecent] = useState<Opportunity[]>([])
  const [counts, setCounts] = useState<Record<string, number>>({})
  const [total, setTotal] = useState(0)
  const [loading, setLoading] = useState(true)
  const statsRef = useRef<HTMLDivElement>(null)
  const statsInView = useInView(statsRef, { once: true })

  useEffect(() => {
    const load = async () => {
      try {
        const [all, ...typeCounts] = await Promise.all([
          getOpportunities({}, 0, 6),
          ...TYPE_COUNTS.map(({ type }) => getOpportunities({ type }, 0, 100)),
        ])
        setRecent(all)
        const countMap: Record<string, number> = {}
        TYPE_COUNTS.forEach(({ type }, i) => { countMap[type] = typeCounts[i].length })
        setCounts(countMap)
        // rough total
        const allFull = await getOpportunities({}, 0, 200)
        setTotal(allFull.length)
      } catch {
        // silently handle
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return (
    <PageWrapper>
      <div className="pt-16">
        {/* ── HERO ──────────────────────────────────────────────── */}
        <section className="relative flex flex-col items-center justify-center text-center px-4 py-28 sm:py-36 overflow-hidden">
          {/* dome SVG */}
          <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-full max-w-2xl opacity-10 pointer-events-none">
            <svg viewBox="0 0 800 300" fill="none" xmlns="http://www.w3.org/2000/svg">
              <motion.path
                d="M0 300 Q400 0 800 300"
                stroke="url(#domeGrad)" strokeWidth="2" fill="none"
                initial={{ pathLength: 0 }} animate={{ pathLength: 1 }}
                transition={{ duration: 2, ease: 'easeOut' }}
              />
              <defs>
                <linearGradient id="domeGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                  <stop offset="0%" stopColor="#1e40af" />
                  <stop offset="100%" stopColor="#7c3aed" />
                </linearGradient>
              </defs>
            </svg>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7 }}
            className="max-w-3xl"
          >
            <p className="font-mono text-xs tracking-[0.25em] text-observatory-accent mb-4 uppercase">
              Intelligent University Observatory
            </p>
            <h1 className="font-display font-bold text-5xl sm:text-6xl lg:text-7xl leading-tight mb-4">
              Discover Your Next{' '}
              <span className="bg-gradient-to-r from-observatory-primaryLight via-observatory-accentLight to-observatory-starGold bg-clip-text text-transparent">
                Opportunity
              </span>
            </h1>
            <p className="text-lg text-observatory-textSecondary mb-10 max-w-2xl mx-auto leading-relaxed">
              AI-powered matching for internships, scholarships, research projects, and more — personalized to your skills and academic journey.
            </p>
            <div className="flex flex-wrap items-center justify-center gap-4">
              <Link
                to="/opportunities"
                className="flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-observatory-primary to-observatory-accent text-white font-semibold hover:opacity-90 hover:shadow-[0_0_24px_rgba(124,58,237,0.5)] transition-all"
              >
                Browse Opportunities <ArrowRight className="w-5 h-5" />
              </Link>
              <GlowButton
                variant="ghost"
                size="lg"
                onClick={() => navigate(isAuthenticated ? '/dashboard' : '/register')}
              >
                <Telescope className="w-5 h-5" />
                {isAuthenticated ? 'Mission Control' : 'Get Matched'}
              </GlowButton>
            </div>
          </motion.div>
        </section>

        {/* ── STATS ─────────────────────────────────────────────── */}
        <section ref={statsRef} className="px-4 py-16 max-w-7xl mx-auto">
          <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
            <GlassCard className="col-span-2 lg:col-span-1 p-5 text-center border-observatory-primary/30">
              <p className="font-mono text-xs text-observatory-textMuted mb-1">TOTAL</p>
              <div className="font-display font-bold text-4xl bg-gradient-to-r from-observatory-primaryLight to-observatory-accentLight bg-clip-text text-transparent">
                {statsInView ? <CountUpNumber value={total} /> : '0'}
              </div>
              <p className="text-xs text-observatory-textSecondary mt-1">Opportunities</p>
            </GlassCard>
            {TYPE_COUNTS.map(({ type, label, icon }) => (
              <GlassCard key={type} className="p-5 text-center">
                <p className="text-2xl mb-1">{icon}</p>
                <div className="font-display font-bold text-3xl text-observatory-textPrimary">
                  {statsInView ? <CountUpNumber value={counts[type] ?? 0} /> : '0'}
                </div>
                <p className="text-xs text-observatory-textSecondary mt-1">{label}</p>
              </GlassCard>
            ))}
          </div>
        </section>

        {/* ── RECENT ────────────────────────────────────────────── */}
        <section className="px-4 pb-20 max-w-7xl mx-auto">
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-observatory-starGold" />
              <h2 className="font-display font-bold text-2xl text-observatory-textPrimary">Recently Added</h2>
            </div>
            <Link
              to="/opportunities"
              className="text-sm text-observatory-accent hover:text-observatory-accentLight transition-colors flex items-center gap-1"
            >
              Explore All <ArrowRight className="w-4 h-4" />
            </Link>
          </div>

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {recent.map((opp, i) => (
                <OpportunityCard key={opp.id} opportunity={opp} animationDelay={i * 0.07} />
              ))}
            </div>
          )}
        </section>

        {/* ── HOW IT WORKS ──────────────────────────────────────── */}
        <section className="px-4 pb-24 max-w-5xl mx-auto">
          <h2 className="font-display font-bold text-2xl text-center text-observatory-textPrimary mb-12">
            How the Observatory Works
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 relative">
            {/* Connecting dashed line */}
            <div className="hidden md:block absolute top-1/2 left-[16.5%] right-[16.5%] h-px border-t border-dashed border-observatory-border" />
            {[
              { icon: <GraduationCap className="w-7 h-7" />, num: '01', title: 'Build Your Profile', desc: 'Add your skills, interests, and academic level to calibrate the system.' },
              { icon: <Search className="w-7 h-7" />, num: '02', title: 'Agents Discover', desc: 'AI agents scrape and classify hundreds of opportunities daily, automatically.' },
              { icon: <Target className="w-7 h-7" />, num: '03', title: 'You Get Matched', desc: 'Receive ranked recommendations with transparent match reasons.' },
            ].map(({ icon, num, title, desc }, i) => (
              <motion.div
                key={num}
                initial={{ opacity: 0, y: 24 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.15, duration: 0.5 }}
              >
                <GlassCard className="p-6 text-center relative z-10">
                  <div className="absolute -top-4 left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-gradient-to-br from-observatory-primary to-observatory-accent flex items-center justify-center text-xs font-mono font-bold text-white">
                    {num}
                  </div>
                  <div className="mt-4 mb-4 flex justify-center text-observatory-accent">{icon}</div>
                  <h3 className="font-display font-semibold text-observatory-textPrimary mb-2">{title}</h3>
                  <p className="text-sm text-observatory-textMuted leading-relaxed">{desc}</p>
                </GlassCard>
              </motion.div>
            ))}
          </div>
        </section>

        {/* ── FOOTER ────────────────────────────────────────────── */}
        <footer className="border-t border-observatory-border px-4 py-8 text-center">
          <div className="flex items-center justify-center gap-2 mb-2">
            <Telescope className="w-4 h-4 text-observatory-accent" />
            <span className="font-display font-bold text-observatory-textSecondary">Observatory</span>
          </div>
          <p className="text-xs font-mono text-observatory-textMuted">Powered by Multi-Agent AI · {new Date().getFullYear()}</p>
        </footer>
      </div>
    </PageWrapper>
  )
}
