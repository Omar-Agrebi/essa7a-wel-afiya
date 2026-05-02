import { useEffect, useState, useCallback } from 'react'
import { Telescope } from 'lucide-react'
import type { Opportunity, OpportunityFilters } from '@/types'
import { getOpportunities } from '@/api/opportunities'
import PageWrapper from '@/components/layout/PageWrapper'
import OpportunityCard from '@/components/opportunities/OpportunityCard'
import OpportunityFiltersBar from '@/components/opportunities/OpportunityFilters'
import { SkeletonCard, EmptyState, PageHeader, GlowButton } from '@/components/ui'

const PAGE_SIZE = 12

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([])
  const [filters, setFilters] = useState<OpportunityFilters>({})
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [page, setPage] = useState(0)
  const [total, setTotal] = useState(0)

  const fetchOpportunities = useCallback(async (f: OpportunityFilters, p: number) => {
    setLoading(true)
    setError(null)
    try {
      const data = await getOpportunities(f, p * PAGE_SIZE, PAGE_SIZE)
      setOpportunities(data)
      if (p === 0) {
        // fetch a larger batch just to know total (backend has no count endpoint)
        const allData = await getOpportunities(f, 0, 500)
        setTotal(allData.length)
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load opportunities')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    setPage(0)
    fetchOpportunities(filters, 0)
  }, [filters])

  useEffect(() => {
    if (page > 0) fetchOpportunities(filters, page)
  }, [page])

  const totalPages = Math.ceil(total / PAGE_SIZE)
  const start = page * PAGE_SIZE + 1
  const end = Math.min((page + 1) * PAGE_SIZE, total)

  return (
    <PageWrapper>
      <div className="pt-16">
        <OpportunityFiltersBar filters={filters} onChange={setFilters} isLoading={loading} />

        <div className="max-w-7xl mx-auto px-4 py-8">
          <PageHeader
            title="Opportunities"
            subtitle={!loading && total > 0 ? `Showing ${start}–${end} of ${total} results` : undefined}
          />

          {error && (
            <div className="mb-6 p-4 rounded-xl border border-red-800 bg-red-900/20 text-red-300 text-sm">
              {error}
              <button
                onClick={() => fetchOpportunities(filters, page)}
                className="ml-3 underline hover:no-underline"
              >
                Retry
              </button>
            </div>
          )}

          {loading ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: PAGE_SIZE }).map((_, i) => <SkeletonCard key={i} />)}
            </div>
          ) : opportunities.length === 0 ? (
            <EmptyState
              icon={<Telescope className="w-14 h-14" />}
              title="No opportunities found"
              description="Try clearing your filters or broadening your search."
              action={{ label: 'Clear Filters', onClick: () => setFilters({}) }}
            />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {opportunities.map((opp, i) => (
                <OpportunityCard key={opp.id} opportunity={opp} animationDelay={i * 0.04} />
              ))}
            </div>
          )}

          {/* Pagination */}
          {totalPages > 1 && !loading && (
            <div className="mt-10 flex items-center justify-center gap-2">
              <GlowButton variant="ghost" size="sm" disabled={page === 0} onClick={() => setPage(p => p - 1)}>
                ← Prev
              </GlowButton>
              {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                const pageNum = totalPages <= 7 ? i : Math.max(0, Math.min(page - 3, totalPages - 7)) + i
                return (
                  <button
                    key={pageNum}
                    onClick={() => setPage(pageNum)}
                    className={`w-9 h-9 rounded-lg text-sm font-mono transition-all ${
                      pageNum === page
                        ? 'bg-observatory-primary text-white'
                        : 'text-observatory-textMuted hover:text-observatory-textSecondary hover:bg-observatory-surfaceLight'
                    }`}
                  >
                    {pageNum + 1}
                  </button>
                )
              })}
              <GlowButton variant="ghost" size="sm" disabled={page >= totalPages - 1} onClick={() => setPage(p => p + 1)}>
                Next →
              </GlowButton>
            </div>
          )}
        </div>
      </div>
    </PageWrapper>
  )
}
