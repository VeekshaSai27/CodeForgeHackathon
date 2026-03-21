# Skill Intelligence Platform

An AI-driven personalized learning system that analyzes a user's resume against a job description, validates their skills through adaptive testing, computes a prioritized learning roadmap, and delivers an interactive learning experience — all powered by **Gemini 2.5 Flash Lite**.

---

## How it works

```
Resume + JD
    │
    ▼
Skill Intelligence Service     → extracts & scores skills (SkillDNA)
    │
    ▼
Skill Validation Service       → generates & evaluates adaptive quiz
    │
    ▼
Skill Graph + Decision Engine  → builds dependency graph, computes learning path
    │
    ▼
Learning Experience (Frontend) → renders roadmap, resources, AI mentor chat
    │
    ▼
PostgreSQL                     → persists skills, assessments, logs
```

---

## Architecture

### Services

| Service | Language | Role |
|---|---|---|
| `skill_intelligence_service` | Python | Parses resume + JD → `SkillDNA` (skills, importance, confidence) |
| `skill_validation_service` | Python | Generates adaptive quiz questions, evaluates answers, scores proficiency |
| `skill_graph_engine` | Python | Builds skill dependency graph, computes Skill Pressure Scores, generates learning path |
| `api_server.py` | Python / Flask | Unified REST API — wires all 3 services to 5 endpoints |
| `frontend` | React / TypeScript / Vite | 3-step onboarding UI + dashboard + AI mentor chat |
| `database` | PostgreSQL 16 | Shared persistence layer — 20 tables across 8 domains |

### Shared infrastructure

| Component | File | Role |
|---|---|---|
| Gemini pool | `shared/gemini_pool.py` | Rotating API key pool with 429 back-off — used by all services |
| DB layer | `db.py` | psycopg2 persistence — skills, assessments, learning paths, system logs |
| Rate limiting | `flask-limiter` | 20 req/min on heavy endpoints, 30/min on chat, 60/min global |
| Session management | `api_server.py` | Thread-safe token-keyed sessions via `X-Session-Token` header |

---

## Project structure

```
CodeForgeHackathon/
├── api_server.py                    # Unified Flask + Gunicorn backend
├── db.py                            # PostgreSQL persistence layer
├── main.py                          # Standalone skill intelligence demo
├── requirements.txt
│
├── shared/
│   └── gemini_pool.py               # Rotating Gemini API key pool
│
├── skill_intelligence_service/
│   ├── __init__.py
│   ├── models.py                    # SkillDNA pydantic model
│   ├── prompts.py                   # LLM prompt template
│   └── service.py                   # Gemini inference + validation
│
├── skill_validation_service/
│   ├── services/
│   │   ├── gemini_service.py        # Thin wrapper → shared pool
│   │   ├── question_generator.py    # Generates 8 questions per skill
│   │   ├── evaluation_engine.py     # Scores answers by difficulty weight
│   │   ├── confidence_engine.py     # Confidence from answer variance
│   │   ├── adaptive_engine.py       # Next difficulty selector
│   │   └── skill_extractor.py       # Extracts skills from resume + JD
│   ├── utils/helpers.py             # Exaggeration detection
│   └── main.py                      # Standalone Flask app (legacy)
│
├── skill_graph_engine/
│   ├── __init__.py                  # run_engine() entry point
│   ├── base_graph.py                # Hardcoded prerequisite graph (25 skills)
│   ├── graph.py                     # Merges SkillDNA + expands via Gemini
│   ├── engine.py                    # Prerequisite filtering + roadmap builder
│   ├── scorer.py                    # Skill Pressure Score formula
│   ├── reasoning.py                 # Gemini explains each skill priority
│   └── models.py                    # SkillNode, RoadmapItem, LearningPath
│
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── UploadPage.tsx       # Step 1 — resume + JD input
│   │   │   ├── QuizPage.tsx         # Step 2 — adaptive skill quiz
│   │   │   └── DashboardPage.tsx    # Step 3 — roadmap + resources
│   │   ├── components/
│   │   │   ├── ChatPanel.tsx        # Floating AI mentor chat
│   │   │   └── ConfidenceBar.tsx    # Skill score visualizer
│   │   ├── context/OnboardingContext.tsx  # Global state across 3 steps
│   │   ├── lib/
│   │   │   ├── api.ts               # Typed fetch client + session token
│   │   │   └── learningEngine.js    # Client-side resource selector
│   │   └── types/onboarding.ts      # Shared TypeScript interfaces
│   └── vite.config.ts               # Dev proxy → Flask :5000
│
├── database/
│   ├── schema.sql                   # Full PostgreSQL schema (20 tables)
│   └── README.md                    # Schema docs, indexes, relationships
│
├── Dockerfile.api                   # Python 3.13-slim + Gunicorn
├── Dockerfile.frontend              # Node 20 build → Nginx 1.27 serve
├── docker-compose.yml               # Orchestrates postgres + api + frontend
├── nginx.conf                       # SPA routing + API reverse proxy
├── .env.example                     # All secrets template
└── .dockerignore
```

---

## API endpoints

All served by `api_server.py` on port `5000`. Every response includes `X-Session-Token` — the client must echo it back on subsequent requests to maintain session state.

| Method | Endpoint | Input | Output |
|---|---|---|---|
| `POST` | `/analyze-profile` | `{ resume, jd }` | `{ skills[], importance_scores{}, user_confidence{} }` |
| `POST` | `/generate-test` | `{ skills[] }` | `{ questions[] }` |
| `POST` | `/evaluate-test` | `{ answers{} }` | `{ proficiency{}, weak_areas[] }` |
| `POST` | `/compute-path` | `{ proficiency{}, ... }` | `{ learning_path[] }` |
| `POST` | `/chat` | `{ message, context? }` | `{ response }` |
| `GET` | `/health` | — | `{ status: "ok" }` |

---

## Skill Pressure Score

The Decision Engine ranks every skill using:

```
Score = 0.4 × Importance
      + 0.3 × (1 − Proficiency)
      + 0.2 × DependencyCentrality
      − 0.1 × Confidence
```

Skills whose prerequisites have `proficiency < 0.4` are filtered out before ranking. The top 3 unlocked skills become `status: "current"` in the roadmap.

---

## Gemini key pool

Set multiple keys in `.env` — the pool rotates on every request and retries with exponential back-off (1s → 2s → 4s) on `429 ResourceExhausted`:

```env
GEMINI_API_KEY_1=your_first_key
GEMINI_API_KEY_2=your_second_key
GEMINI_API_KEY_3=your_third_key
```

Single key fallback: `GEMINI_API_KEY=your_key`.

---

## Database schema (summary)

20 tables across 8 domains. Full schema in `database/schema.sql`.

| Domain | Tables |
|---|---|
| Users | `users`, `user_profiles` |
| Skill Intelligence | `skills`, `user_skills`, `job_roles`, `job_role_skills` |
| Skill Validation | `assessments`, `assessment_questions` |
| Skill Graph | `skill_graph_nodes`, `skill_graph_edges` |
| Decision Engine | `skill_scores`, `learning_paths`, `learning_path_nodes` |
| Learning Experience | `resources`, `user_progress` |
| Journey Tracking | `user_journeys`, `journey_events` |
| Observability | `system_logs`, `decision_logs` |

---

## Running with Docker (recommended)

```bash
# 1. Copy and fill secrets
cp .env.example .env

# 2. Build and start all 3 containers
docker compose up --build
```

| Service | URL |
|---|---|
| Frontend | http://localhost |
| API | http://localhost:5000 |
| PostgreSQL | localhost:5432 |

Startup order is enforced: `postgres` (healthcheck) → `api` (healthcheck) → `frontend`.

The schema is applied automatically on first boot via `docker-entrypoint-initdb.d`.

---

## Running locally (dev)

```bash
# 1. Install Python deps
pip install -r requirements.txt

# 2. Start PostgreSQL
docker compose up postgres -d

# 3. Copy and fill secrets (set POSTGRES_HOST=localhost)
cp .env.example .env

# 4. Start API server
python api_server.py

# 5. Start frontend (separate terminal)
cd frontend
npm install
npm run dev
```

| Service | URL |
|---|---|
| Frontend | http://localhost:8080 |
| API | http://localhost:5000 |

In dev, Vite proxies all API calls to `:5000` — no CORS configuration needed.

---

## Environment variables

Single `.env` file at project root covers all services.

```env
# Gemini (required)
GEMINI_API_KEY=your_key_here

# API server
API_PORT=5000
FLASK_DEBUG=false
CORS_ORIGINS=http://localhost:8080

# PostgreSQL
POSTGRES_DB=skill_platform
POSTGRES_USER=skill_user
POSTGRES_PASSWORD=changeme
POSTGRES_HOST=localhost   # use "postgres" inside Docker (set automatically)
POSTGRES_PORT=5432

# Frontend
VITE_API_URL=             # leave empty — proxy handles it in both dev and Docker
```

See `.env.example` for the full template.

---

## Tech stack

| Layer | Technology |
|---|---|
| LLM | Google Gemini 2.5 Flash Lite (`google-genai`) |
| Backend | Python 3.13, Flask 3, Gunicorn |
| Frontend | React 18, TypeScript, Vite, Tailwind CSS, shadcn/ui |
| Database | PostgreSQL 16, psycopg2 |
| Rate limiting | flask-limiter (in-memory) |
| Containerization | Docker, Docker Compose, Nginx 1.27 |
| Graph engine | NetworkX |
| Validation | Pydantic v2 |
