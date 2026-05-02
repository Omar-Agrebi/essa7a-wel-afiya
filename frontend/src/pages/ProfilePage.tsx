import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ShieldOff, Save } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { updateSkills, updateInterests } from '@/api/auth'
import PageWrapper from '@/components/layout/PageWrapper'
import { SkillGalaxy, InterestTagInput } from '@/components/profile'
import { GlassCard, GlowButton, PageHeader } from '@/components/ui'
import { getInitials, getLevelLabel } from '@/utils/formatting'
import { formatDate } from '@/utils/formatting'
import toast from 'react-hot-toast'
import { clsx } from 'clsx'

export default function ProfilePage() {
  const { user, logout, updateUser } = useAuthStore()
  const navigate = useNavigate()

  const [skills, setSkills] = useState<string[]>(user?.skills ?? [])
  const [interests, setInterests] = useState<string[]>(user?.interests ?? [])
  const [savingSkills, setSavingSkills] = useState(false)
  const [savingInterests, setSavingInterests] = useState(false)
  const [confirmLogout, setConfirmLogout] = useState(false)

  useEffect(() => {
    if (user) {
      setSkills(user.skills)
      setInterests(user.interests)
    }
  }, [user])

  const skillsChanged = JSON.stringify(skills) !== JSON.stringify(user?.skills ?? [])
  const interestsChanged = JSON.stringify(interests) !== JSON.stringify(user?.interests ?? [])

  const handleSaveSkills = async () => {
    setSavingSkills(true)
    try {
      const updated = await updateSkills(skills)
      updateUser(updated)
      toast.success('Capabilities updated')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed to save skills')
    } finally {
      setSavingSkills(false)
    }
  }

  const handleSaveInterests = async () => {
    setSavingInterests(true)
    try {
      const updated = await updateInterests(interests)
      updateUser(updated)
      toast.success('Interests updated')
    } catch (e) {
      toast.error(e instanceof Error ? e.message : 'Failed to save interests')
    } finally {
      setSavingInterests(false)
    }
  }

  const handleLogout = () => {
    logout()
    navigate('/')
  }

  if (!user) return null

  return (
    <PageWrapper>
      <div className="pt-20 pb-16 max-w-5xl mx-auto px-4">
        <PageHeader title="Agent Dossier" subtitle="Manage your capabilities and mission profile" />

        {/* ── DOSSIER HEADER ── */}
        <GlassCard className="p-6 mb-6">
          <div className="flex flex-col sm:flex-row items-center sm:items-start gap-6">
            {/* Avatar with orbital ring */}
            <div className="relative flex-shrink-0">
              <div className="absolute inset-0 rounded-full border-2 border-observatory-accent/30 animate-spin-slow" style={{ animationDuration: '8s' }} />
              <div className="w-20 h-20 rounded-full bg-gradient-to-br from-observatory-primary to-observatory-accent flex items-center justify-center text-2xl font-display font-bold text-white">
                {getInitials(user.name)}
              </div>
            </div>

            <div className="text-center sm:text-left flex-1">
              <p className="font-mono text-xs text-observatory-accent tracking-widest mb-1">AGENT DOSSIER</p>
              <h2 className="font-display font-bold text-2xl text-observatory-textPrimary">{user.name}</h2>
              <p className="font-mono text-sm text-observatory-textMuted">{user.email}</p>
              <div className="mt-2 flex flex-wrap items-center gap-3 justify-center sm:justify-start">
                <span className="px-3 py-1 rounded-full border border-observatory-accent/40 bg-observatory-accent/10 text-observatory-accentLight text-xs font-mono font-bold">
                  {getLevelLabel(user.level)}
                </span>
                <span className="text-xs font-mono text-observatory-textMuted">
                  SINCE {formatDate(user.created_at)}
                </span>
              </div>
            </div>
          </div>
        </GlassCard>

        {/* ── SKILLS ── */}
        <GlassCard className="p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="font-mono text-xs text-observatory-textMuted tracking-wider">REGISTERED CAPABILITIES</p>
              <h3 className="font-display font-semibold text-observatory-textPrimary">Skills</h3>
            </div>
            <GlowButton
              variant="primary"
              size="sm"
              loading={savingSkills}
              disabled={!skillsChanged}
              onClick={handleSaveSkills}
            >
              <Save className="w-3.5 h-3.5" /> Save
            </GlowButton>
          </div>
          <SkillGalaxy
            skills={skills}
            onRemove={(s) => setSkills(skills.filter((x) => x !== s))}
            onAdd={(s) => setSkills([...skills, s])}
          />
        </GlassCard>

        {/* ── INTERESTS ── */}
        <GlassCard className="p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <p className="font-mono text-xs text-observatory-textMuted tracking-wider">MISSION INTERESTS</p>
              <h3 className="font-display font-semibold text-observatory-textPrimary">Areas of Focus</h3>
            </div>
            <GlowButton
              variant="primary"
              size="sm"
              loading={savingInterests}
              disabled={!interestsChanged}
              onClick={handleSaveInterests}
            >
              <Save className="w-3.5 h-3.5" /> Save
            </GlowButton>
          </div>
          <InterestTagInput
            value={interests}
            onChange={setInterests}
            placeholder="Add interests (e.g. NLP, Computer Vision)..."
          />
        </GlassCard>

        {/* ── SESSION CONTROL ── */}
        <GlassCard className="p-6">
          <p className="font-mono text-xs text-observatory-textMuted tracking-wider mb-3">SESSION CONTROL</p>
          {!confirmLogout ? (
            <GlowButton
              variant="danger"
              onClick={() => setConfirmLogout(true)}
            >
              <ShieldOff className="w-4 h-4" /> Terminate Session
            </GlowButton>
          ) : (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex items-center gap-3">
              <p className="text-sm text-observatory-textSecondary">Confirm session termination?</p>
              <GlowButton variant="danger" size="sm" onClick={handleLogout}>Confirm</GlowButton>
              <GlowButton variant="ghost" size="sm" onClick={() => setConfirmLogout(false)}>Cancel</GlowButton>
            </motion.div>
          )}
        </GlassCard>
      </div>
    </PageWrapper>
  )
}
