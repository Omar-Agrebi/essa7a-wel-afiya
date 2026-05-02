# Intelligent University Observatory — Frontend

React + TypeScript frontend for the Intelligent University Observatory multi-agent system.

---

## Stack

| Layer | Technology |
|---|---|
| Framework | React 18 + TypeScript (strict) |
| Build | Vite 5 |
| Styling | Tailwind CSS 3 (dark theme) |
| State | Zustand (with localStorage persistence) |
| HTTP | Axios (with JWT interceptors) |
| Routing | React Router v6 |
| Animation | Framer Motion |
| Icons | Lucide React |
| Toasts | React Hot Toast |
| Dates | date-fns |

---

## Prerequisites

- Node.js 18+
- Backend running at `http://localhost:8000`

---

## Setup

```bash
# 1. Install dependencies
npm install

# 2. Copy env
cp .env.example .env

# 3. Start dev server
npm run dev
```

Visit: http://localhost:5173

The Vite dev server proxies all `/api/*` requests to `http://localhost:8000`.

---

## Build for Production

```bash
npm run build
# Output in /dist
```

---

## Project Structure

```
src/
├── types/         — TypeScript interfaces (mirrors backend schemas exactly)
├── store/         — Zustand auth store
├── api/           — Axios API clients per domain
├── utils/         — Deadline urgency, formatting helpers
├── hooks/         — useDebounce, useUnreadCount
├── components/
│   ├── layout/    — Navbar, StarField, PageWrapper, ProtectedRoute
│   ├── opportunities/ — OpportunityCard, OpportunityFilters
│   ├── deadline/  — DeadlineBadge
│   ├── profile/   — SkillGalaxy, InterestTagInput
│   ├── dashboard/ — MissionCard, SystemStatus, TransmissionPanel
│   └── ui/        — GlassCard, GlowButton, LoadingSpinner, EmptyState, etc.
├── pages/
│   ├── HomePage
│   ├── OpportunitiesPage
│   ├── OpportunityDetailPage
│   ├── LoginPage
│   ├── RegisterPage
│   ├── DashboardPage
│   └── ProfilePage
├── App.tsx
├── main.tsx
└── index.css
```

---

## Backend API Endpoints Used

| Feature | Endpoint |
|---|---|
| Login | `POST /users/login` |
| Register | `POST /users/register` |
| Profile | `GET/PUT /users/me` |
| Skills | `PUT /users/me/skills` |
| Interests | `PUT /users/me/interests` |
| Opportunities | `GET /opportunities/` |
| Opportunity detail | `GET /opportunities/{id}` |
| Recommendations | `GET /recommendations/` |
| Refresh recs | `POST /recommendations/refresh` |
| Notifications | `GET /notifications/unread` |
| Mark read | `PUT /notifications/{id}/read` |
| Pipeline status | `GET /pipeline/status` |
| Run pipeline | `POST /pipeline/run` |

---

## Auth Flow

1. JWT token stored in Zustand + `localStorage`
2. `loadFromStorage()` called synchronously before React renders — no flash to login on refresh
3. Axios request interceptor attaches `Authorization: Bearer {token}` header
4. Axios response interceptor auto-logouts on 401

---

## Notes

- All API calls use `/api/` prefix — Vite proxies to backend
- TypeScript strict mode — no `any` types
- Dark space theme throughout — no light mode
- Mobile responsive: 1 col mobile, 2 tablet, 3 desktop
