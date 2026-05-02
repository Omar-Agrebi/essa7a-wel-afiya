/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        observatory: {
          bg: '#0a0f1e',
          surface: '#0f172a',
          surfaceLight: '#1e293b',
          border: '#1e3a5f',
          primary: '#1e40af',
          primaryLight: '#3b5fd4',
          primaryDark: '#1a3691',
          accent: '#7c3aed',
          accentLight: '#9461f5',
          starGold: '#fbbf24',
          textPrimary: '#f0f4ff',
          textSecondary: '#94a3b8',
          textMuted: '#475569',
        },
      },
      fontFamily: {
        display: ['"Space Grotesk"', 'sans-serif'],
        body: ['"DM Sans"', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'pulse-glow': 'pulseGlow 2s ease-in-out infinite',
        'star-drift': 'starDrift 8s linear infinite',
        'telescope-focus': 'telescopeFocus 1s ease-out forwards',
        'stamp-reveal': 'stampReveal 0.4s ease-out forwards',
        'radar-sweep': 'radarSweep 3s linear infinite',
        'bell-swing': 'bellSwing 0.5s ease-in-out 3',
        'scan-line': 'scanLine 0.3s ease-out forwards',
        'ping-slow': 'ping 2s cubic-bezier(0, 0, 0.2, 1) infinite',
      },
      keyframes: {
        pulseGlow: {
          '0%, 100%': { boxShadow: '0 0 10px rgba(124,58,237,0.3)' },
          '50%': { boxShadow: '0 0 25px rgba(124,58,237,0.7)' },
        },
        starDrift: {
          '0%': { transform: 'translateY(0px)', opacity: '0.6' },
          '50%': { opacity: '1' },
          '100%': { transform: 'translateY(-100vh)', opacity: '0' },
        },
        telescopeFocus: {
          '0%': { filter: 'blur(8px)', opacity: '0' },
          '100%': { filter: 'blur(0px)', opacity: '1' },
        },
        stampReveal: {
          '0%': { transform: 'rotate(-10deg) scale(1.3)', opacity: '0' },
          '60%': { transform: 'rotate(-3deg) scale(0.95)', opacity: '0.8' },
          '100%': { transform: 'rotate(-4deg) scale(1)', opacity: '1' },
        },
        radarSweep: {
          '0%': { transform: 'rotate(0deg)' },
          '100%': { transform: 'rotate(360deg)' },
        },
        bellSwing: {
          '0%': { transform: 'rotate(0deg)' },
          '25%': { transform: 'rotate(-15deg)' },
          '75%': { transform: 'rotate(15deg)' },
          '100%': { transform: 'rotate(0deg)' },
        },
        scanLine: {
          '0%': { transform: 'translateX(-100%)', opacity: '0' },
          '100%': { transform: 'translateX(0)', opacity: '1' },
        },
      },
      backgroundImage: {
        'gradient-observatory': 'linear-gradient(135deg, #1e40af, #7c3aed)',
        'gradient-surface': 'linear-gradient(180deg, #0f172a, #0a0f1e)',
      },
    },
  },
  plugins: [],
}
