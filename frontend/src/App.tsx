import { lazy, Suspense } from 'react'
import { Routes, Route, Navigate } from 'react-router-dom'
import { AnimatePresence } from 'framer-motion'
import Navbar from '@/components/layout/Navbar'
import ProtectedRoute from '@/components/layout/ProtectedRoute'
import { LoadingSpinner } from '@/components/ui'

// ── Lazy-loaded pages ──
const HomePage = lazy(() => import('@/pages/HomePage'))
const OpportunitiesPage = lazy(() => import('@/pages/OpportunitiesPage'))
const OpportunityDetailPage = lazy(() => import('@/pages/OpportunityDetailPage'))
const LoginPage = lazy(() => import('@/pages/LoginPage'))
const RegisterPage = lazy(() => import('@/pages/RegisterPage'))
const DashboardPage = lazy(() => import('@/pages/DashboardPage'))
const ProfilePage = lazy(() => import('@/pages/ProfilePage'))
const InsightsPage = lazy(() => import('@/pages/InsightsPage'))

function PageLoader() {
  return (
    <div className="min-h-screen bg-observatory-bg flex items-center justify-center">
      <LoadingSpinner size="lg" label="LOADING..." />
    </div>
  )
}

export default function App() {
  return (
    <>
      <Navbar />
      <Suspense fallback={<PageLoader />}>
        <AnimatePresence mode="wait">
          <Routes>
            {/* Public */}
            <Route path="/" element={<HomePage />} />
            <Route path="/opportunities" element={<OpportunitiesPage />} />
            <Route path="/opportunities/:id" element={<OpportunityDetailPage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/insights" element={<InsightsPage />} />

            {/* Protected */}
            <Route element={<ProtectedRoute />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/profile" element={<ProfilePage />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </AnimatePresence>
      </Suspense>
    </>
  )
}
