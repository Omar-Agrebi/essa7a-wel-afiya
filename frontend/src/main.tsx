import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import { useAuthStore } from '@/store/authStore'
import App from './App'
import './index.css'

// ── Load auth state from localStorage BEFORE rendering ──
useAuthStore.getState().loadFromStorage()

// ── Apply dark class to root ──
document.documentElement.classList.add('dark')

const rootEl = document.getElementById('root')
if (!rootEl) throw new Error('Root element not found')

createRoot(rootEl).render(
  <StrictMode>
    <BrowserRouter>
      <App />
      <Toaster
        position="bottom-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#0f172a',
            color: '#f0f4ff',
            border: '1px solid #1e3a5f',
            fontFamily: "'DM Sans', sans-serif",
            fontSize: '14px',
          },
          success: {
            iconTheme: { primary: '#10b981', secondary: '#0f172a' },
            style: {
              background: '#0f172a',
              border: '1px solid #064e3b',
              color: '#f0f4ff',
            },
          },
          error: {
            iconTheme: { primary: '#ef4444', secondary: '#0f172a' },
            style: {
              background: '#0f172a',
              border: '1px solid #7f1d1d',
              color: '#f0f4ff',
            },
          },
        }}
      />
    </BrowserRouter>
  </StrictMode>
)
