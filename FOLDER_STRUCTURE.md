# NewsAura - Complete Folder Structure & Organization

## Project Root: `D:\NEWSAG`

```
NEWSAG/
│
├── 📄 Documentation Files (Root)
│   ├── API_CHANGES.md                         # API enhancement tracking
│   ├── AUTH_QUICK_START.md                    # Quick Clerk auth setup
│   ├── AUTHENTICATION_GUIDE.md                # Full auth documentation
│   ├── AUTHENTICATION_IMPLEMENTATION.md       # Auth implementation details
│   ├── BEFORE_AND_AFTER.md                    # Migration/refactor comparisons
│   ├── CLERK_SETUP.md                         # Clerk configuration guide
│   ├── COMPLETION_SUMMARY.md                  # Project completion status
│   ├── FEATURES_FIXED.md                      # Bug fixes and feature toggles
│   ├── FILE_SUMMARY.md                        # File inventory
│   ├── FIXES_APPLIED.md                       # Applied fixes log
│   ├── GNEWS_HIT_COUNTER.md                   # Hit counter implementation
│   ├── GNEWS_INTEGRATION_GUIDE.md             # GNews API integration
│   ├── HIT_COUNTER_SUMMARY.md                 # Hit counter summary
│   ├── IMPLEMENTATION_DETAILS.md              # Implementation notes
│   ├── INTEGRATION_SUMMARY.md                 # Integration summary
│   ├── MIGRATION_SUMMARY.md                   # Migration tracking
│   ├── ML_SENTIMENT_IMPLEMENTATION.md         # ML sentiment details
│   ├── ML_SENTIMENT_MIGRATION.md              # ML migration notes
│   ├── ML_SENTIMENT_SUMMARY.md                # ML summary
│   ├── QUICK_REFERENCE.md                     # Quick command reference
│   ├── README_GNEWS.md                        # GNews readme
│   ├── REDIS_DEPLOYMENT.md                    # Redis setup
│   ├── REDIS_MIGRATION.md                     # Redis migration
│   ├── REDIS_VERIFICATION.md                  # Redis verification
│   ├── SUMMARY_FALLBACK_STRATEGY.md           # Summary fallback logic
│   ├── TESTING_GUIDE.md                       # Testing documentation
│   ├── FOLDER_STRUCTURE.md                    # THIS FILE
│   └── diagnose.py                            # System diagnostics script
│
├──── 🔧 BACKEND (Python FastAPI)
│   │
│   ├── backend/
│   │   ├── README.md                          # Backend overview
│   │   ├── requirements.txt                   # Python dependencies
│   │   │
│   │   └── app/
│   │       ├── __pycache__/                   # Python compiled cache
│   │       ├── main.py                        # 🌟 FastAPI entry point
│   │       │                                   # - App initialization
│   │       │                                   # - CORS middleware setup
│   │       │                                   # - Router registration
│   │       │                                   # - Startup/shutdown events
│   │       │
│   │       ├── 🗂️ core/                       # Core configuration & utilities
│   │       │   ├── __pycache__/
│   │       │   ├── auth.py                    # Authentication utilities
│   │       │   ├── cache.py                   # ⭐ Redis client & helpers
│   │       │   │                              # - get_from_cache()
│   │       │   │                              # - set_in_cache()
│   │       │   │                              # - clear_pattern()
│   │       │   ├── config.py                  # Configuration settings
│   │       │   │                              # - API keys (GNEWS_API_KEY)
│   │       │   │                              # - Endpoints (MONGO_URI, REDIS_URL)
│   │       │   │                              # - TTL settings
│   │       │   ├── database.py                # ⭐ MongoDB connection (Motor)
│   │       │   │                              # - Async MongoDB client
│   │       │   │                              # - Connection pooling
│   │       │   ├── gnews_counter.py           # ⭐ API rate limiting
│   │       │   │                              # - Daily hit counting
│   │       │   │                              # - Quota enforcement (100/day)
│   │       │   │                              # - Warning thresholds
│   │       │   ├── indexes.py                 # Database indexes
│   │       │   ├── logging.py                 # Logging configuration
│   │       │   └── __pycache__/
│   │       │
│   │       ├── 🗂️ models/                     # Pydantic/MongoDB data models
│   │       │   ├── __pycache__/
│   │       │   ├── base.py                    # Base model with Mongo ID
│   │       │   ├── bookmark.py                # Bookmark schema
│   │       │   ├── comment.py                 # Comment schema
│   │       │   ├── feedback.py                # Feedback schema
│   │       │   ├── read_later.py              # Read-Later schema
│   │       │   └── __pycache__/
│   │       │
│   │       ├── 🗂️ routers/                    # API endpoint handlers (routes)
│   │       │   ├── __pycache__/
│   │       │   ├── bookmarks.py               # POST /api/bookmarks (CRUD)
│   │       │   ├── comments.py                # POST /api/comments (CRUD)
│   │       │   ├── feedbacks.py               # POST /api/feedback
│   │       │   ├── news.py                    # ⭐ GET /api/news (cache-first)
│   │       │   │                              # - Trending headlines
│   │       │   │                              # - Topic-based news fetch
│   │       │   │                              # - Manual refresh & admin
│   │       │   ├── read_laters.py             # POST /api/read-later (CRUD)
│   │       │   ├── sentiments.py              # POST /api/sentiment (ML)
│   │       │   ├── summary.py                 # ⭐ POST /api/summary (NLP)
│   │       │   │                              # - Scraping fallback
│   │       │   │                              # - TF-IDF summarization
│   │       │   │                              # - Caching
│   │       │   └── __pycache__/
│   │       │
│   │       ├── 🗂️ services/                   # Business logic services
│   │       │   ├── __pycache__/
│   │       │   ├── news_service.py            # ⭐ External GNews API integration
│   │       │   │                              # - fetch_category()
│   │       │   │                              # - Article normalization
│   │       │   │                              # - ID generation (MD5)
│   │       │   ├── sentiment_ml.py            # ⭐ HuggingFace sentiment inference
│   │       │   │                              # - Model: cardiffnlp/twitter-roberta
│   │       │   │                              # - Per-text caching
│   │       │   │                              # - Lazy model loading
│   │       │   ├── summarizer.py              # ⭐ Extractive summarizer (TF-IDF)
│   │       │   │                              # - Sentence scoring with lead bias
│   │       │   │                              # - Redundancy filtering
│   │       │   │                              # - Word count constraints
│   │       │   ├── text_utils.py              # Utilities for text processing
│   │       │   │                              # - extract_article_text()
│   │       │   │                              # - httpx + BeautifulSoup scraper
│   │       │   └── __pycache__/
│   │       │
│   │       ├── 🗂️ logs/                       # Application logs
│   │       │   └── newsaura.log
│   │       │
│   │       └── __pycache__/
│   │
│   └── logs/                                   # Backend log directory
│
│
├──── 🎨 FRONTEND (React + TypeScript)
│   │
│   ├── frontend/
│   │   ├── package.json                       # NPM dependencies & scripts
│   │   ├── package.json.example                # Example env vars
│   │   ├── README.md                          # Frontend setup guide
│   │   ├── index.html                         # HTML entry point
│   │   │
│   │   ├── 📋 Config Files
│   │   ├── eslint.config.js                   # ESLint rules
│   │   ├── vite.config.ts                     # Vite build config
│   │   ├── tsconfig.json                      # TypeScript main config
│   │   ├── tsconfig.app.json                  # App-specific TS config
│   │   ├── tsconfig.node.json                 # Node-specific TS config
│   │   │
│   │   ├── 🗂️ public/                         # Static assets
│   │   │   └── favicon.ico
│   │   │
│   │   └── 🗂️ src/                            # React source code
│   │       ├── index.css                      # Global styles
│   │       ├── main.tsx                       # React app entry
│   │       ├── types.ts                       # TypeScript type definitions
│   │       │                                   # - Article, SentimentData
│   │       │                                   # - Topic, SummaryData
│   │       │
│   │       ├── 🗂️ app/                        # Application shell
│   │       │   ├── App.tsx                    # Root App component
│   │       │   │                              # - Layout structure
│   │       │   │                              # - Clerk auth integration
│   │       │   │                              # - Token sync
│   │       │   └── router.tsx                 # React Router setup
│   │       │
│   │       ├── 🗂️ components/                 # React UI components
│   │       │   ├── ProtectedRoute.tsx         # Route protection wrapper
│   │       │   │
│   │       │   ├── 🗂️ layout/                 # Layout components
│   │       │   │   ├── Navbar.tsx             # Top navigation bar
│   │       │   │   ├── Sidebar.tsx            # Left sidebar (categories)
│   │       │   │   └── Footer.tsx             # Footer
│   │       │   │
│   │       │   ├── 🗂️ news/                   # News display components
│   │       │   │   ├── NewsCard.tsx           # ⭐ Individual article card
│   │       │   │   │                          # - Grid & list layouts
│   │       │   │   │                          # - Summary modal
│   │       │   │   │                          # - Bookmark/Read-Later toggles
│   │       │   │   ├── NewsGrid.tsx           # ⭐ Grid/list container
│   │       │   │   │                          # - Responsive layout
│   │       │   │   │                          # - Loading skeletons
│   │       │   │   ├── NewsSkeleton.tsx       # Skeleton loader
│   │       │   │   ├── SentimentBadge.tsx     # Sentiment label display
│   │       │   │   ├── TrendingBulletin.tsx   # Ticker/bulletin display
│   │       │   │   └── commentSection.tsx     # Comment threads
│   │       │   │
│   │       │   └── 🗂️ ui/                     # Reusable UI components
│   │       │       ├── Button.tsx             # Styled button
│   │       │       ├── FeedbackFAB.tsx        # Feedback floating action button
│   │       │       ├── LoginRequiredModal.tsx # Auth gate modal
│   │       │       ├── Modal.tsx              # Generic modal
│   │       │       ├── Skeleton.tsx           # Skeleton placeholder
│   │       │       └── Toast.tsx              # Toast notification
│   │       │
│   │       ├── 🗂️ pages/                      # Full page components
│   │       │   ├── Bookmarks.tsx              # Saved articles page
│   │       │   ├── Home.tsx                   # Main feed page
│   │       │   ├── Login.tsx                  # Clerk login page
│   │       │   ├── Login.css                  # Login styles
│   │       │   ├── Profile.tsx                # User profile page
│   │       │   └── ReadLater.tsx              # Read-Later list page
│   │       │
│   │       ├── 🗂️ services/                   # API client services
│   │       │   ├── api.ts                     # ⭐ Axios setup (base URL, interceptors)
│   │       │   │                              # - Bearer token handling
│   │       │   │                              # - Error mapping
│   │       │   ├── news.service.ts            # ⭐ News API calls
│   │       │   │                              # - getNewsByTopic()
│   │       │   │                              # - getTrendingHeadlines()
│   │       │   │                              # - getSummary()
│   │       │   │                              # - getSentiment()
│   │       │   └── user.service.ts            # User-specific API calls
│   │       │                                   # - Bookmarks, Read-Later, Comments
│   │       │
│   │       └── 🗂️ utils/                      # Utility functions
│   │           ├── timeUtils.ts               # formatRelativeTime()
│   │           └── (other utilities)
│   │
│   └── node_modules/                          # NPM packages (gitignored)
│
│
└── 📋 PROJECT INFO
    ├── README.md                              # Top-level project guide
    └── .env (example in package.json.example)  # Environment variables
```

---

## Architecture by Layer

### 1️⃣ **Frontend Layer** (`frontend/src/`)
```
Frontend/
├── services/
│   ├── api.ts                         # Axios instance (BASE_URL, headers)
│   ├── news.service.ts                # Wrapped API calls
│   └── user.service.ts                # User CRUD
├── components/
│   ├── news/NewsCard.tsx              # Main UI card (summary modal, actions)
│   ├── news/NewsGrid.tsx              # Grid/list container
│   └── ui/*.tsx                       # Reusable UI (Modal, Toast, Button)
└── pages/*.tsx                         # Full pages (Home, Bookmarks, etc.)
```

### 2️⃣ **Backend Layer** (`backend/app/`)
```
Backend/
├── main.py                            # FastAPI app + router registration
├── core/
│   ├── config.py                      # Environment & settings
│   ├── database.py                    # MongoDB (Motor)
│   ├── cache.py                       # Redis client
│   └── gnews_counter.py               # Rate limiting logic
├── routers/                           # API endpoints
│   ├── news.py                        # GET /api/news/... (cache-first)
│   ├── summary.py                     # POST /api/summary/... (scrape+summarize)
│   ├── sentiments.py                  # POST /api/sentiment/... (ML)
│   └── bookmarks.py, comments.py      # CRUD endpoints
└── services/                          # Business logic
    ├── news_service.py                # GNews fetcher
    ├── sentiment_ml.py                # HF model inference
    ├── summarizer.py                  # TF-IDF extraction
    └── text_utils.py                  # Article scraper
```

### 3️⃣ **Data Layer**
```
Data/
├── Redis                              # articles, sentiment, summaries, hits counter
├── MongoDB                            # bookmarks, comments, read_later
└── External APIs
    ├── GNews.io                       # news source
    └── Article Pages                 # scraping targets
```

---

## Key File Responsibilities

| File | Purpose | Key Functions |
|------|---------|---------------|
| `backend/app/main.py` | FastAPI app initialization | `startup_event()`, `shutdown_event()`, router registration |
| `backend/app/core/config.py` | Configuration (env vars) | `GNEWS_API_KEY`, `MONGO_URI`, `REDIS_URL`, `CACHE_TTL_NEWS` |
| `backend/app/core/cache.py` | Redis wrapper | `get_from_cache()`, `set_in_cache()`, `delete_from_cache()` |
| `backend/app/core/gnews_counter.py` | Rate limiting | `check_limit()`, `increment_hit()`, `get_hit_status()` |
| `backend/app/services/news_service.py` | GNews API client | `fetch_category(category)` |
| `backend/app/services/sentiment_ml.py` | Sentiment inference | `analyze_article(title, desc, content)`, model preloading |
| `backend/app/services/summarizer.py` | Extractive summarization | `summarize(text, min_words, max_sentences)` |
| `backend/app/services/text_utils.py` | Article scraping | `extract_article_text(url)` (httpx + BeautifulSoup) |
| `backend/app/routers/news.py` | News endpoints | `GET /api/news/topic/{topic}`, `/api/news/trending/headlines` |
| `backend/app/routers/summary.py` | Summary endpoint | `POST /api/summary/` (cache check → scrape → summarize) |
| `frontend/src/services/api.ts` | Axios config | `BASE_URL`, `setAuthToken()`, error mapping |
| `frontend/src/services/news.service.ts` | API wrapper | `getNewsByTopic()`, `getSummary()`, `getSentiment()` |
| `frontend/src/components/news/NewsCard.tsx` | Article card UI | Grid/list layouts, summary modal, bookmarks toggle |
| `frontend/src/components/news/NewsGrid.tsx` | Grid container | Responsive layout, skeleton loaders |

---

## Caches & Data Structures

### Redis Keys (ephemeral, TTL-based)
```
gnews:{topic}               → Array of enriched articles (TTL: 900s)
gnews:trending:headlines    → Array of trending headlines (TTL: 600s)
sentiment:{md5(text)}       → { label, confidence, model } (TTL: 900s)
summary:{md5(url)}          → { summary, source, is_fallback } (TTL: 900s)
gnews:hits:YYYY-MM-DD       → int (daily hit count, TTL: 86400s)
```

### MongoDB Collections
```
bookmarks                   → { user_id, article_id, title, url, image_url, ... }
comments                    → { article_id, user_id, text, created_at, ... }
read_later                  → { user_id, article_id, title, url, ... }
feedbacks                   → { user_id, message, created_at, ... }
```

---

## Dependency Flow

```
Frontend (React)
    ↓ axios
Backend Routers (FastAPI)
    ↓
Services Layer
    ├─→ GNewsService → GNews API (httpx)
    ├─→ SentimentService → HuggingFace (transformers)
    ├─→ TextSummarizer → scikit-learn (TF-IDF)
    ├─→ text_utils → Article pages (httpx + BeautifulSoup)
    └─→ Caching layer (Redis)
         ├─→ Redis (redis.asyncio)
         ├─→ MongoDB (Motor)
         └─→ Rate limiter (GNewsCounter)
```

---

## Environment Variables Required

```bash
# Backend (.env)
MONGO_URI=mongodb+srv://user:pass@cluster.mongodb.net/db
REDIS_URL=redis://localhost:6379
GNEWS_API_KEY=your_gnews_api_key_here
HOST=127.0.0.1
PORT=8000

# Frontend (.env.local)
VITE_API_URL=http://localhost:8000
VITE_CLERK_PUBLISHABLE_KEY=clerk_pub_key_here
```

---

## Build & Deployment Folder Structure (Docker)

```
Docker Image
├── Dockerfile (Python 3.11-slim base)
├── backend/
│   ├── app/
│   ├── requirements.txt (installed via pip)
│   └── logs/
└── ENTRYPOINT: uvicorn app.main:app --host 0.0.0.0 --port 8000
```

For frontend:
```
Docker Image
├── Dockerfile (node:18 base → build → nginx)
├── frontend/
│   ├── src/
│   └── vite.config.ts
├── ENTRYPOINT: serve dist/ on port 3000
```

---

## Quick Navigation

- **To add a new news category:** edit `ALLOWED_CATEGORIES` in `backend/app/services/news_service.py`
- **To change cache TTL:** edit `CACHE_TTL_NEWS` in `backend/app/core/config.py`
- **To change GNews quota:** edit `MAX_HITS_PER_DAY` in `backend/app/core/gnews_counter.py`
- **To add a new API route:** create file in `backend/app/routers/` and import in `main.py`
- **To add a new MongoDB model:** create class in `backend/app/models/`, inherit from `MongoBase`
- **To add a new UI component:** create `.tsx` file in `frontend/src/components/` and export from sibling `index.ts` (if using barrels)
