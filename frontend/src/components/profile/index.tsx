import { useState, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { X, Plus } from 'lucide-react'

// ─── SkillGalaxy ─────────────────────────────────────────────────────────────
interface SkillGalaxyProps {
  skills: string[]
  onRemove: (skill: string) => void
  onAdd: (skill: string) => void
}

function getSkillColor(skill: string): string {
  const lower = skill.toLowerCase()
  if (['pytorch', 'tensorflow', 'nlp', 'bert', 'gpt', 'transformers', 'keras', 'ml'].some(k => lower.includes(k)))
    return 'from-blue-600 to-purple-600'
  if (['pandas', 'numpy', 'sql', 'r', 'tableau', 'spark', 'hadoop', 'data'].some(k => lower.includes(k)))
    return 'from-emerald-600 to-cyan-600'
  if (['docker', 'git', 'kubernetes', 'ci', 'devops', 'linux', 'bash'].some(k => lower.includes(k)))
    return 'from-orange-600 to-yellow-600'
  return 'from-observatory-primary to-observatory-accent'
}

export function SkillGalaxy({ skills, onRemove, onAdd }: SkillGalaxyProps) {
  const [input, setInput] = useState('')

  const handleAdd = () => {
    const trimmed = input.trim()
    if (trimmed && !skills.includes(trimmed)) {
      onAdd(trimmed)
      setInput('')
    }
  }

  return (
    <div className="space-y-4">
      {/* Skills as orbital pills */}
      <div className="flex flex-wrap gap-2 min-h-[80px] p-4 rounded-xl border border-observatory-border bg-observatory-surface/50">
        <AnimatePresence>
          {skills.length === 0 && (
            <p className="text-sm text-observatory-textMuted italic self-center w-full text-center">
              No skills registered. Add your first capability below.
            </p>
          )}
          {skills.map((skill) => (
            <motion.div
              key={skill}
              initial={{ opacity: 0, scale: 0.5 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 0.5, x: 20 }}
              className="relative"
            >
              <div
                className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-white bg-gradient-to-r ${getSkillColor(skill)} cursor-pointer transition-shadow hover:shadow-[0_0_12px_rgba(124,58,237,0.5)]`}
              >
                <span>{skill}</span>
                <button
                  onClick={() => onRemove(skill)}
                  className="ml-0.5 opacity-70 hover:opacity-100 transition-opacity"
                >
                  <X className="w-3 h-3" />
                </button>
              </div>
            </motion.div>
          ))}
        </AnimatePresence>
      </div>

      {/* Add input */}
      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); handleAdd() } }}
          placeholder="Add a capability (e.g. PyTorch, Docker...)"
          className="flex-1 bg-observatory-surface border border-observatory-border rounded-lg px-3 py-2 text-sm text-observatory-textPrimary placeholder:text-observatory-textMuted focus:outline-none focus:border-observatory-accent transition-colors"
        />
        <button
          onClick={handleAdd}
          className="px-3 py-2 bg-observatory-accent/20 border border-observatory-accent/40 rounded-lg text-observatory-accentLight hover:bg-observatory-accent/30 transition-colors"
        >
          <Plus className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}

// ─── InterestTagInput ─────────────────────────────────────────────────────────
interface InterestTagInputProps {
  value: string[]
  onChange: (tags: string[]) => void
  placeholder?: string
}

export function InterestTagInput({ value, onChange, placeholder = 'Add an interest...' }: InterestTagInputProps) {
  const [input, setInput] = useState('')
  const inputRef = useRef<HTMLInputElement>(null)

  const add = (raw: string) => {
    const trimmed = raw.trim().replace(/,$/, '')
    if (trimmed && !value.includes(trimmed)) {
      onChange([...value, trimmed])
    }
    setInput('')
  }

  const remove = (tag: string) => onChange(value.filter((t) => t !== tag))

  return (
    <div
      className="min-h-[80px] p-3 rounded-xl border border-observatory-border bg-observatory-surface/50 flex flex-wrap gap-2 cursor-text"
      onClick={() => inputRef.current?.focus()}
    >
      <AnimatePresence>
        {value.map((tag) => (
          <motion.span
            key={tag}
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            className="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-observatory-accent/20 text-observatory-accentLight border border-observatory-accent/30"
          >
            {tag}
            <button onClick={() => remove(tag)} className="hover:text-white transition-colors">
              <X className="w-3 h-3" />
            </button>
          </motion.span>
        ))}
      </AnimatePresence>
      <input
        ref={inputRef}
        type="text"
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={(e) => {
          if (e.key === 'Enter' || e.key === ',') { e.preventDefault(); add(input) }
          if (e.key === 'Backspace' && !input && value.length > 0) remove(value[value.length - 1])
        }}
        placeholder={value.length === 0 ? placeholder : ''}
        className="flex-1 min-w-[140px] bg-transparent text-sm text-observatory-textPrimary placeholder:text-observatory-textMuted outline-none"
      />
    </div>
  )
}
