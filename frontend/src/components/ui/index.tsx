import { useEffect, useRef } from 'react'
import { useMotionValue, useTransform, animate } from 'framer-motion'
import { clsx } from 'clsx'

// ─── GlassCard ───────────────────────────────────────────────────────────────
interface GlassCardProps {
  children: React.ReactNode
  className?: string
  hover?: boolean
}
export function GlassCard({ children, className = '', hover = false }: GlassCardProps) {
  return (
    <div
      className={clsx(
        'rounded-xl border border-observatory-border',
        hover && 'hover:border-observatory-primary hover:shadow-[0_0_20px_rgba(30,64,175,0.3)] transition-all duration-300 cursor-pointer',
        className
      )}
      style={{ background: 'rgba(15,23,42,0.8)', backdropFilter: 'blur(12px)' }}
    >
      {children}
    </div>
  )
}

// ─── GlowButton ──────────────────────────────────────────────────────────────
interface GlowButtonProps {
  variant?: 'primary' | 'accent' | 'ghost' | 'danger'
  size?: 'sm' | 'md' | 'lg'
  loading?: boolean
  disabled?: boolean
  children: React.ReactNode
  onClick?: () => void
  type?: 'button' | 'submit' | 'reset'
  className?: string
}
export function GlowButton({
  variant = 'primary',
  size = 'md',
  loading = false,
  disabled = false,
  children,
  onClick,
  type = 'button',
  className = '',
}: GlowButtonProps) {
  const base = 'inline-flex items-center justify-center gap-2 font-medium rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed'
  const sizes = { sm: 'px-3 py-1.5 text-sm', md: 'px-4 py-2.5 text-sm', lg: 'px-6 py-3 text-base' }
  const variants = {
    primary: 'bg-gradient-to-r from-observatory-primary to-observatory-accent text-white hover:opacity-90 hover:shadow-[0_0_20px_rgba(124,58,237,0.4)]',
    accent: 'bg-observatory-accent text-white hover:bg-observatory-accentLight hover:shadow-[0_0_16px_rgba(124,58,237,0.5)]',
    ghost: 'border border-observatory-border text-observatory-textSecondary hover:border-observatory-primary hover:text-observatory-textPrimary hover:shadow-[0_0_12px_rgba(30,64,175,0.3)]',
    danger: 'border border-red-800 text-red-400 hover:bg-red-900/20 hover:border-red-600',
  }
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled || loading}
      className={clsx(base, sizes[size], variants[variant], className)}
    >
      {loading ? (
        <>
          <span className="w-4 h-4 border-2 border-current border-t-transparent rounded-full animate-spin" />
          <span>Loading...</span>
        </>
      ) : children}
    </button>
  )
}

// ─── LoadingSpinner ───────────────────────────────────────────────────────────
interface SpinnerProps { size?: 'sm' | 'md' | 'lg'; label?: string }
export function LoadingSpinner({ size = 'md', label }: SpinnerProps) {
  const sizes = { sm: 'w-5 h-5', md: 'w-8 h-8', lg: 'w-12 h-12' }
  return (
    <div className="flex flex-col items-center justify-center gap-3">
      <div className={clsx('border-2 border-observatory-border border-t-observatory-accent rounded-full animate-spin', sizes[size])}
        style={{ boxShadow: '0 0 12px rgba(124,58,237,0.4)' }} />
      {label && <p className="text-sm text-observatory-textMuted font-mono">{label}</p>}
    </div>
  )
}

// ─── EmptyState ───────────────────────────────────────────────────────────────
interface EmptyStateProps {
  icon: React.ReactNode
  title: string
  description: string
  action?: { label: string; onClick: () => void }
}
export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center py-16 px-6 text-center">
      <div className="mb-4 text-observatory-textMuted opacity-60">{icon}</div>
      <h3 className="font-display font-semibold text-observatory-textPrimary mb-2">{title}</h3>
      <p className="text-sm text-observatory-textMuted max-w-xs mb-6">{description}</p>
      {action && (
        <GlowButton variant="ghost" onClick={action.onClick}>{action.label}</GlowButton>
      )}
    </div>
  )
}

// ─── PageHeader ───────────────────────────────────────────────────────────────
interface PageHeaderProps { title: string; subtitle?: string; action?: React.ReactNode }
export function PageHeader({ title, subtitle, action }: PageHeaderProps) {
  return (
    <div className="flex items-start justify-between mb-6">
      <div>
        <h1 className="font-display font-bold text-3xl bg-gradient-to-r from-observatory-textPrimary to-observatory-textSecondary bg-clip-text text-transparent">
          {title}
        </h1>
        {subtitle && <p className="mt-1 text-sm text-observatory-textMuted">{subtitle}</p>}
      </div>
      {action && <div className="ml-4 flex-shrink-0">{action}</div>}
    </div>
  )
}

// ─── CountUpNumber ────────────────────────────────────────────────────────────
interface CountUpProps { value: number; duration?: number; suffix?: string; className?: string }
export function CountUpNumber({ value, duration = 1.5, suffix = '', className = '' }: CountUpProps) {
  const count = useMotionValue(0)
  const rounded = useTransform(count, (v) => Math.round(v))
  const displayRef = useRef<HTMLSpanElement>(null)

  useEffect(() => {
    const controls = animate(count, value, { duration })
    const unsubscribe = rounded.on('change', (v) => {
      if (displayRef.current) displayRef.current.textContent = `${v}${suffix}`
    })
    return () => { controls.stop(); unsubscribe() }
  }, [value])

  return <span ref={displayRef} className={className}>0{suffix}</span>
}

// ─── SkeletonCard ─────────────────────────────────────────────────────────────
export function SkeletonCard() {
  return (
    <div className="rounded-xl border border-observatory-border p-5 space-y-3 animate-pulse"
      style={{ background: 'rgba(15,23,42,0.8)' }}>
      <div className="flex gap-2">
        <div className="h-5 w-20 bg-observatory-surfaceLight rounded-full" />
        <div className="h-5 w-16 bg-observatory-surfaceLight rounded-full ml-auto" />
      </div>
      <div className="h-5 w-3/4 bg-observatory-surfaceLight rounded" />
      <div className="h-4 w-1/2 bg-observatory-surfaceLight rounded" />
      <div className="flex gap-2">
        <div className="h-6 w-14 bg-observatory-surfaceLight rounded-full" />
        <div className="h-6 w-14 bg-observatory-surfaceLight rounded-full" />
        <div className="h-6 w-14 bg-observatory-surfaceLight rounded-full" />
      </div>
      <div className="h-9 w-full bg-observatory-surfaceLight rounded-lg" />
    </div>
  )
}
