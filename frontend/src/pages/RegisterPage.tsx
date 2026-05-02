import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Telescope, AlertCircle, Eye, EyeOff, ArrowLeft, ArrowRight } from 'lucide-react'
import { register, login } from '@/api/auth'
import { useAuthStore } from '@/store/authStore'
import type { UserLevel } from '@/types'
import PageWrapper from '@/components/layout/PageWrapper'
import { InterestTagInput } from '@/components/profile'
import { GlowButton } from '@/components/ui'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'

const LEVELS: { value: UserLevel; label: string; subtitle: string }[] = [
  { value: 'bachelor', label: 'BACHELOR', subtitle: 'Undergraduate Explorer' },
  { value: 'master', label: 'MASTER', subtitle: 'Advanced Researcher' },
  { value: 'phd', label: 'PHD', subtitle: 'Elite Investigator' },
  { value: 'professional', label: 'PROFESSIONAL', subtitle: 'Field Operative' },
]

function passwordStrength(pw: string): { score: number; label: string } {
  let score = 0
  if (pw.length >= 8) score++
  if (/[A-Z]/.test(pw)) score++
  if (/[0-9]/.test(pw)) score++
  if (/[^A-Za-z0-9]/.test(pw)) score++
  const labels = ['WEAK', 'FAIR', 'STRONG', 'CLASSIFIED']
  return { score, label: labels[score - 1] ?? 'WEAK' }
}

export default function RegisterPage() {
  const navigate = useNavigate()
  const { login: storeLogin } = useAuthStore()
  const [step, setStep] = useState(1)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [showPw, setShowPw] = useState(false)

  // Form state
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPw, setConfirmPw] = useState('')
  const [level, setLevel] = useState<UserLevel>('master')
  const [interests, setInterests] = useState<string[]>([])
  const [skills, setSkills] = useState<string[]>([])
  const [skillInput, setSkillInput] = useState('')

  const pwStrength = passwordStrength(password)
  const strengthColors = ['bg-red-500', 'bg-orange-500', 'bg-yellow-500', 'bg-emerald-500']

  const validateStep1 = () => {
    if (!name.trim()) return 'Name is required'
    if (!email.includes('@')) return 'Valid email required'
    if (password.length < 8) return 'Password must be at least 8 characters'
    if (password !== confirmPw) return 'Passwords do not match'
    return null
  }

  const addSkill = () => {
    const t = skillInput.trim()
    if (t && !skills.includes(t)) setSkills([...skills, t])
    setSkillInput('')
  }

  const handleSubmit = async () => {
    setError(null)
    setLoading(true)
    try {
      await register({ name, email, password, skills, interests, level })
      const loginData = await login(email, password)
      storeLogin(loginData.access_token, loginData.user)
      toast.success('Agent registered. Welcome to the Observatory!')
      navigate('/dashboard')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed')
      setLoading(false)
    }
  }

  const stepNext = () => {
    if (step === 1) {
      const err = validateStep1()
      if (err) { setError(err); return }
    }
    setError(null)
    setStep((s) => s + 1)
  }

  return (
    <PageWrapper>
      <div className="pt-16 min-h-screen flex items-center justify-center px-4 py-12">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          className="w-full max-w-lg"
        >
          <div
            className="rounded-2xl border border-observatory-border p-8"
            style={{ background: 'rgba(15,23,42,0.9)', backdropFilter: 'blur(16px)' }}
          >
            {/* Header */}
            <div className="flex flex-col items-center mb-6">
              <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-observatory-primary to-observatory-accent flex items-center justify-center mb-3">
                <Telescope className="w-6 h-6 text-white" />
              </div>
              <p className="font-mono text-xs text-observatory-accent tracking-widest">AGENT REGISTRATION</p>
              <p className="font-mono text-xs text-observatory-textMuted">INTELLIGENT UNIVERSITY OBSERVATORY</p>
            </div>

            {/* Step progress */}
            <div className="flex items-center gap-2 mb-8">
              {[1, 2, 3].map((s) => (
                <div key={s} className="flex items-center gap-2 flex-1">
                  <div className={clsx(
                    'w-7 h-7 rounded-full flex items-center justify-center text-xs font-mono font-bold border transition-all',
                    step >= s
                      ? 'bg-gradient-to-br from-observatory-primary to-observatory-accent border-observatory-accent text-white'
                      : 'border-observatory-border text-observatory-textMuted'
                  )}>
                    {s}
                  </div>
                  {s < 3 && (
                    <div className={clsx('flex-1 h-px', step > s ? 'bg-observatory-accent' : 'bg-observatory-border')} />
                  )}
                </div>
              ))}
            </div>

            <AnimatePresence mode="wait">
              {/* ── STEP 1: Identity ── */}
              {step === 1 && (
                <motion.div key="step1" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="font-mono text-4xl font-bold text-observatory-accent/30">01</span>
                    <div>
                      <p className="font-mono text-xs text-observatory-textMuted">RECRUIT IDENTIFICATION</p>
                      <h2 className="font-display font-semibold text-observatory-textPrimary">Identity Verification</h2>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <input type="text" placeholder="Full name" value={name} onChange={(e) => setName(e.target.value)}
                      className="w-full bg-observatory-surface border border-observatory-border rounded-lg px-4 py-2.5 text-sm text-observatory-textPrimary placeholder:text-observatory-textMuted focus:outline-none focus:border-observatory-primary transition-all" />
                    <input type="email" placeholder="Email address" value={email} onChange={(e) => setEmail(e.target.value)}
                      className="w-full bg-observatory-surface border border-observatory-border rounded-lg px-4 py-2.5 text-sm text-observatory-textPrimary placeholder:text-observatory-textMuted focus:outline-none focus:border-observatory-primary transition-all" />
                    <div className="relative">
                      <input type={showPw ? 'text' : 'password'} placeholder="Password (min 8 chars)" value={password} onChange={(e) => setPassword(e.target.value)}
                        className="w-full bg-observatory-surface border border-observatory-border rounded-lg px-4 pr-10 py-2.5 text-sm text-observatory-textPrimary placeholder:text-observatory-textMuted focus:outline-none focus:border-observatory-primary transition-all" />
                      <button type="button" onClick={() => setShowPw(!showPw)} className="absolute right-3 top-1/2 -translate-y-1/2 text-observatory-textMuted">
                        {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    {password && (
                      <div className="space-y-1">
                        <div className="flex gap-1">
                          {[0, 1, 2, 3].map((i) => (
                            <div key={i} className={clsx('h-1 flex-1 rounded-full transition-colors', i < pwStrength.score ? strengthColors[pwStrength.score - 1] : 'bg-observatory-surfaceLight')} />
                          ))}
                        </div>
                        <p className="text-xs font-mono text-observatory-textMuted">{pwStrength.label}</p>
                      </div>
                    )}
                    <input type="password" placeholder="Confirm password" value={confirmPw} onChange={(e) => setConfirmPw(e.target.value)}
                      className="w-full bg-observatory-surface border border-observatory-border rounded-lg px-4 py-2.5 text-sm text-observatory-textPrimary placeholder:text-observatory-textMuted focus:outline-none focus:border-observatory-primary transition-all" />
                  </div>
                </motion.div>
              )}

              {/* ── STEP 2: Mission Profile ── */}
              {step === 2 && (
                <motion.div key="step2" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="font-mono text-4xl font-bold text-observatory-accent/30">02</span>
                    <div>
                      <p className="font-mono text-xs text-observatory-textMuted">MISSION PROFILE</p>
                      <h2 className="font-display font-semibold text-observatory-textPrimary">Mission Specialization</h2>
                    </div>
                  </div>
                  <div className="space-y-4">
                    <div>
                      <p className="text-xs font-mono text-observatory-textMuted mb-2 tracking-wider">ACADEMIC LEVEL</p>
                      <div className="grid grid-cols-2 gap-2">
                        {LEVELS.map(({ value, label, subtitle }) => (
                          <button key={value} onClick={() => setLevel(value)}
                            className={clsx(
                              'p-3 rounded-xl border text-left transition-all',
                              level === value
                                ? 'border-observatory-accent bg-observatory-accent/10 shadow-[0_0_12px_rgba(124,58,237,0.3)]'
                                : 'border-observatory-border hover:border-observatory-primary'
                            )}
                          >
                            <p className="font-mono text-xs font-bold text-observatory-textPrimary">{label}</p>
                            <p className="text-xs text-observatory-textMuted">{subtitle}</p>
                          </button>
                        ))}
                      </div>
                    </div>
                    <div>
                      <p className="text-xs font-mono text-observatory-textMuted mb-2 tracking-wider">AREAS OF INTEREST</p>
                      <InterestTagInput value={interests} onChange={setInterests} placeholder="e.g. NLP, Computer Vision, MLOps..." />
                    </div>
                  </div>
                </motion.div>
              )}

              {/* ── STEP 3: Skills ── */}
              {step === 3 && (
                <motion.div key="step3" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -20 }}>
                  <div className="flex items-center gap-2 mb-4">
                    <span className="font-mono text-4xl font-bold text-observatory-accent/30">03</span>
                    <div>
                      <p className="font-mono text-xs text-observatory-textMuted">CAPABILITY ASSESSMENT</p>
                      <h2 className="font-display font-semibold text-observatory-textPrimary">Skills Declaration</h2>
                    </div>
                  </div>
                  <div className="space-y-3">
                    <div className="flex gap-2">
                      <input
                        type="text"
                        placeholder="Add a skill (e.g. Python, PyTorch...)"
                        value={skillInput}
                        onChange={(e) => setSkillInput(e.target.value)}
                        onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addSkill() } }}
                        className="flex-1 bg-observatory-surface border border-observatory-border rounded-lg px-4 py-2.5 text-sm text-observatory-textPrimary placeholder:text-observatory-textMuted focus:outline-none focus:border-observatory-accent transition-all"
                      />
                      <GlowButton variant="accent" onClick={addSkill}>Add</GlowButton>
                    </div>
                    <div className="flex flex-wrap gap-2 min-h-[80px] p-3 rounded-xl border border-observatory-border bg-observatory-surface/50">
                      {skills.length === 0 && (
                        <p className="text-xs text-observatory-textMuted italic self-center w-full text-center">No skills added yet</p>
                      )}
                      <AnimatePresence>
                        {skills.map((skill) => (
                          <motion.span key={skill} initial={{ opacity: 0, scale: 0.5 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0, scale: 0.5 }}
                            className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium bg-gradient-to-r from-observatory-primary to-observatory-accent text-white"
                          >
                            {skill}
                            <button onClick={() => setSkills(skills.filter(s => s !== skill))} className="opacity-70 hover:opacity-100">×</button>
                          </motion.span>
                        ))}
                      </AnimatePresence>
                    </div>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Error */}
            {error && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="mt-4 flex items-center gap-2 p-3 rounded-lg bg-red-900/20 border border-red-800 text-red-300 text-sm"
              >
                <AlertCircle className="w-4 h-4 flex-shrink-0" /> {error}
              </motion.div>
            )}

            {/* Nav buttons */}
            <div className="flex gap-3 mt-6">
              {step > 1 && (
                <GlowButton variant="ghost" onClick={() => { setStep(s => s - 1); setError(null) }}>
                  <ArrowLeft className="w-4 h-4" /> Back
                </GlowButton>
              )}
              {step < 3 ? (
                <GlowButton variant="primary" className="flex-1" onClick={stepNext}>
                  Continue <ArrowRight className="w-4 h-4" />
                </GlowButton>
              ) : (
                <GlowButton variant="primary" className="flex-1" loading={loading} onClick={handleSubmit}>
                  Complete Registration
                </GlowButton>
              )}
            </div>

            <p className="mt-4 text-center text-sm text-observatory-textMuted">
              Already registered?{' '}
              <Link to="/login" className="text-observatory-accent hover:text-observatory-accentLight transition-colors">Sign in</Link>
            </p>
          </div>
        </motion.div>
      </div>
    </PageWrapper>
  )
}
