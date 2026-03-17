# NewsAura Project - Complete Diagrams & Documentation Summary

## 📋 Overview

This document maps all three detailed diagrams and the folder structure to help understand NewsAura's architecture from multiple perspectives.

---

## 🏗️ Diagram 1: System Architecture (High-Level)

**File Reference:** `FOLDER_STRUCTURE.md` → Architecture by Layer section

**What it shows:**
- **Frontend Layer:** React SPA with Clerk auth, UI components, and service wrappers
- **API Gateway:** FastAPI with CORS middleware and token validation
- **Service Layer:** Business logic (GNewsService, SentimentML, TextSummarizer, text_utils)
- **Data & Cache Layer:** Redis (ephemeral) and MongoDB (persistent)
- **External APIs:** GNews.io, HuggingFace Hub, article pages via scraping
- **API Routes:** All endpoints exposed by FastAPI

**Use cases:**
- Present to stakeholders to show overall system layout
- Explain tech stack choices to architects
- Plan scaling strategies

**Key files in this diagram:**
- Backend: `backend/app/main.py`, `backend/app/core/cache.py`, `backend/app/core/database.py`
- Frontend: `frontend/src/services/api.ts`, `frontend/src/app/App.tsx`

---

## 🔄 Diagram 2: Detailed Request Flow (Sequence Diagram)

**File Reference:** All flow sequences shown here

**Four key flows illustrated:**

### Flow 1: Get News by Topic (Cache-First)
```
User clicks category
→ Frontend: GET /api/news/topic/technology
→ Backend: Check Redis cache "gnews:technology"
  ├─ HIT: Return cached articles + sentiment
  └─ MISS:
      → Check daily quota (RedisCounter)
      → Fetch from GNews API
      → Enrich with sentiment (per-article ML caching)
      → Store in Redis (TTL: 900s)
      → Increment hit counter
→ Frontend: Display NewsGrid + NewsCards
```

**Files involved:**
- Frontend: `frontend/src/pages/Home.tsx`, `frontend/src/components/news/NewsGrid.tsx`
- Backend: `backend/app/routers/news.py`, `backend/app/services/news_service.py`, `backend/app/core/gnews_counter.py`

### Flow 2: Generate AI Summary
```
User clicks "AI Summary" on article
→ Frontend: POST /api/summary/ { url, content, description }
→ Backend: Check Redis cache "summary:{md5(url)}"
  ├─ HIT: Return cached summary
  └─ MISS:
      → Scrape full article text (httpx + BeautifulSoup)
      → If sufficient text (>200 words):
          └─ Run TF-IDF summarizer (lead-bias, redundancy filter)
      → Else: Fallback to GNews description
      → Cache summary
→ Frontend: Display in newspaper-style modal
```

**Files involved:**
- Frontend: `frontend/src/components/news/NewsCard.tsx` (summary modal section)
- Backend: `backend/app/routers/summary.py`, `backend/app/services/summarizer.py`, `backend/app/services/text_utils.py`

### Flow 3: Bookmark Article (User Action)
```
User clicks bookmark icon
→ Frontend: POST /api/bookmarks/ with Bearer token
→ Backend: Validate Clerk token
→ Database: Insert into MongoDB bookmarks collection
→ Frontend: Toggle bookmark icon UI state
```

**Files involved:**
- Frontend: `frontend/src/components/news/NewsCard.tsx` (toggleBookmark method)
- Backend: `backend/app/routers/bookmarks.py`, `backend/app/models/bookmark.py`, `backend/app/core/database.py`

### Flow 4: Admin Manual Refresh
```
Admin: POST /api/news/refresh/technology
→ Backend: Delete Redis cache for "gnews:technology"
→ Fetch fresh GNews data (1 hit used)
→ Enrich + cache fresh
→ Return refreshed articles
```

**Files involved:**
- Backend: `backend/app/routers/news.py` (refresh_category endpoint)

---

## 🔗 Diagram 3: Component Interaction

**File Reference:** Shows how modules call each other

**Key interactions:**
1. **Frontend → API:** Component calls `news.service.ts` / `user.service.ts` → `api.ts` (Axios)
2. **FastAPI → Services:** Routers call business logic services for enrichment
3. **Services → External:** GNewsService calls GNews API; SentimentML calls HuggingFace; TextUtils scrapes articles
4. **Services → Cache:** All services check Redis first, write results back
5. **Routes → Persistence:** Bookmark/Comment routes use MongoDB models

**Dependency example (single request flow):**
```
NewsCard.tsx
  ↓ calls newsService.getNewsByTopic("technology")
  ↓ calls api.get("/api/news/topic/technology")
  ↓ HTTP GET to FastAPI
  ↓ routers/news.py → GET /api/news/topic/technology
  ↓ calls GNewsService.fetch_category("technology")
  ↓ calls GNewsService.check_limit() (GNewsCounter via Redis)
  ↓ calls httpx.get(GNews API)
  ↓ for each article: SentimentService.analyze_article()
  ↓ SentimentService checks Redis, calls HF if needed
  ↓ stores enriched articles in Redis
  ↓ HTTP response back to frontend
  ↓ NewsGrid renders NewsCard instances
```

---

## 📁 Folder Structure Mapping

### Frontend Structure (`frontend/src/`)
```
src/
├── services/
│   ├── api.ts                    ← Config (Axios, Bearer token setup)
│   ├── news.service.ts           ← Wrappers for /api/news/*, /api/summary, /api/sentiment
│   └── user.service.ts           ← Wrappers for /api/bookmarks, /api/comments, /api/read-later
├── components/
│   ├── news/
│   │   ├── NewsCard.tsx          ← Individual article + summary modal + toggles
│   │   ├── NewsGrid.tsx          ← Container + responsive layout
│   │   ├── NewsCard_LIST.tsx     ← Same card, list layout variant
│   │   ├── SentimentBadge.tsx    ← Sentiment label display
│   │   └── TrendingBulletin.tsx  ← Marquee/ticker for trending
│   └── ui/
│       ├── Modal.tsx             ← Summary modal container
│       ├── Toast.tsx             ← Notification toasts
│       └── Button.tsx            ← Reusable button
└── pages/
    ├── Home.tsx                  ← Main feed (calls newsService)
    ├── Bookmarks.tsx             ← Saved articles
    ├── ReadLater.tsx             ← Read-later list
    └── Login.tsx                 ← Clerk login
```

### Backend Structure (`backend/app/`)
```
app/
├── main.py                       ← FastAPI app + router imports
├── core/
│   ├── config.py                 ← Environment settings (GNEWS_API_KEY, REDIS_URL, etc.)
│   ├── cache.py                  ← Redis client singleton + helpers
│   ├── database.py               ← MongoDB async client (Motor)
│   ├── gnews_counter.py          ← Daily quota enforcement
│   └── auth.py                   ← Token validation helpers (TODO: expand)
├── routers/
│   ├── news.py                   ← GET /api/news/... endpoints
│   ├── summary.py                ← POST /api/summary/ endpoint
│   ├── sentiments.py             ← POST /api/sentiment/ endpoint
│   ├── bookmarks.py              ← CRUD /api/bookmarks/
│   ├── comments.py               ← CRUD /api/comments/
│   └── read_laters.py            ← CRUD /api/read-later/
├── services/
│   ├── news_service.py           ← GNews API client
│   ├── sentiment_ml.py           ← HF transformer inference + caching
│   ├── summarizer.py             ← TF-IDF extractive summarizer
│   └── text_utils.py             ← Article text scraper (httpx + BeautifulSoup)
└── models/
    ├── bookmark.py               ← Mongo document schema
    ├── comment.py                ← Mongo document schema
    └── read_later.py             ← Mongo document schema
```

---

## 🔑 Key Files for Each Concern

| Concern | Frontend File(s) | Backend File(s) |
|---------|-----------------|-----------------|
| **Displaying news** | NewsCard.tsx, NewsGrid.tsx | news.py, news_service.py |
| **AI Summary** | NewsCard.tsx (Summary modal) | summary.py, summarizer.py, text_utils.py |
| **Sentiment badges** | SentimentBadge.tsx | sentiments.py, sentiment_ml.py |
| **Bookmarking articles** | NewsCard.tsx (toggleBookmark) | bookmarks.py, bookmark.py (model) |
| **User authentication** | App.tsx (Clerk setup) | auth.py (token validation) |
| **Caching strategy** | news.service.ts (requests) | cache.py, gnews_counter.py |
| **External API (GNews)** | news.service.ts | news_service.py, gnews_counter.py |
| **ML model loading** | (frontend calls API) | sentiment_ml.py (startup preload) |
| **Database persistence** | (user actions trigger saves) | database.py, all models |

---

## 📊 Data Flow Example: User Searches "Technology"

```
STEP 1: Frontend
  └─ User clicks "Technology" in Sidebar
  └─ Home.tsx → setState(topic: "technology")
  └─ Triggers newsService.getNewsByTopic("technology")

STEP 2: API Call
  └─ axios.get("/api/news/topic/technology") [from news.service.ts]
  └─ Includes Bearer token in header

STEP 3: Backend Router (news.py)
  └─ POST /api/news/topic/technology
  └─ validate_token() confirms user session

STEP 4: Cache Check (cache.py)
  └─ Check Redis for "gnews:technology"
  └─ If found: return cached results → Frontend

STEP 5: Cache Miss → API Fetch (news_service.py)
  └─ GNewsCounter.check_limit() → "8/100 hits used"
  └─ httpx.AsyncClient.get(GNews API) + params
  └─ Parse 20 articles + normalize IDs

STEP 6: Enrichment (sentiment_ml.py)
  └─ For each article:
    ├─ Check Redis for "sentiment:{md5(title+desc+content)}"
    ├─ If miss: load HF model, run inference
    ├─ Cache result in Redis
    └─ Attach { label, confidence } to article

STEP 7: Store & Respond (cache.py)
  └─ Cache full articles in Redis under "gnews:technology" (TTL: 900s)
  └─ GNewsCounter.increment_hit() → now 9/100
  └─ Return HTTP 200 with articles + sentiment

STEP 8: Frontend Render (NewsGrid.tsx)
  └─ Receive articles with { sentiment, title, url, ... }
  └─ Map articles → NewsCard components
  └─ Each card shows:
    ├─ Image + title + description
    ├─ Sentiment badge (Positive/Neutral/Negative + score)
    ├─ Bookmark & Read-Later buttons
    └─ "AI Summary" button (on-demand)

STEP 9: User clicks "AI Summary"
  └─ NewsCard.tsx → handleSummary()
  └─ POST /api/summary/ { url, content, description }

STEP 10: Backend Summary Router (summary.py)
  └─ Check Redis cache "summary:{md5(url)}"
  └─ If miss:
    ├─ text_utils.extract_article_text(url) [httpx + BeautifulSoup]
    ├─ TextSummarizer.summarize(text) [TF-IDF]
    ├─ Cache result in Redis
  └─ Return { summary, source, is_fallback }

STEP 11: Frontend Modal
  └─ Display summary in newspaper-style modal
  └─ User can share, bookmark, or close
```

---

## 🔐 Security & Access Control Points

```
Authentication (Clerk)
  ├─ Frontend: Clerk SDK manages user session
  ├─ setAuthToken() → stores Bearer token
  └─ API: every POST/PUT/DELETE includes Authorization header

Backend Validation
  ├─ TokenVal middleware (auth.py) verifies JWT signature
  ├─ Extracts user_id from token
  └─ Attaches to request context (e.g., for bookmarks)

Authorization (TODO: Enhance)
  ├─ Public routes: GET /api/news/* (no auth required)
  ├─ Protected routes: POST /api/bookmarks (user_id from token)
  ├─ Admin routes: POST /api/news/admin/reset-hits (role check needed)
  └─ Recommend: Add RBAC middleware + role column to user metadata (Mongo)
```

---

## 🚀 Deployment Architecture

For Docker/K8s deployments:

```
Docker Images:
├── backend-api:latest
│   ├── Base: python:3.11-slim
│   ├── Entrypoint: uvicorn app.main:app --host 0.0.0.0 --port 8000
│   ├── Depends on: MONGO_URI, REDIS_URL (env vars)
│   └── Port: 8000
│
├── frontend-web:latest
│   ├── Build stage: node:18 + npm install + npm run build
│   ├── Serve stage: nginx serving dist/
│   ├── Healthcheck: GET / → 200
│   └── Port: 3000

External Services:
├── Redis: redis:7-alpine (localhost:6379 or cloud URL)
└── MongoDB: mongo:6 (localhost:27017 or cloud URL)

Environment Variables:
├── Backend:
│   ├── MONGO_URI
│   ├── REDIS_URL
│   ├── GNEWS_API_KEY
│   └── HOST, PORT
└── Frontend:
    ├── VITE_API_URL (backend endpoint)
    └── VITE_CLERK_PUBLISHABLE_KEY
```

---

## 📝 Quick Reference

### To understand a feature, follow these steps:

1. **Read the Mermaid diagrams above** to see high-level architecture
2. **Check `Diagram 2: Request Flow`** to see step-by-step execution
3. **Reference `Diagram 3: Component Interaction`** to see which modules talk
4. **Open the actual files listed in the "Key Files" table**
5. **Cross-reference `FOLDER_STRUCTURE.md`** for exact paths and responsibilities

### Example: "How does sentiment analysis work?"
1. Look at Diagram 3 → find `SentimentML` component
2. Look at Diagram 2 → see sentiment inference in Flow 1
3. Check "Key Files" table → `backend/app/services/sentiment_ml.py`
4. Open that file and read the `SentimentService.analyze_article()` method
5. Follow the cache check → HF model call → result storage flow

---

## 🎯 Presentation Tips

- **For architects:** Show Diagram 1 (System Architecture) + Diagram 3 (Component Interaction)
- **For developers:** Show Diagram 2 (Request Flows) + component interaction + actual code (files listed)
- **For stakeholders:** Show Diagram 1 + explain business value (reduced read time, sentiment badges, etc.)
- **For QA/testing:** Show Diagram 2 (flows) to understand all scenarios to test

All diagrams are now available in this document and have been rendered as Mermaid visualizations!
