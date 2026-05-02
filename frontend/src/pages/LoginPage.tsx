import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Telescope, Mail, Lock, Eye, EyeOff, AlertCircle } from 'lucide-react'
import { login } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'
import PageWrapper from '@/components/layout/PageWrapper'
import { GlowButton } from '@/components/ui'
import toast from 'react-hot-toast'

export default function LoginPage() {
  const navigate = useNavigate()
  const { login: storeLogin } = useAuthStore()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPw, setShowPw] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setLoading(true)
    try {
      const data = await login(email, password)
      storeLogin(data.access_token, data.user)
      toast.success(`Welcome back, ${data.user.name}!`)
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <PageWrapper>
      <div className="pt-16 min-h-screen flex items-center justify-center px-4">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5 }}
          className="w-full max-w-md"
        >
          <div
            className="rounded-2xl border border-observatory-border p-8"
            style={{ background: 'rgba(15,23,42,0.9)', backdropFilter: 'blur(16px)' }}
          >
            {/* Logo */}
            <div className="flex flex-col items-center mb-8">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-observatory-primary to-observatory-accent flex items-center justify-center mb-3">
                <Telescope className="w-6 h-6 text-white" />
              </div>
              <h1 className="font-display font-bold text-2xl text-observatory-textPrimary">Welcome Back</h1>
              <p className="text-sm text-observatory-textMuted mt-1">Sign in to your mission control</p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Email */}
              <div>
                <label className="block text-xs font-mono text-observatory-textMuted mb-1.5 tracking-wider">
                  EMAIL ADDRESS
                </label>
                <div className="relative">
                  <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-observatory-textMuted" />
                  <input
                    type="email"
                    required
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="agent@university.edu"
                    className="w-full bg-observatory-surface border border-observatory-border rounded-lg pl-10 pr-4 py-2.5 text-sm text-observatory-textPrimary placeholder:text-observatory-textMuted focus:outline-none focus:border-observatory-primary focus:shadow-[0_0_10px_rgba(30,64,175,0.2)] transition-all"
                  />
                </div>
              </div>

              {/* Password */}
              <div>
                <label className="block text-xs font-mono text-observatory-textMuted mb-1.5 tracking-wider">
                  PASSWORD
                </label>
                <div className="relative">
                  <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-observatory-textMuted" />
                  <input
                    type={showPw ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="••••••••"
                    className="w-full bg-observatory-surface border border-observatory-border rounded-lg pl-10 pr-10 py-2.5 text-sm text-observatory-textPrimary placeholder:text-observatory-textMuted focus:outline-none focus:border-observatory-primary focus:shadow-[0_0_10px_rgba(30,64,175,0.2)] transition-all"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPw(!showPw)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-observatory-textMuted hover:text-observatory-textSecondary transition-colors"
                  >
                    {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
              </div>

              {/* Error */}
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center gap-2 p-3 rounded-lg bg-red-900/20 border border-red-800 text-red-300 text-sm"
                >
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <span>{error}</span>
                </motion.div>
              )}

              <GlowButton type="submit" variant="primary" size="lg" loading={loading} className="w-full">
                Sign In →
              </GlowButton>
            </form>

            <p className="mt-6 text-center text-sm text-observatory-textMuted">
              New to the Observatory?{' '}
              <Link to="/register" className="text-observatory-accent hover:text-observatory-accentLight transition-colors">
                Join the mission
              </Link>
            </p>
          </div>
        </motion.div>
      </div>
    </PageWrapper>
  )
}
