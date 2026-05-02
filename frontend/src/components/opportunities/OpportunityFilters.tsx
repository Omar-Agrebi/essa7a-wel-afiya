import { useState } from 'react'
import { Search, SlidersHorizontal, X } from 'lucide-react'
import { clsx } from 'clsx'
import type { OpportunityFilters, OpportunityType, OpportunityCategory } from '@/types'
import { useDebounce } from '@/hooks/useDebounce'
import { useEffect } from 'react'

interface OpportunityFiltersProps {
  filters: OpportunityFilters
  onChange: (f: OpportunityFilters) => void
  isLoading?: boolean
}

const TYPES: OpportunityType[] = ['internship', 'scholarship', 'project', 'course', 'postdoc']
const CATEGORIES: OpportunityCategory[] = ['AI', 'Data Science', 'Cybersecurity', 'Software Engineering', 'Other']

export default function OpportunityFiltersBar({ filters, onChange, isLoading }: OpportunityFiltersProps) {
  const [keywordInput, setKeywordInput] = useState(filters.keyword ?? '')
  const [showAdvanced, setShowAdvanced] = useState(false)
  const debouncedKeyword = useDebounce(keywordInput, 300)

  useEffect(() => {
    onChange({ ...filters, keyword: debouncedKeyword || undefined })
  }, [debouncedKeyword])

  const hasActiveFilters =
    filters.type || filters.category || filters.keyword || filters.expiring_in_days !== undefined

  const clearAll = () => {
    setKeywordInput('')
    onChange({})
  }

  const selectStyle = 'w-full bg-observatory-surface border border-observatory-border rounded-lg px-3 py-2 text-sm text-observatory-textSecondary focus:outline-none focus:border-observatory-primary transition-colors appearance-none cursor-pointer'

  return (
    <div
      className="sticky top-16 z-40 border-b border-observatory-border px-4 py-3"
      style={{ background: 'rgba(10,15,30,0.9)', backdropFilter: 'blur(12px)' }}
    >
      <div className="max-w-7xl mx-auto flex flex-wrap gap-3 items-center">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className={clsx('absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 transition-colors',
            isLoading ? 'text-observatory-accent animate-pulse' : 'text-observatory-textMuted')} />
          <input
            type="text"
            placeholder="Search opportunities..."
            value={keywordInput}
            onChange={(e) => setKeywordInput(e.target.value)}
            className="w-full bg-observatory-surface border border-observatory-border rounded-lg pl-9 pr-3 py-2 text-sm text-observatory-textPrimary placeholder:text-observatory-textMuted focus:outline-none focus:border-observatory-primary focus:shadow-[0_0_10px_rgba(30,64,175,0.2)] transition-all"
          />
        </div>

        {/* Type filter */}
        <select
          value={filters.type ?? ''}
          onChange={(e) => onChange({ ...filters, type: (e.target.value as OpportunityType) || undefined })}
          className={selectStyle}
          style={{ minWidth: 140 }}
        >
          <option value="">All Types</option>
          {TYPES.map((t) => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
        </select>

        {/* Category filter */}
        <select
          value={filters.category ?? ''}
          onChange={(e) => onChange({ ...filters, category: (e.target.value as OpportunityCategory) || undefined })}
          className={selectStyle}
          style={{ minWidth: 160 }}
        >
          <option value="">All Categories</option>
          {CATEGORIES.map((c) => <option key={c} value={c}>{c}</option>)}
        </select>

        {/* Expiring soon toggle */}
        <button
          onClick={() => onChange({ ...filters, expiring_in_days: filters.expiring_in_days !== undefined ? undefined : 7 })}
          className={clsx(
            'flex items-center gap-2 px-3 py-2 text-sm rounded-lg border transition-all whitespace-nowrap',
            filters.expiring_in_days !== undefined
              ? 'bg-orange-900/30 border-orange-600 text-orange-300 shadow-[0_0_8px_rgba(249,115,22,0.3)]'
              : 'border-observatory-border text-observatory-textMuted hover:border-observatory-primary hover:text-observatory-textSecondary'
          )}
        >
          <span className={clsx('w-2 h-2 rounded-full', filters.expiring_in_days !== undefined ? 'bg-orange-400' : 'bg-observatory-textMuted')} />
          Expiring Soon
        </button>

        {/* Advanced toggle */}
        <button
          onClick={() => setShowAdvanced(!showAdvanced)}
          className="flex items-center gap-1.5 px-3 py-2 text-sm border border-observatory-border rounded-lg text-observatory-textMuted hover:text-observatory-textSecondary hover:border-observatory-primary transition-colors"
        >
          <SlidersHorizontal className="w-3.5 h-3.5" /> Advanced
        </button>

        {/* Active filter count + clear */}
        {hasActiveFilters && (
          <button
            onClick={clearAll}
            className="flex items-center gap-1.5 px-3 py-2 text-sm text-red-400 border border-red-800/50 rounded-lg hover:bg-red-900/20 transition-colors"
          >
            <X className="w-3.5 h-3.5" /> Clear
          </button>
        )}
      </div>

      {/* Advanced panel */}
      {showAdvanced && (
        <div className="max-w-7xl mx-auto mt-3 flex gap-3 items-center">
          <label className="text-xs text-observatory-textMuted font-mono">CLUSTER ID</label>
          <input
            type="number"
            placeholder="e.g. 2"
            value={filters.cluster_id ?? ''}
            onChange={(e) => onChange({ ...filters, cluster_id: e.target.value ? Number(e.target.value) : undefined })}
            className="w-32 bg-observatory-surface border border-observatory-border rounded-lg px-3 py-1.5 text-sm text-observatory-textPrimary focus:outline-none focus:border-observatory-primary transition-colors"
          />
        </div>
      )}
    </div>
  )
}
