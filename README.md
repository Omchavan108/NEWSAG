# NewsAura

NewsAura is a full-stack, AI-augmented news reader designed for personalized discovery, saving and lightweight analytics. It combines a React + Tailwind frontend with a Python FastAPI backend, stores user content and activity in MongoDB, and uses Redis for caching. The app integrates with external news sources and provides summarization and sentiment insights to improve reading workflows.

---

## 1. Project Overview

- What NewsAura is
  - A web application for browsing, saving, and summarizing news. It provides curated topic feeds, the ability to bookmark or save articles to read later, and AI-powered summaries and sentiment signals.

- Core problem it solves
  - Reduces friction of consuming many daily news stories by surfacing topic-based feeds, enabling users to save articles for later, and offering quick AI summaries and sentiment/context to speed comprehension.

- High-level feature list
  - Topic/category-based news feeds
  - Search and suggestion features
  - Bookmark and Read Later lists per user
  - AI-generated article summaries (server-side)
  - Sentiment extraction for saved items
  - Profile analytics (articles read, saved counts, weekly activity, top category, engagement scoring)
  - Light caching with Redis to reduce external API load

---

## 2. Tech Stack

- Frontend
  - React (TypeScript), Vite, Tailwind CSS

- Backend
  - Python, FastAPI, Uvicorn (ASGI)

- Database
  - MongoDB for persistent storage of bookmarks, read-later items, summary logs and user-driven content

- Caching
  - Redis (used for cache / hit counters / performance — see `backend/app/core/cache.py` and project docs)

- External APIs
  - GNews (integration documentation and config files exist in the repo)

- Authentication
  - Clerk (project contains setup docs and references to Clerk integration)

---

## 3. System Architecture

High level flow:

  Frontend (React) <--HTTP/JSON--> FastAPI backend <--(optional cache)--> External News API (GNews)

- The frontend calls backend endpoints (news feeds, bookmarks, read-later, summaries, analytics).
- The backend queries external news APIs and may cache results in Redis to reduce request volume and improve latency.
- User actions (bookmark/read-later) are persisted in MongoDB; summary and sentiment logs are also persisted to support analytics.

ASCII diagram

  [Browser/React] --(REST)--> [FastAPI backend]
        |                         |---> [GNews API]
        |                         |---> [Redis cache]
        |                         \---> [MongoDB]

- Redis role: caches frequently-requested feed responses and hits counters (improves throughput and reduces external API calls).
- MongoDB role: primary persistent store for user data and event logs.
- Rate limiting strategy: the codebase does not include an explicit, application-level rate limiter. For production deployments, a Redis-backed rate limiter or API gateway should be used to protect external API keys and backend endpoints.

---

## 4. Backend Architecture

Overview
- The backend is a FastAPI application with a modular layout under `backend/app/`.

Major modules
- `routers/` — HTTP endpoints grouped by feature (news, bookmarks, read_laters, profile analytics, sentiments, summary, etc.). Each router returns JSON responses and relies on services for core logic.
- `services/` — Domain logic and integrations. Notable modules include the news integration, summarizer, and `sentiment_ml` for sentiment processing.
- `core/` — Core cross-cutting utilities such as `auth.py` (Clerk authentication helpers), `cache.py` (Redis connection and cache helpers), `config.py` (configuration loader), and `database.py` (MongoDB connection factory).
- `models/` — Pydantic models for request/response and Mongo objects (bookmarks, read_later, summary logs, etc.).

GNews integration
- The backend fetches topic-based or search-based news from GNews (integration details and keys are referenced in repository docs). Results are normalized and, where applicable, stored or summarized.

Redis caching
- Used to cache feed responses and counters. Cache helpers live under `core` and are used by services/routers to reduce repeated external API calls.

Sentiment analysis
- The `sentiment_ml` service/module is responsible for extracting sentiment labels from saved content; those labels are stored alongside bookmarks/read-later entries and used in profile analytics.

Summaries
- Summaries are generated on the backend (summarizer service). The frontend requests an article summary and the backend either uses cached summaries or generates a new one via the summarizer implementation.

Analytics & engagement
- Profile analytics are computed server-side (see `routers/profile.py`). The endpoint aggregates counts from MongoDB (articles read, bookmarks, read-later), computes weekly activity by created_at timestamps, builds a category breakdown, and calculates an `engagement_score` defined as:

  engagement_score = articles_read + (bookmarks_count * 2) + read_later_count

  The engagement score maps to labels such as “Casual Reader”, “Active Reader”, and “Power Reader”.

---

## 5. Frontend Architecture

Overview
- Located under `frontend/`, the UI is a TypeScript React app scaffolded with Vite and styled using Tailwind CSS.

Key structure
- `src/pages/` — Top-level routes/pages (`Home`, `Bookmarks`, `ReadLater`, `Profile`).
- `src/components/` — Reusable UI components (layout, news cards, modals, sentiment badge, toast, etc.).
- `src/services/` — HTTP client wrappers (`api.ts`) and typed service modules (`news.service.ts`, `user.service.ts`) that call backend endpoints.
- `src/utils/` — Utility functions (time formatting, text helpers).

State management
- Uses component state and local hooks (no external global state manager required). Data is fetched from typed `userService` and `newsService` modules.

API integration pattern
- Services call backend endpoints via a shared `api` client; responses map to TypeScript interfaces defined in `src/types.ts`.

---

## 6. Search & Discovery Flow

- Category-based fetching: Frontend requests category/topic endpoints; backend queries the external news API (GNews) and returns normalized articles.
- Keyword search: Search queries are passed to backend endpoints which proxy search to the external API and return paged or limited results.
- Search suggestions: A lightweight suggestions service exists to return cached or derived suggestions (see `news.service.ts` and `api` utilities).
- Cache-first strategy: Feed requests can be served from Redis cache first when available to reduce external API calls and improve local responsiveness.

---

## 7. User Interaction Flow

- Reading articles: Users click through to the original article (external link) or open an AI summary modal generated by the backend summarizer.
- AI summaries: Triggered by the frontend, generated server-side, and optionally cached.
- Bookmarking: User bookmarks are posted to `/api/bookmarks/` and persisted in MongoDB. Bookmarks include article metadata and optional category.
- Read Later: Similar to bookmarks; saved items include metadata and timestamps.
- Comments: The repo contains comment-related routers and frontend components — comments are persisted and fetched per-article.

---

## 8. Analytics & Profile Dashboard

- What is tracked
  - Articles read (summary log entries)
  - Bookmarks count
  - Read Later count
  - Weekly activity (counts by day)
  - Top category (computed from saved bookmarks/read-later category fields)
  - Sentiment breakdown for saved items (Positive/Neutral/Negative)

- How metrics are calculated
  - Aggregated server-side from MongoDB documents and timestamp fields (created_at). Top category is computed by counting categories across bookmark and read-later collections.

- Engagement scoring
  - engagement_score = articles_read + (bookmarks_count * 2) + read_later_count
  - Labels are derived from score ranges (e.g., “Power Reader” for high engagement).

---

## 9. Folder Structure

Top-level (abridged):

```
NEWSAG/
├─ backend/
│  ├─ app/
│  │  ├─ routers/         # API endpoints (news, bookmarks, read_laters, profile, sentiments, summary, ...)
│  │  ├─ services/        # Business logic (news integration, summarizer, sentiment)
│  │  ├─ core/            # auth, cache, config, database helpers
│  │  ├─ models/          # Pydantic models for requests/responses and Mongo documents
│  │  └─ main.py          # FastAPI application entrypoint
│  └─ requirements.txt
├─ frontend/
│  ├─ src/
│  │  ├─ pages/           # Home, Profile, Bookmarks, ReadLater
│  │  ├─ components/      # UI building blocks
│  │  ├─ services/        # API clients and typed services
│  │  ├─ utils/           # helper functions
│  │  └─ index.css        # global styles + Tailwind setup
│  ├─ package.json
│  └─ vite.config.ts
└─ docs and project-level .md files (setup guides, migration notes)
```

Short explanations
- `backend/app/routers` — every public API route is grouped here (e.g., `profile.py` contains analytics aggregations).
- `backend/app/services` — contains specialized modules (summarizer, sentiment_ml, news_service) that perform external API calls and processing.
- `frontend/src/services` — client-side service wrappers used by pages/components to fetch typed data.

---

## 10. Environment Configuration

Required environment variables (inferred from integrations and code structure):

```
# MongoDB connection string
MONGODB_URI=mongodb://localhost:27017/newsag

# Redis connection (if using redis caching)
REDIS_URL=redis://localhost:6379/0

# External news API
GNEWS_API_KEY=your_gnews_api_key_here

# Clerk (if using Clerk authentication — see Clerk docs in repo)
CLERK_FRONTEND_API=your_clerk_frontend_api
CLERK_API_KEY=your_clerk_api_key

# Optional: backend host/port
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
```

Placeholders should be stored in a `.env` file read by backend `config.py` or injected into your environment when running locally. Do not commit real keys.

---

## 11. Performance & Scalability Considerations

- Redis caching strategy: Cache high-traffic feed responses and frequently-requested summaries; use short TTLs for freshness.
- API hit protection: There is no explicit rate-limiter in the codebase; a production deployment should add a Redis-backed rate limiter or API gateway to protect external API usage.
- ML model loading: Sentiment and summarization components are implemented server-side; ensure models are loaded lazily and reused across requests to avoid repeated initialization cost.
- Async handling: The FastAPI code uses async Mongo and async endpoints; this enables high concurrency when combined with an ASGI server (uvicorn) and proper connection pooling.

---

## 12. Security Considerations

- Authentication: Clerk is used for user auth; tokens and session checks are validated in `core/auth.py`.
- Token validation: Backend routes call helper functions to validate the authenticated user before allowing writes to user-scoped collections.
- Rate-limit safety: Not implemented; recommend a Redis-based limiter.
- Data isolation: All user-scoped queries include `user_id` filters to avoid cross-user data leaks.

---

## 13. Future Enhancements (future scope — not implemented)

- Add server-side rate limiting and throttling middleware.
- Implement background tasks for heavy summarization work (Celery/RQ) to avoid blocking request handlers.
- Add paged, incremental loading for very large bookmark/read-later lists.
- Add richer personalization and recommendation signals (off-device ML or model-service architecture).

---

## 14. How to Run the Project (Local development)

Backend (Python/FastAPI)

1. Create a Python virtual environment and install requirements:

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

2. Provide environment variables (example `.env`) and start the server:

```bash
export MONGODB_URI='mongodb://localhost:27017/newsag'
export REDIS_URL='redis://localhost:6379/0'
export GNEWS_API_KEY='...'
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Frontend (React / Vite)

1. Install dependencies and start dev server:

```bash
cd frontend
npm install
npm run dev
# The app typically serves on http://localhost:5173
```

Notes
- The backend default port observed during development is `8000`, and the frontend Vite server commonly runs on `5173` in this repo (see dev run logs and screenshots).
- After changing backend models (for example adding fields to Pydantic models), restart the backend to pick up changes.

---

## Contributing / Notes for Reviewers

- The codebase is organized to separate HTTP routing, business services, and core infra helpers. When adding features, follow the existing pattern: routers call services, services use `core` helpers and `models` for validation and persistence.
- The project contains documentation files at the repo root (integration guides for GNews, Redis migration notes, and Clerk setup) — consult those for integration details and environment variable names.

---

If you want, I can:
- add a short architecture diagram in SVG/ascii to the docs,
- or run a quick read of `backend/app/routers/profile.py` and show the exact analytics output shape for a sample user.

This README was generated from the repository structure and inline code references. No external services or undocumented features were assumed.
