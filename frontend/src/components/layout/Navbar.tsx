import { useState, useEffect, useRef } from 'react'
import { Link, useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Telescope, Bell, Menu, X, ChevronDown, LogOut, User } from 'lucide-react'
import { useAuthStore } from '@/store/authStore'
import { useUnreadCount } from '@/hooks/useUnreadCount'
import { getInitials } from '@/utils/formatting'

export default function Navbar() {
  const { isAuthenticated, user, logout } = useAuthStore()
  const { count: unreadCount } = useUnreadCount()
  const [mobileOpen, setMobileOpen] = useState(false)
  const [avatarOpen, setAvatarOpen] = useState(false)
  const [prevCount, setPrevCount] = useState(0)
  const [bellRing, setBellRing] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (unreadCount > prevCount && prevCount > 0) {
      setBellRing(true)
      setTimeout(() => setBellRing(false), 1500)
    }
    setPrevCount(unreadCount)
  }, [unreadCount])

  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setAvatarOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  useEffect(() => setMobileOpen(false), [location.pathname])

  const navLinks = [
    { label: 'Home', to: '/' },
    { label: 'Opportunities', to: '/opportunities' },
    ...(isAuthenticated
      ? [
          { label: 'Dashboard', to: '/dashboard' },
          { label: 'Profile', to: '/profile' },
        ]
      : []),
  ]

  const isActive = (to: string) =>
    to === '/' ? location.pathname === '/' : location.pathname.startsWith(to)

  const handleLogout = () => {
    logout()
    navigate('/')
    setAvatarOpen(false)
  }

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-observatory-border"
      style={{ background: 'rgba(10,15,30,0.88)', backdropFilter: 'blur(16px)' }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 group">
            <Telescope className="w-6 h-6 text-observatory-accent group-hover:text-observatory-accentLight transition-colors" />
            <span className="font-display font-bold text-lg bg-gradient-to-r from-observatory-primaryLight to-observatory-accentLight bg-clip-text text-transparent">
              Observatory
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.to}
                to={link.to}
                className={`relative px-4 py-2 text-sm font-medium rounded-lg transition-colors ${
                  isActive(link.to)
                    ? 'text-observatory-textPrimary'
                    : 'text-observatory-textSecondary hover:text-observatory-textPrimary'
                }`}
              >
                {link.label}
                {isActive(link.to) && (
                  <motion.div
                    layoutId="nav-indicator"
                    className="absolute bottom-0 left-2 right-2 h-0.5 rounded-full bg-gradient-to-r from-observatory-primary to-observatory-accent"
                  />
                )}
              </Link>
            ))}
          </div>

          {/* Right side */}
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <>
                {/* Bell */}
                <button
                  onClick={() => navigate('/dashboard')}
                  className="relative p-2 rounded-lg text-observatory-textSecondary hover:text-observatory-textPrimary transition-colors"
                >
                  <Bell
                    className={`w-5 h-5 ${bellRing ? 'animate-[bellSwing_0.5s_ease-in-out_3]' : ''}`}
                  />
                  {unreadCount > 0 && (
                    <span className="absolute -top-0.5 -right-0.5 min-w-[18px] h-[18px] flex items-center justify-center text-[10px] font-bold bg-red-600 text-white rounded-full animate-pulse-glow">
                      {unreadCount > 9 ? '9+' : unreadCount}
                    </span>
                  )}
                </button>

                {/* Avatar dropdown */}
                <div className="relative" ref={dropdownRef}>
                  <button
                    onClick={() => setAvatarOpen(!avatarOpen)}
                    className="flex items-center gap-2 p-1 rounded-lg hover:bg-observatory-surfaceLight transition-colors"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-observatory-primary to-observatory-accent flex items-center justify-center text-xs font-bold text-white">
                      {user ? getInitials(user.name) : 'U'}
                    </div>
                    <ChevronDown className={`w-4 h-4 text-observatory-textMuted transition-transform ${avatarOpen ? 'rotate-180' : ''}`} />
                  </button>
                  <AnimatePresence>
                    {avatarOpen && (
                      <motion.div
                        initial={{ opacity: 0, y: -8 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -8 }}
                        className="absolute right-0 mt-2 w-48 rounded-xl border border-observatory-border overflow-hidden"
                        style={{ background: 'rgba(15,23,42,0.95)', backdropFilter: 'blur(12px)' }}
                      >
                        <div className="px-4 py-3 border-b border-observatory-border">
                          <p className="text-sm font-medium text-observatory-textPrimary truncate">{user?.name}</p>
                          <p className="text-xs text-observatory-textMuted truncate">{user?.email}</p>
                        </div>
                        <Link
                          to="/profile"
                          onClick={() => setAvatarOpen(false)}
                          className="flex items-center gap-2 px-4 py-2.5 text-sm text-observatory-textSecondary hover:text-observatory-textPrimary hover:bg-observatory-surfaceLight transition-colors"
                        >
                          <User className="w-4 h-4" /> Profile
                        </Link>
                        <button
                          onClick={handleLogout}
                          className="w-full flex items-center gap-2 px-4 py-2.5 text-sm text-red-400 hover:text-red-300 hover:bg-red-900/20 transition-colors"
                        >
                          <LogOut className="w-4 h-4" /> Sign Out
                        </button>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </>
            ) : (
              <div className="flex items-center gap-2">
                <Link
                  to="/login"
                  className="hidden sm:block px-4 py-2 text-sm font-medium text-observatory-textSecondary border border-observatory-border rounded-lg hover:border-observatory-primary hover:text-observatory-textPrimary transition-colors"
                >
                  Sign In
                </Link>
                <Link
                  to="/register"
                  className="px-4 py-2 text-sm font-medium text-white rounded-lg bg-gradient-to-r from-observatory-primary to-observatory-accent hover:opacity-90 transition-opacity"
                >
                  Join
                </Link>
              </div>
            )}

            {/* Mobile hamburger */}
            <button
              onClick={() => setMobileOpen(!mobileOpen)}
              className="md:hidden p-2 rounded-lg text-observatory-textSecondary hover:text-observatory-textPrimary transition-colors"
            >
              {mobileOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="md:hidden border-t border-observatory-border"
            style={{ background: 'rgba(10,15,30,0.95)' }}
          >
            <div className="px-4 py-3 space-y-1">
              {navLinks.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  className={`block px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive(link.to)
                      ? 'bg-observatory-surfaceLight text-observatory-textPrimary'
                      : 'text-observatory-textSecondary hover:text-observatory-textPrimary'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
              {!isAuthenticated && (
                <Link
                  to="/login"
                  className="block px-3 py-2 rounded-lg text-sm font-medium text-observatory-textSecondary hover:text-observatory-textPrimary"
                >
                  Sign In
                </Link>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  )
}
