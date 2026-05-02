import StarField from './StarField'

interface PageWrapperProps {
  children: React.ReactNode
  className?: string
}

export default function PageWrapper({ children, className = '' }: PageWrapperProps) {
  return (
    <div className="relative min-h-screen bg-observatory-bg text-observatory-textPrimary font-body">
      <StarField />
      <div className={`relative z-10 ${className}`}>{children}</div>
    </div>
  )
}
