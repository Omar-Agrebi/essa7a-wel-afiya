# 🎓 Intelligent University Observatory

> A Multi-Agent System (MAS) for automated discovery, classification, and personalized recommendation of academic opportunities — internships, scholarships, research projects, certifications, and postdocs.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Tech Stack](#tech-stack)
4. [Project Structure](#project-structure)
5. [Quick Start (SQLite / Local Dev)](#quick-start-sqlite--local-dev)
6. [Production Setup (PostgreSQL + Docker)](#production-setup-postgresql--docker)
7. [Mock Data & Demo Credentials](#mock-data--demo-credentials)
8. [API Reference](#api-reference)
9. [Multi-Agent Pipeline](#multi-agent-pipeline)
10. [ML Layer](#ml-layer)
11. [Frontend](#frontend)
12. [Configuration](#configuration)
13. [Testing](#testing)
14. [Known Limitations & Roadmap](#known-limitations--roadmap)

---

## Overview

The Intelligent University Observatory automatically:

- **Scrapes** opportunities from multiple sources (mock or live)
- **Cleans & normalizes** raw data (HTML stripping, date normalization, URL validation)
- **Classifies** opportunities by type (`internship`, `scholarship`, `project`, `course`, `postdoc`) and domain category (`AI`, `Data Science`, `Cybersecurity`, `Software Engineering`)
- **Clusters** opportunities into thematic groups using KMeans
- **Recommends** personalized opportunities per user using TF-IDF cosine similarity, level matching, and deadline recency scoring
- **Notifies** users of urgent deadlines and new matches

---

## Architecture

```
React Frontend (Vite + TypeScript + Tailwind)
       ↓  REST API over HTTP
FastAPI Routers  (/opportunities, /users, /recommendations, /notifications, /pipeline, /health)
       ↓
Services (OpportunityService, UserService, RecommendationService, NotificationService)
       ↓
Repositories (BaseRepository[T] + domain-specific repos)
       ↓
Database (PostgreSQL in production | SQLite for local dev)

+ ML Layer  (TF-IDF Classifier · KMeans Clusterer · Cosine Similarity Recommender)
+ MAS Layer (MESA Model · 10 Agents · StagedActivation pipeline)
```

### Multi-Agent Pipeline (MESA)

```
Phase 1 — Parallel scraping (asyncio.gather):
  AgentInternshipScraper  AgentScholarshipScraper
  AgentProjectScraper     AgentCertificationScraper

Phase 2 — Sequential stages (StagedActivation):
  clean → classify → cluster → store → recommend → notify
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | FastAPI 0.115, Python 3.11+ |
| ORM | SQLAlchemy 2.0 async |
| Database (prod) | PostgreSQL 15 |
| Database (dev) | SQLite via aiosqlite |
| Migrations | Alembic |
| Auth | JWT (python-jose) + bcrypt (passlib) |
| Validation | Pydantic v2 |
| ML | scikit-learn (TF-IDF, LogisticRegression, KMeans) |
| NLP | dateparser, BeautifulSoup4 |
| MAS Framework | MESA 2.3 |
| Scheduling | APScheduler |
| Frontend | React 18, Vite, TypeScript, Tailwind CSS, Zustand |
| Containerization | Docker + Docker Compose |

---

## Project Structure

```
intelligent_university_observatory/
├── app/
│   ├── api/
│   │   ├── dependencies/      # JWT auth dependency
│   │   ├── middleware/        # CORS, logging
│   │   ├── routers/           # 6 API routers
│   │   └── schemas/           # Pydantic v2 schemas
│   ├── core/
│   │   ├── config.py          # pydantic-settings (reads .env)
│   │   ├── constants.py       # Enums: OpportunityType, UserLevel, etc.
│   │   ├── logging.py         # Structured logging
│   │   └── security.py        # bcrypt + JWT utilities
│   ├── models/                # SQLAlchemy models (SQLite-compatible)
│   ├── repositories/          # Generic BaseRepository[T] + domain repos
│   └── services/              # Business logic layer
├── agents/
│   ├── base_agent.py          # BaseAgent(mesa.Agent) with run_safe()
│   ├── observatory_model.py   # ObservatoryModel(mesa.Model) — orchestrator
│   ├── scrapers/
│   │   ├── base_scraper.py    # Live/mock switching via SCRAPER_MODE
│   │   ├── internship_scraper.py   # 20 mock internships
│   │   ├── scholarship_scraper.py  # 15 mock scholarships
│   │   ├── project_scraper.py      # 12 mock research projects
│   │   └── certification_scraper.py # 15 mock courses (Coursera API shape)
│   ├── processing/
│   │   ├── data_cleaner_agent.py   # HTML strip, date normalize, URL validate
│   │   ├── classifier_agent.py     # Calls OpportunityClassifier
│   │   └── cluster_agent.py        # Calls OpportunityClusterer
│   ├── recommendation/
│   │   ├── advisor_agent.py        # Full recommendation pass per user
│   │   └── relevance_matcher_agent.py  # Utility matcher
│   └── system/
│       ├── store_agent.py          # Persists clustered opportunities to DB
│       └── notification_agent.py   # Generates deadline alerts
├── ml/
│   └── inference/
│       ├── classifier.py      # TF-IDF + LogisticRegression (type + category)
│       ├── clustering.py      # TF-IDF + KMeans (n_clusters=5)
│       └── recommender.py     # TF-IDF cosine similarity + level + recency
├── database/
│   ├── base.py                # DeclarativeBase + TimestampMixin
│   ├── session.py             # AsyncSessionLocal, get_db()
│   └── init_db.py             # create_all() on startup
├── pipeline/
│   ├── scheduler.py           # APScheduler: full/rec/notify jobs
│   └── tasks/                 # Task functions called by scheduler
├── scripts/
│   └── seed_mock_data.py      # ⭐ Mock data seeder (SQLite-compatible)
├── tests/
│   └── test_observatory.py    # Full test suite (ML + scrapers + agents + pipeline)
├── frontend/                  # React + Vite + TypeScript app
│   └── src/
│       ├── api/               # Axios clients (opportunities, auth, recommendations)
│       ├── components/        # Layout, OpportunityCard, MatchReasons, etc.
│       ├── pages/             # Home, Opportunities, Dashboard, Profile, Auth
│       ├── store/             # Zustand authStore
│       └── types/             # TypeScript interfaces mirroring backend schemas
├── alembic/                   # Migration scripts (for PostgreSQL)
├── docker/                    # Dockerfiles
├── main.py                    # FastAPI app entry point
├── .env.example               # Environment variable template
└── requirements.txt           # Python dependencies
```

---

## Quick Start (SQLite / Local Dev)

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- pip

### 1. Clone & Install Backend

```bash
git clone <your-repo-url>
cd intelligent_university_observatory

# Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install aiosqlite        # For SQLite local dev
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
# Use SQLite for local development
DATABASE_URL=sqlite+aiosqlite:///./observatory.db
SECRET_KEY=your-super-secret-key-change-this-in-production
CORS_ORIGINS=http://localhost:5173
ENVIRONMENT=development
SCRAPER_MODE=mock
```

### 3. Seed the Database with Mock Data

```bash
python scripts/seed_mock_data.py
```

This inserts:
- **29 realistic opportunities** (internships, scholarships, projects, courses, postdocs)
- **4 demo users** (Alice, Bob, Carol, Diana — each with different skills and interests)
- **32 ML-scored recommendations** (generated by the real recommender engine)
- **16 notifications** (deadline alerts + discovery alerts)

### 4. Start the Backend

```bash
python main.py
# or
uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```

API is live at: **http://127.0.0.1:8000**  
Swagger docs: **http://127.0.0.1:8000/docs**

### 5. Start the Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend is live at: **http://localhost:5173**

> The Vite proxy forwards `/api/*` requests to `http://127.0.0.1:8000`, so no CORS issues during development.

---

## Production Setup (PostgreSQL + Docker)

### 1. Configure Production `.env`

```env
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@db:5432/observatory
SECRET_KEY=change-this-to-a-very-long-random-secret-key
CORS_ORIGINS=https://your-frontend-domain.com
ENVIRONMENT=production
SCRAPER_MODE=mock
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

Services:
- `db` — PostgreSQL 15
- `api` — FastAPI backend on port 8000
- `worker` — Pipeline worker
- `frontend` — React on port 3000 (via nginx)

### 3. Run Alembic Migrations

```bash
docker-compose exec api alembic upgrade head
```

### 4. Seed Data (optional)

```bash
docker-compose exec api python scripts/seed_mock_data.py
```

---

## Mock Data & Demo Credentials

The seeder creates 4 demo users, each tailored to a different research profile:

| Name | Email | Password | Level | Focus |
|---|---|---|---|---|
| Alice Martin | alice@example.com | Password123! | Master | AI / NLP / PyTorch |
| Bob Chen | bob@example.com | Password123! | PhD | Data Science / Statistics |
| Carol Ndiaye | carol@example.com | Password123! | Master | Cybersecurity / Networks |
| Diana Kowalski | diana@example.com | Password123! | Bachelor | Software Engineering / APIs |

### Opportunity Distribution

| Type | Count | Examples |
|---|---|---|
| Internship | 10 | DeepMind RL intern, ETH Zurich CV intern, ESA Data Science intern |
| Scholarship | 6 | DAAD, Eiffel, Gates Cambridge, Swiss Gov Excellence |
| Research Project | 5 | Horizon Europe federated learning, ERC explainable AI |
| Course | 5 | Deep Learning Specialization, MLOps, Ethical Hacking |
| Postdoc | 3 | ETH Zurich trustworthy ML, INRIA NLP fellow |

---

## API Reference

### Public Endpoints (no auth required)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | System health check |
| `GET` | `/opportunities/` | List opportunities (filters: `type`, `category`, `keyword`, `cluster_id`, `expiring_in_days`) |
| `GET` | `/opportunities/search?keyword=...` | Full-text search on title + description |
| `GET` | `/opportunities/expiring?days=7` | Opportunities expiring within N days |
| `GET` | `/opportunities/{id}` | Single opportunity by ID |
| `POST` | `/users/register` | Register a new user |
| `POST` | `/users/login` | Login — returns JWT access token |

### Protected Endpoints (Bearer token required)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/users/me` | Get current user profile |
| `PUT` | `/users/me` | Update profile (name, email, level) |
| `PUT` | `/users/me/skills` | Replace skills array |
| `PUT` | `/users/me/interests` | Replace interests array |
| `GET` | `/recommendations/` | Get top-N recommendations for current user |
| `POST` | `/recommendations/refresh` | Recompute recommendations for current user |
| `GET` | `/notifications/` | Get notifications for current user |
| `PUT` | `/notifications/{id}/read` | Mark notification as read |
| `POST` | `/pipeline/run` | Trigger full pipeline (background) |
| `GET` | `/pipeline/status` | Get last pipeline run status |

### Example: Login & Get Recommendations

```bash
# 1. Login
TOKEN=$(curl -s -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Password123!"}' | \
  python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])")

# 2. Get personalized recommendations
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/recommendations/
```

### Example: Filter Opportunities

```bash
# Internships in AI
curl "http://localhost:8000/opportunities/?type=internship&category=AI&limit=10"

# Search by keyword
curl "http://localhost:8000/opportunities/search?keyword=reinforcement+learning"

# Expiring in 10 days
curl "http://localhost:8000/opportunities/expiring?days=10"
```

---

## Multi-Agent Pipeline

### Agent Registry

| ID | Agent | Stage | Role |
|---|---|---|---|
| 1 | `AgentInternshipScraper` | scrape | Fetches/generates internship data |
| 2 | `AgentScholarshipScraper` | scrape | Fetches/generates scholarship data |
| 3 | `AgentProjectScraper` | scrape | Fetches/generates research project data |
| 4 | `AgentCertificationScraper` | scrape | Fetches/generates course/cert data |
| 5 | `AgentDataCleaner` | clean | Strips HTML, normalizes dates, validates URLs |
| 6 | `AgentClassifier` | classify | Predicts type + category via ML |
| 7 | `AgentCluster` | cluster | Groups into 5 thematic clusters |
| 8 | `AgentStore` | store | Persists to database via bulk_upsert |
| 9 | `AgentAdvisor` | recommend | Generates per-user recommendations |
| 10 | `AgentNotification` | notify | Creates deadline alerts |
| 99 | `AgentRelevanceMatcher` | — | Utility (not scheduled directly) |

### Scraper Modes

Set `SCRAPER_MODE` in `.env`:

- `mock` — Returns hardcoded realistic data (default, no external requests)
- `live` — Makes real HTTP requests (for scrapers that have real API targets, e.g. Coursera)

### Running the Pipeline Manually

```python
import asyncio
from agents.observatory_model import ObservatoryModel
from app.core.config import settings

model = ObservatoryModel(services=build_services(db), settings=settings)
report = asyncio.run(model.run_pipeline())
print(report)
```

---

## ML Layer

### 1. Classifier (`ml/inference/classifier.py`)

- **Algorithm:** TF-IDF (bigrams, max 5000 features) + Logistic Regression
- **Trained on:** 80 labeled examples (20 internships, 20 scholarships, 15 projects, 15 courses, 10 postdocs)
- **Outputs:** `type` and `category` per opportunity text
- **Training accuracy:** ~98% (synthetic data, in-distribution)

```python
from ml.inference.classifier import OpportunityClassifier
clf = OpportunityClassifier()
clf.train()
print(clf.predict_type("DAAD scholarship for master students in AI"))  # → "scholarship"
print(clf.predict_category("Deep learning with PyTorch and transformers"))  # → "AI"
```

### 2. Clusterer (`ml/inference/clustering.py`)

- **Algorithm:** TF-IDF (max 3000 features) + KMeans (k=5, n_init=10)
- **Cluster labels:** Auto-generated from top-5 TF-IDF terms per centroid
- **Minimum:** Requires ≥5 opportunities to cluster

```python
from ml.inference.clustering import OpportunityClusterer
clusterer = OpportunityClusterer(n_clusters=5)
clusterer.fit(texts)
print(clusterer.predict("Reinforcement learning AI safety research"))  # → 0
print(clusterer.get_cluster_label(0))  # → "machine learning phd research"
```

### 3. Recommender (`ml/inference/recommender.py`)

Scoring formula:

```
final_score = W1 × cosine_similarity(user_profile, opportunity)
            + W2 × level_match_score
            + W3 × deadline_recency_score

Default weights (configurable in config.py):
  W1 = 0.5  (semantic similarity)
  W2 = 0.3  (level match: 1.0 exact, 0.5 adjacent, 0.0 incompatible)
  W3 = 0.2  (recency: 1.0 far, 0.5 medium, 0.2 urgent, 0.0 expired)
```

Each recommendation includes human-readable `match_reasons`:
```json
[
  "4 of your skills match (python, pytorch, nlp)",
  "Master level compatible",
  "High relevance (36% match)",
  "Matches your interest in AI"
]
```

---

## Frontend

The React frontend communicates with the FastAPI backend via `/api/*` (proxied by Vite in dev).

### Pages

| Route | Page | Auth |
|---|---|---|
| `/` | Home — hero + featured opportunities | Public |
| `/opportunities` | Browse + filter all opportunities | Public |
| `/opportunities/:id` | Opportunity detail view | Public |
| `/login` | JWT login form | Public |
| `/register` | Registration form | Public |
| `/dashboard` | Personalized recommendations + stats | Protected |
| `/profile` | Edit skills, interests, academic level | Protected |

### Frontend Architecture

```
src/
├── api/        # Axios clients (client.ts, opportunities.ts, auth.ts, ...)
├── store/      # Zustand authStore (JWT + user state, localStorage)
├── types/      # TypeScript interfaces (mirror backend Pydantic schemas)
├── components/ # Reusable UI (Navbar, OpportunityCard, MatchReasons, TagInput, ...)
└── pages/      # Route-level page components
```

### Running the Frontend

```bash
cd frontend
npm install
npm run dev      # dev server on http://localhost:5173
npm run build    # production build → frontend/dist/
```

---

## Configuration

All config lives in `.env` and is read by `app/core/config.py` (pydantic-settings):

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | — | SQLAlchemy async URL (sqlite or postgresql+asyncpg) |
| `SECRET_KEY` | — | JWT signing key (keep secret!) |
| `CORS_ORIGINS` | — | Comma-separated allowed origins |
| `ENVIRONMENT` | `development` | Controls log level (`development` → DEBUG) |
| `SCRAPER_MODE` | `mock` | `mock` or `live` |
| `RECOMMENDATION_W1` | `0.5` | Weight: cosine similarity |
| `RECOMMENDATION_W2` | `0.3` | Weight: level match |
| `RECOMMENDATION_W3` | `0.2` | Weight: deadline recency |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | JWT expiry |
| `ALGORITHM` | `HS256` | JWT algorithm |

---

## Testing

### Run the Full Test Suite (no DB required)

```bash
python tests/test_observatory.py
```

Covers:
- **ML Classifier** — train, predict type, predict category, batch predict, save/load
- **ML Clusterer** — fit, predict, label generation, save/load, error handling
- **ML Recommender** — level match, recency scoring, similarity, match reasons, ranking
- **Scrapers** — mock data structure, normalized fields, parallel gather
- **Processing Agents** — cleaner (HTML/date/URL), classifier agent, cluster agent
- **Advisor Agent** — full recommendation pass with match_reasons
- **Full Pipeline Simulation** — 5 phases end-to-end without DB
- **Data Quality** — type coverage, ISO dates, valid URLs, no empty titles

Expected output: **~40 tests, 100% pass rate**

### Test API Endpoints

With the server running:

```bash
# Health
curl http://localhost:8000/health

# All opportunities
curl http://localhost:8000/opportunities/?limit=10

# Filter by type
curl "http://localhost:8000/opportunities/?type=internship&limit=5"

# Login
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"email":"alice@example.com","password":"Password123!"}'
```

### Swagger UI

Navigate to `http://localhost:8000/docs` for interactive API documentation with all endpoints, schemas, and try-it-out functionality.

---

## Known Limitations & Roadmap

### v1 Limitations

| Area | Current State |
|---|---|
| Scraping | Mock data only for LinkedIn/Indeed (they block scrapers). Coursera API shape is implemented |
| ML training data | Synthetic — real-world accuracy will be lower until labeled data is collected |
| Security | No rate limiting, no input sanitization beyond basic cleaning |
| Observability | No pipeline run history table |
| Auth | No refresh token rotation, no password reset flow |
| SQLite | ARRAY columns use JSON strings; switch to PostgreSQL for production |

### Recommended Roadmap

```
Month 1: Polish demo end-to-end with SQLite + real labeled data
Month 2: Migrate to PostgreSQL + Docker + add auth hardening
Month 3: Connect real data sources (arXiv API, Coursera API, EU Open Data)
Month 4: Add pipeline run history, observability, production deployment
```

### Real Data Sources (Accessible APIs)

| Source | API | Data Type |
|---|---|---|
| arXiv | `export.arxiv.org/api/` | Research papers/postdocs |
| Coursera | `api.coursera.org/api/courses.v1` | Courses/certifications |
| EU Open Data | `data.europa.eu/api/hub/search` | EU-funded projects |
| DAAD | RSS feeds | Scholarships |

---

## Git Workflow

```bash
# Initial setup
git init
git add .
git commit -m "chore: initial commit"
git remote add origin https://github.com/your-username/observatory.git
git push -u origin main

# Feature branches
git checkout -b feature/real-scrapers
# ... make changes ...
git commit -m "feat: connect arXiv API to project scraper"
git push -u origin feature/real-scrapers
```

### Branch Strategy

```
main          ← stable, production-ready
dev           ← active development
feature/*     ← individual features
```

---

## License

MIT — See LICENSE file for details.

---

*Intelligent University Observatory v1.0 — Built with FastAPI + MESA + React*
