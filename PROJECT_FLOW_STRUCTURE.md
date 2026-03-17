# NewsAura - Project Flow Structure

## 📋 Table of Contents
1. [Overall Application Flow](#overall-application-flow)
2. [User Journey Flows](#user-journey-flows)
3. [Data Flow Pipeline](#data-flow-pipeline)
4. [Request-Response Cycle](#request-response-cycle)
5. [Component Communication](#component-communication)
6. [Cache & Persistence Strategy](#cache--persistence-strategy)
7. [Error Handling & Fallbacks](#error-handling--fallbacks)

---

## Overall Application Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                     USER OPENS NEWSAURA                             │
└────────────────────────┬────────────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │ Frontend │
                    │  Ready?  │
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐    ┌──────▼──────┐   ┌────▼────┐
   │ No Auth │    │ Auth Pending │   │ Authed  │
   │ (Public)│    │ (Clerk SDK)  │   │ (Token) │
   └────┬────┘    └──────┬───────┘   └────┬────┘
        │                │                │
        └───────────┬────────────────┬────┘
                    │
            ┌───────▼──────────┐
            │ Load Home Page   │
            │ Fetch Headlines  │
            │ Display Trending │
            └────────┬─────────┘
                     │
            ┌────────▼─────────┐
            │  User Interacts  │
            │ - Click Category │
            │ - Open Summary   │
            │ - Bookmark      │
            └────────┬─────────┘
                     │
         ┌───────────┴──────────┐
         │                      │
    ┌────▼────┐           ┌────▼────┐
    │ GET      │           │ POST     │
    │ /api/... │           │ /api/... │
    └────┬─────┘           └────┬─────┘
         │                      │
         ▼                      ▼
    [Backend Processing]  [Backend Writes]
         │                      │
    ┌────▼──────────────────────▼──────┐
    │   Redis Cache + ML Enrichment     │
    │   GNews API + Scraping            │
    │   MongoDB Persistence             │
    └────┬──────────────────────────────┘
         │
    ┌────▼────────────────────────────┐
    │  Response JSON                   │
    │  (articles + sentiment + meta)   │
    └────┬─────────────────────────────┘
         │
    ┌────▼────────────────────┐
    │   Frontend Renders       │
    │   Updated UI            │
    └─────────────────────────┘
```

---

## User Journey Flows

### Flow 1: Browse News (Most Common)

```
START
  │
  ├─► User lands on Home page
  │    └─► Clerk checks session (if logged in)
  │    └─► Frontend loads
  │
  ├─► User clicks "Technology" category
  │    └─► Frontend: newsService.getNewsByTopic("technology")
  │    └─► Axios: POST to http://localhost:8000/api/news/topic/technology
  │
  ├─► Backend receives request
  │    ├─► Validate Bearer token (if protected route)
  │    ├─► Hit routers/news.py → GET /api/news/topic/technology
  │    ├─► Check Redis cache "gnews:technology"
  │    │
  │    └─► DECISION: Cache hit or miss?
  │         │
  │         ├─► CACHE HIT ✓
  │         │    └─► Return cached articles + sentiment
  │         │    └─► HTTP 200 → Frontend
  │         │
  │         └─► CACHE MISS ✗
  │              ├─► Check daily quota: GNewsCounter.check_limit()
  │              │    └─► Query Redis "gnews:hits:2026-02-06"
  │              │    └─► if >= 100: return 429 Too Many Requests
  │              │
  │              ├─► Call GNews API
  │              │    └─► httpx.AsyncClient.get(GNews endpoint)
  │              │    └─► Normalize 20 articles (id, title, url, etc.)
  │              │
  │              ├─► Enrich with Sentiment (for each article)
  │              │    ├─► Check Redis "sentiment:{md5(text)}"
  │              │    ├─► if miss: Load HF model → Infer → Cache result
  │              │    └─► Attach sentiment to article
  │              │
  │              ├─► Store in Redis "gnews:technology" (TTL: 900s)
  │              ├─► Increment hit counter: gnews:hits:2026-02-06 += 1
  │              └─► Return enriched articles → Frontend
  │
  ├─► Frontend receives JSON response
  │    ├─► Map articles to NewsCard components
  │    ├─► Render NewsGrid (responsive grid/list layout)
  │    ├─► Display sentiment badges, source, publish time
  │    └─► Show skeleton loaders if still loading
  │
  ├─► User sees articles with:
  │    ├─ Article image + title
  │    ├─ Source + publish date
  │    ├─ Sentiment badge (Positive/Neutral/Negative)
  │    ├─ Bookmark & Read-Later buttons
  │    └─ AI Summary button
  │
  └─► Ready for next interaction
```

### Flow 2: Generate AI Summary

```
START (User clicks "✨ AI Summary" on article)
  │
  ├─► Frontend: newsService.getSummary(url, content, description)
  │    └─► POST /api/summary/ with Bearer token
  │
  ├─► Backend: routers/summary.py → POST /api/summary/
  │    ├─► Validate token
  │    ├─► Extract params: { url, content, description }
  │    │
  │    ├─► Check Redis cache: "summary:{md5(url)}"
  │    │
  │    └─► DECISION: Cached or not?
  │         │
  │         ├─► CACHE HIT ✓
  │         │    └─► Return { summary, source: "cache", is_fallback: false }
  │         │    └─► HTTP 200 → Frontend
  │         │
  │         └─► CACHE MISS ✗
  │              │
  │              ├─► PRIMARY: Try full-text scraping
  │              │    ├─► text_utils.extract_article_text(url)
  │              │    ├─► httpx → fetch URL
  │              │    ├─► BeautifulSoup → parse HTML
  │              │    ├─► Extract <p> tags + clean
  │              │    └─► Return full article text
  │              │
  │              ├─► DECISION: Sufficient text (>200 words)?
  │              │    │
  │              │    ├─► YES: Run TF-IDF Summarizer
  │              │    │    ├─► TextSummarizer.summarize(text)
  │              │    │    ├─► Vectorize sentences via TF-IDF
  │              │    │    ├─► Score with lead-bias (early sentences weighted higher)
  │              │    │    ├─► Filter redundant sentences (>60% overlap)
  │              │    │    ├─► Select top sentences to reach 100-120 words
  │              │    │    └─► Return extractive summary
  │              │    │
  │              │    └─► NO: Fallback to GNews description
  │              │         ├─► if content available: use it
  │              │         ├─► elif description available: use it
  │              │         └─► else: use placeholder message
  │              │
  │              ├─► Cache result in Redis "summary:{md5(url)}" (TTL: 900s)
  │              └─► Return { summary, source, is_fallback }
  │
  ├─► Frontend receives response
  │    ├─► Set modal isOpen = true
  │    ├─► Display summary in newspaper-style modal
  │    ├─► Show spinner if still loading
  │    └─► Show error if failed
  │
  └─► User reads summary or closes modal
```

### Flow 3: Save Article (Bookmark / Read-Later)

```
START (User clicks Bookmark or Read-Later icon)
  │
  ├─► Frontend: toggleBookmark() or toggleReadLater()
  │    ├─► userService.addBookmark(article) or removeBookmark(url)
  │    ├─► POST /api/bookmarks/ with Bearer token
  │    └─► Payload: { article_id, title, source, url, image_url }
  │
  ├─► Backend: routers/bookmarks.py → POST /api/bookmarks/
  │    ├─► Validate Bearer token → Extract user_id
  │    ├─► Parse request body
  │    │
  │    ├─► DECIDE: Add or Remove?
  │    │    │
  │    │    ├─► ADD:
  │    │    │    ├─► Create BookmarkModel instance
  │    │    │    ├─► db.bookmarks.insert_one(
  │    │    │    │    {
  │    │    │    │      user_id: "clerk_user_id",
  │    │    │    │      article_id: "article_hash",
  │    │    │    │      title: "...",
  │    │    │    │      url: "...",
  │    │    │    │      created_at: datetime.utcnow()
  │    │    │    │    }
  │    │    │    │   )
  │    │    │    └─► HTTP 201 Created
  │    │    │
  │    │    └─► REMOVE:
  │    │         ├─► db.bookmarks.delete_one({ user_id, article_id })
  │    │         └─► HTTP 204 No Content
  │    │
  │    └─► MongoDB persists the change
  │
  ├─► Frontend receives response
  │    ├─► Update isBookmarked state
  │    ├─► Toggle icon style (filled or outline)
  │    └─► Show success toast
  │
  └─► User's bookmarks sync across sessions
```

### Flow 4: View Bookmarks Page

```
START (User clicks "Bookmarks" in sidebar)
  │
  ├─► React Router navigates to /bookmarks
  │    └─► Bookmarks.tsx component mounts
  │
  ├─► useEffect() triggers on mount
  │    └─► userService.getBookmarks() 
  │    └─► GET /api/bookmarks/ with Bearer token
  │
  ├─► Backend: routers/bookmarks.py → GET /api/bookmarks/
  │    ├─► Extract user_id from token
  │    ├─► Query MongoDB: db.bookmarks.find({ user_id })
  │    ├─► Convert documents to JSON
  │    └─► Return array of bookmarked articles
  │
  ├─► Frontend receives array
  │    ├─► setState(bookmarks: Article[])
  │    ├─► Pass to NewsGrid component
  │    └─► Render as cards (grid or list view)
  │
  └─► User sees all saved articles
       ├─ Can click to view summary
       ├─ Can remove from bookmarks
       └─ Can sort/filter
```

---

## Data Flow Pipeline

### Request → Response Pipeline

```
┌──────────────────────────────────────────────────────────────────┐
│ 1. FRONTEND INITIATES REQUEST                                    │
├──────────────────────────────────────────────────────────────────┤
│ Action: User clicks category or button                           │
│ Code: newsService.getNewsByTopic("technology")                   │
│ Output: Axios HTTP request                                       │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 2. NETWORK LAYER                                                 │
├──────────────────────────────────────────────────────────────────┤
│ Method: GET /api/news/topic/technology                           │
│ Headers: Authorization: Bearer <clerk_token>                     │
│ Timeout: 20000ms (configured in api.ts)                          │
│ Base URL: http://localhost:8000 (VITE_API_URL)                   │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 3. FASTAPI RECEIVES REQUEST                                      │
├──────────────────────────────────────────────────────────────────┤
│ Middleware: CORS verification                                    │
│ Handler: routers/news.py → @router.get("/topic/{topic}")         │
│ Dependency: Token validation (Bearer token verified)             │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 4. SERVICE LAYER - CACHE CHECK                                   │
├──────────────────────────────────────────────────────────────────┤
│ Cache Key: "gnews:technology"                                    │
│ Code: await get_from_cache("gnews:technology")                   │
│                                                                  │
│ ┌──────────────────────┬───────────────────────────────────┐     │
│ │ CACHE HIT            │ CACHE MISS                        │     │
│ ├──────────────────────┼───────────────────────────────────┤     │
│ │ ✓ Found in Redis     │ ✗ Not in Redis                    │     │
│ │ → Return directly    │ → Continue to API fetch           │     │
│ │ → Skip ML (already   │                                   │     │
│ │   computed)          │                                   │     │
│ │ → Fast (~5ms)        │                                   │     │
│ └──────────────────────┴───────────────────────────────────┘     │
└────────────────────────────┬─────────────────────────────────────┘
                             │
                    (If CACHE MISS, continue)
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 5. QUOTA ENFORCEMENT                                             │
├──────────────────────────────────────────────────────────────────┤
│ Check: GNewsCounter.check_limit()                                │
│ Query: Redis "gnews:hits:2026-02-06" (today's date)              │
│                                                                  │
│ ├─► if >= 100: Reject request (HTTP 429 Too Many Requests)      │
│ └─► if < 100: Proceed to API fetch                               │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 6. EXTERNAL API CALL (GNews)                                     │
├──────────────────────────────────────────────────────────────────┤
│ Service: GNewsService.fetch_category("technology")               │
│ Code: httpx.AsyncClient.get(                                      │
│         "https://gnews.io/api/v4/top-headlines",                 │
│         params={...}                                              │
│       )                                                           │
│ Params:                                                          │
│   - category: "technology"                                       │
│   - country: "in" (India)                                        │
│   - lang: "en"                                                   │
│   - max: 20                                                      │
│   - apikey: GNEWS_API_KEY                                        │
│ Response: JSON array of 20 articles (raw from GNews)             │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 7. NORMALIZE ARTICLES                                            │
├──────────────────────────────────────────────────────────────────┤
│ For each article in GNews response:                              │
│   ├─► Extract: title, description, content, image, url, etc.    │
│   ├─► Generate ID: md5(url) → deterministic hash                │
│   ├─► Normalize fields (handle nulls, truncate)                  │
│   └─► Create standardized article object                        │
│                                                                  │
│ Output: Array of 20 normalized articles                          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 8. ML ENRICHMENT - SENTIMENT ANALYSIS                            │
├──────────────────────────────────────────────────────────────────┤
│ For each normalized article:                                     │
│                                                                  │
│   ┌─► SentimentService.analyze_article(                          │
│   │    title=article.title,                                     │
│   │    description=article.description,                         │
│   │    content=article.content                                  │
│   │   )                                                          │
│   │                                                              │
│   ├─► Combined text = title + " " + description + " " + content │
│   ├─► Cache key: "sentiment:{md5(combined_text)}"               │
│   │                                                              │
│   ├─► Check Redis for cached sentiment                          │
│   │    ├─ HIT: Return cached { label, confidence }             │
│   │    └─ MISS:                                                │
│   │         ├─► Load HF model (singleton, one-time load)        │
│   │         ├─► Run pipeline: combined_text → Model             │
│   │         ├─► Model outputs: POSITIVE/NEUTRAL/NEGATIVE        │
│   │         ├─► Normalize: "Positive" / "Neutral" / "Negative" │
│   │         ├─► Extract confidence score (0.0-1.0)              │
│   │         └─► Cache in Redis (TTL: 900s)                      │
│   │                                                              │
│   └─► Attach to article: article.sentiment = {label, confidence}│
│                                                                  │
│ Output: Articles with sentiment metadata                         │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 9. CACHE RESULTS                                                 │
├──────────────────────────────────────────────────────────────────┤
│ Store full articles in Redis:                                    │
│   Key: "gnews:technology"                                        │
│   Value: JSON array of articles (with sentiment)                 │
│   TTL: 900 seconds (15 minutes)                                  │
│                                                                  │
│ Increment daily hit counter:                                     │
│   Key: "gnews:hits:2026-02-06"                                   │
│   Operation: increment by 1 (now 9/100)                          │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 10. SERIALIZE & RETURN RESPONSE                                  │
├──────────────────────────────────────────────────────────────────┤
│ HTTP 200 OK                                                      │
│ Content-Type: application/json                                   │
│ Body:                                                            │
│ {                                                                │
│   "source": "api",          ← Indicates fresh data               │
│   "count": 20,              ← Number of articles                │
│   "articles": [             ← Array of enriched articles         │
│     {                                                            │
│       "id": "a1b2c3d4...",  ← MD5 hash of URL                   │
│       "title": "...",                                            │
│       "description": "...",                                      │
│       "content": "...",                                          │
│       "url": "...",                                              │
│       "image_url": "...",                                        │
│       "source": "...",                                           │
│       "published_at": "2026-02-06T10:30:00Z",                   │
│       "category": "technology",                                  │
│       "sentiment": {        ← ML Output!                        │
│         "label": "Positive",                                     │
│         "confidence": 0.89,                                      │
│         "model": "roberta-news"                                  │
│       }                                                          │
│     },                                                           │
│     ...                                                          │
│   ],                                                             │
│   "hits": {                 ← Quota info                        │
│     "today_hits": 9,                                             │
│     "remaining_hits": 91,                                        │
│     "warning": false,                                            │
│     "max_hits": 100                                              │
│   }                                                              │
│ }                                                                │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 11. FRONTEND RECEIVES RESPONSE                                   │
├──────────────────────────────────────────────────────────────────┤
│ news.service.ts handles response:                                │
│   ├─► Extract articles array                                     │
│   ├─► Store in component state: articles: Article[]              │
│   ├─► Handle errors via getErrorMessage()                        │
│   └─► Show toast notification if error                           │
└────────────────────────────┬─────────────────────────────────────┘
                             │
┌────────────────────────────▼─────────────────────────────────────┐
│ 12. REACT RENDERS COMPONENTS                                     │
├──────────────────────────────────────────────────────────────────┤
│ Home.tsx:                                                        │
│   ├─► Pass articles[] to NewsGrid                                │
│   └─► Pass isLoading state                                       │
│                                                                  │
│ NewsGrid.tsx:                                                    │
│   ├─► Map articles to NewsCard components                        │
│   ├─► Render grid layout (responsive columns)                    │
│   └─► Show skeleton loaders if still loading                     │
│                                                                  │
│ NewsCard.tsx (for each article):                                 │
│   ├─► Display image                                              │
│   ├─► Display title as link (opens article in new tab)           │
│   ├─► Display description / category / publish date              │
│   ├─► Show SentimentBadge with label + confidence                │
│   ├─► Show bookmark & read-later buttons                         │
│   └─► Show "✨ AI Summary" button                                 │
│                                                                  │
│ SentimentBadge.tsx:                                              │
│   └─► Render colored pill badge with label                       │
│         ├─ GREEN for Positive                                    │
│         ├─ GRAY for Neutral                                      │
│         └─ RED for Negative                                      │
│                                                                  │
│ Result: Fully rendered news feed visible to user                 │
└──────────────────────────────────────────────────────────────────┘
```

---

## Request-Response Cycle

### 1. GET News Request Cycle

```
REQUEST:
┌────────────────────────────────────────┐
│ GET /api/news/topic/technology          │
│ Host: localhost:8000                    │
│ Authorization: Bearer eyJhbGc...        │
│ Content-Type: application/json          │
│ Accept: application/json                │
└────────────────────────────────────────┘

PROCESSING TIME BREAKDOWN:
├─ Cache lookup: ~5ms (if HIT)
├─ GNews API call: ~500ms (if MISS)
├─ ML sentiment (per-article): ~50ms × 20 articles (if not cached)
├─ Redis write: ~10ms
└─ Total: 5ms (cached) OR ~1500ms (fresh)

RESPONSE:
┌────────────────────────────────────────┐
│ HTTP/1.1 200 OK                         │
│ Content-Type: application/json          │
│ Content-Length: 45320                   │
│ Cache-Control: no-cache                 │
│ Date: Fri, 06 Feb 2026 10:30:45 GMT    │
│                                         │
│ {                                       │
│   "source": "api",                      │
│   "count": 20,                          │
│   "articles": [...],                    │
│   "hits": {...}                         │
│ }                                       │
└────────────────────────────────────────┘
```

### 2. POST Summary Request Cycle

```
REQUEST:
┌────────────────────────────────────────┐
│ POST /api/summary/                      │
│ Host: localhost:8000                    │
│ Authorization: Bearer eyJhbGc...        │
│ Content-Type: application/json          │
│                                         │
│ {                                       │
│   "url": "https://example.com/news",   │
│   "content": "Full article text...",   │
│   "description": "Short description..." │
│ }                                       │
└────────────────────────────────────────┘

PROCESSING TIME BREAKDOWN:
├─ Cache lookup: ~5ms (if HIT)
├─ Article scraping: ~2000ms (if required)
├─ TF-IDF summarization: ~100ms
├─ Redis write: ~10ms
└─ Total: 5ms (cached) OR ~2100ms (fresh)

RESPONSE:
┌────────────────────────────────────────┐
│ HTTP/1.1 200 OK                         │
│ Content-Type: application/json          │
│                                         │
│ {                                       │
│   "summary": "This article discusses...", │
│   "source": "generated",                │
│   "is_fallback": false                  │
│ }                                       │
└────────────────────────────────────────┘
```

### 3. POST Bookmark Request Cycle

```
REQUEST:
┌────────────────────────────────────────┐
│ POST /api/bookmarks/                    │
│ Host: localhost:8000                    │
│ Authorization: Bearer eyJhbGc...        │
│ Content-Type: application/json          │
│                                         │
│ {                                       │
│   "article_id": "a1b2c3d4...",         │
│   "title": "Breaking News...",         │
│   "source": "TechNews",                 │
│   "url": "https://...",                │
│   "image_url": "https://..."           │
│ }                                       │
└────────────────────────────────────────┘

PROCESSING TIME BREAKDOWN:
├─ Token validation: ~10ms
├─ MongoDB insert: ~20ms
└─ Total: ~30ms

RESPONSE:
┌────────────────────────────────────────┐
│ HTTP/1.1 201 Created                    │
│ Content-Type: application/json          │
│ Location: /api/bookmarks/<bookmark_id> │
│                                         │
│ {                                       │
│   "_id": "507f1f77bcf86cd799439011",   │
│   "user_id": "user_clerk_123",         │
│   "article_id": "a1b2c3d4...",         │
│   "created_at": "2026-02-06T10:30:00", │
│   "status": "success"                   │
│ }                                       │
└────────────────────────────────────────┘
```

---

## Component Communication

### Frontend Component Hierarchy & Data Flow

```
┌─────────────────────────────────────────────────────────┐
│                      App.tsx                            │
│  ├─ Clerk Auth Setup                                   │
│  ├─ Token Sync                                         │
│  └─ Router Provider                                    │
└────────────────┬────────────────────────────────────────┘
                 │
         ┌───────┴──────────┐
         │                  │
    ┌────▼────┐        ┌────▼──────┐
    │ Navbar  │        │ Sidebar   │
    ├─────────┤        ├───────────┤
    │ Logo    │        │ Categories│
    │ Theme   │        └───────────┘
    │ Profile │
    └────┬────┘
         │
    ┌────▼──────────────────────────┐
    │       AppRouter               │
    ├───────────────────────────────┤
    │ ProtectedRoute wraps pages    │
    └────┬──────────────────────────┘
         │
    ┌────┴─────────────────────────────────────────┐
    │                                               │
 ┌──▼─────┐  ┌──────────┐  ┌────────┐  ┌────────┐
 │  Home  │  │ Bookmarks│  │ ReadLater│ │ Login │
 └──┬─────┘  └──┬───────┘  └────────┘  └────────┘
    │           │
    └────┬──────┘
         │
    ┌────▼──────────────┐
    │   useEffect()     │
    │ Fetch data on     │
    │ mount/change      │
    └────┬──────────────┘
         │
    ┌────▼──────────┐
    │ newsService   │
    │ userService   │
    └────┬──────────┘
         │
    ┌────▼──────────┐
    │    api.ts     │
    │  (Axios)      │
    └────┬──────────┘
         │
    ┌────▼───────────────┐
    │  Backend API       │
    │  (FastAPI)         │
    └───────────────────┘
         │
    ┌────▼─────────────────────────┐
    │   NewsGrid.tsx              │
    │                             │
    │   ├─ Props: articles,       │
    │   │ isLoading, viewType      │
    │   │                          │
    │   └─► Map to NewsCard array  │
    └────┬────────────────────────┘
         │
    ┌────▼──────────────────────┐
    │   NewsCard.tsx (×N)       │
    │                          │
    │   ├─ Props: article      │
    │   ├─ State:              │
    │   │  - isBookmarked      │
    │   │  - isInReadLater     │
    │   │  - summary           │
    │   │  - isModalOpen       │
    │   │                      │
    │   └─ Children:           │
    │      ├─ ImageSection     │
    │      ├─ ContentSection   │
    │      ├─ SentimentBadge   │
    │      ├─ ActionButtons    │
    │      └─ Modal            │
    └────────────────────────────┘
                 │
         ┌───────┴──────────┐
         │                  │
    ┌────▼──────────┐  ┌────▼──────┐
    │ SentimentBadge│  │   Modal    │
    └───────────────┘  ├───────────┤
                       │ NewsCard  │
                       │ Summary   │
                       │ Display   │
                       └───────────┘
```

### Backend Service Communication

```
routers/
├─ news.py
│  └─► GNewsService.fetch_category()
│      ├─► GNewsCounter.check_limit()
│      ├─► httpx (GNews API call)
│      └─► SentimentService.analyze_article() [parallel]
│          ├─► HF Model inference
│          └─► Redis caching
│
├─ summary.py
│  └─► text_utils.extract_article_text()
│      ├─► httpx (web scraping)
│      └─► BeautifulSoup (HTML parsing)
│  └─► TextSummarizer.summarize()
│      └─► scikit-learn TF-IDF
│
├─ sentiments.py
│  └─► SentimentService.analyze()
│      ├─► Redis cache check
│      ├─► HF Model load (lazy)
│      └─► Redis cache store
│
├─ bookmarks.py
│  └─► MongoDB.get_database()
│      └─► db.bookmarks CRUD
│
└─ comments.py
   └─► MongoDB.get_database()
       └─► db.comments CRUD
```

---

## Cache & Persistence Strategy

### Redis Cache Hierarchy (TTL-based, ephemeral)

```
┌─────────────────────────────────────────────────────────┐
│                    REDIS CACHE                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│ KEY: gnews:general                                      │
│ VALUE: [article₁, article₂, ..., article₂₀]            │
│ TTL: 900 seconds (15 minutes)                           │
│ USE: General news trending headlines                    │
│ SET BY: routers/news.py                                 │
│ GET BY: routers/news.py, trending endpoint              │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│ KEY: gnews:technology                                   │
│ VALUE: [article₁, article₂, ..., article₂₀]            │
│ TTL: 900 seconds                                        │
│ USE: Technology news feeds                              │
│ SET BY: routers/news.py on cache miss                   │
│ GET BY: routers/news.py                                 │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│ KEY: gnews:trending:headlines                           │
│ VALUE: [headline₁, headline₂, ..., headline₈]           │
│ TTL: 600 seconds (10 minutes)                           │
│ USE: Trending bulletin/ticker                           │
│ SET BY: trending headlines endpoint                     │
│ GET BY: TrendingBulletin component                      │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│ KEY: sentiment:a1b2c3d4e5f6...                          │
│ VALUE: {                                                │
│          "label": "Positive",                           │
│          "confidence": 0.89,                            │
│          "model": "roberta-news"                        │
│        }                                                │
│ TTL: 900 seconds                                        │
│ USE: Cache sentiment results per unique text            │
│ SET BY: SentimentService.analyze()                      │
│ GET BY: SentimentService.analyze() (cache-first)        │
│ KEY GEN: md5(combined_text_of_title_desc_content)       │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│ KEY: summary:b2c3d4e5f6a7...                            │
│ VALUE: {                                                │
│          "summary": "This article discusses...",       │
│          "source": "generated",                         │
│          "is_fallback": false                           │
│        }                                                │
│ TTL: 900 seconds                                        │
│ USE: Cache generated summaries                          │
│ SET BY: routers/summary.py                              │
│ GET BY: routers/summary.py (cache-first)                │
│ KEY GEN: md5(url)                                       │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│ KEY: gnews:hits:2026-02-06                              │
│ VALUE: 9 (integer count)                                │
│ TTL: 86400 seconds (24 hours, resets daily)             │
│ USE: Track daily API quota (100 requests/day)           │
│ SET BY: GNewsCounter.increment_hit()                    │
│ GET BY: GNewsCounter.check_limit()                      │
│ PATTERN: gnews:hits:YYYY-MM-DD (new key each day)       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### MongoDB Persistence (persistent, schema-flexible)

```
┌─────────────────────────────────────────────────────────┐
│                    MONGODB DATABASE                     │
├─────────────────────────────────────────────────────────┤
│ Database: newsdb (or configured via MONGO_URI)          │
│                                                          │
│ COLLECTION: bookmarks                                   │
│ ├─ Document structure:                                  │
│ │  {                                                    │
│ │    "_id": ObjectId("..."),                            │
│ │    "user_id": "clerk_user_123",                       │
│ │    "article_id": "md5_hash",                          │
│ │    "title": "Article Title",                          │
│ │    "source": "Source Name",                           │
│ │    "url": "https://example.com",                      │
│ │    "image_url": "https://...",                        │
│ │    "created_at": ISODate("2026-02-06T10:30:00Z")      │
│ │  }                                                    │
│ ├─ Indexes:                                             │
│ │  - user_id (for fast user lookups)                    │
│ │  - user_id + article_id (unique combo)                │
│ └─ Operations: INSERT (bookmark), DELETE (unbookmark),   │
│                FIND (get user's bookmarks)               │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│ COLLECTION: comments                                    │
│ ├─ Document structure:                                  │
│ │  {                                                    │
│ │    "_id": ObjectId("..."),                            │
│ │    "article_id": "md5_hash",                          │
│ │    "user_id": "clerk_user_123",                       │
│ │    "text": "User comment text",                       │
│ │    "created_at": ISODate("2026-02-06T10:30:00Z")      │
│ │  }                                                    │
│ ├─ Indexes:                                             │
│ │  - article_id (for comment threads)                   │
│ └─ Operations: INSERT (post), FIND (get thread)          │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│ COLLECTION: read_later                                  │
│ ├─ Document structure:                                  │
│ │  {                                                    │
│ │    "_id": ObjectId("..."),                            │
│ │    "user_id": "clerk_user_123",                       │
│ │    "article_id": "md5_hash",                          │
│ │    "title": "Article Title",                          │
│ │    "source": "Source Name",                           │
│ │    "url": "https://example.com",                      │
│ │    "created_at": ISODate("2026-02-06T10:30:00Z")      │
│ │  }                                                    │
│ ├─ Indexes:                                             │
│ │  - user_id                                            │
│ └─ Similar operations to bookmarks                       │
│                                                          │
│ ─────────────────────────────────────────────────────    │
│                                                          │
│ COLLECTION: feedbacks                                   │
│ ├─ Document structure:                                  │
│ │  {                                                    │
│ │    "_id": ObjectId("..."),                            │
│ │    "user_id": "clerk_user_123",                       │
│ │    "message": "User feedback text",                   │
│ │    "created_at": ISODate("2026-02-06T10:30:00Z")      │
│ │  }                                                    │
│ └─ Operations: INSERT (submit feedback)                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Cache Invalidation & Update Strategy

```
SCENARIO 1: Article Cache Expires
├─ Redis key "gnews:technology" TTL reaches 0
├─ Key auto-deleted from Redis
├─ Next request: CACHE MISS
├─ Fresh fetch from GNews API
└─ New ML sentiment computed + cached

SCENARIO 2: Manual Refresh (Admin)
├─ POST /api/news/refresh/technology
├─ Delete "gnews:technology" from Redis (manual)
├─ Delete "gnews:trending:headlines" from Redis
├─ Fresh fetch from GNews API
└─ Sentiment + cache updates

SCENARIO 3: Sentiment Model Update
├─ New HF model version deployed
├─ Restart backend app
├─ Model reloads at startup
├─ Sentiment cache (Redis) invalidated
├─ On next request: Re-compute sentiments with new model
└─ New sentiment values cached under same keys

SCENARIO 4: Full Cache Flush (Emergency)
├─ Redis FLUSHDB command
├─ All gnews:*, sentiment:*, summary:*, hits: keys deleted
├─ Next requests: Full re-computation
└─ High latency spike until cache repopulated
```

---

## Error Handling & Fallbacks

### Error Handling Flow

```
┌──────────────────────────────────────────────────────┐
│              ERROR OCCURS IN BACKEND                 │
├──────────────────────────────────────────────────────┤
│                                                      │
│ TRY:                                                 │
│ ├─► GNews API call fails (network timeout)          │
│ ├─► Article scraping fails (JavaScript-heavy page) │
│ ├─► HF model inference fails (OOM)                  │
│ └─► MongoDB connection lost                         │
│                                                      │
│ CATCH:                                               │
│ ├─► Log error to logger                             │
│ ├─► Graceful fallback (don't crash)                 │
│ └─► Return user-friendly error response             │
│                                                      │
│ RESPONSE:                                            │
│ ├─► HTTP 5xx (server error) or 4xx (client error)  │
│ └─► JSON error message to frontend                  │
│                                                      │
└──────────────────────────────────────────────────────┘

SPECIFIC FALLBACKS:

├─ GNews API fails
│  └─► Return cached articles if available
│  └─► Else 502 Bad Gateway error

├─ Article scraping fails
│  └─► Use GNews.content field
│  └─► Else use GNews.description
│  └─► Else return placeholder: "Cannot summarize..."

├─ Sentiment model fails to load at startup
│  └─► Log warning (don't block startup)
│  └─► All sentiment requests return neutral fallback

├─ MongoDB insert fails
│  └─► Return 500 error to frontend
│  └─► User sees toast: "Failed to save. Try again."

├─ Redis connection fails
│  └─► Log warning
│  └─► Skip caching, fetch fresh from API
│  └─► App continues (slower but functional)

└─ Quota limit hit (100 hits/day)
   └─► Return 429 Too Many Requests
   └─► Frontend shows: "Daily limit reached. Try tomorrow."
```

### Frontend Error Handling

```
REQUEST FAILS:
└─► news.service.ts catches error
    ├─► Call getErrorMessage(error)
    ├─► Map HTTP status to human-friendly text
    └─► Component receives error state

ERROR DISPLAY:
├─ HTTP 400: "Invalid request. Check your input."
├─ HTTP 401: "Session expired. Log in again."
├─ HTTP 403: "You don't have permission."
├─ HTTP 404: "Article not found."
├─ HTTP 429: "Too many requests. Wait a moment."
├─ HTTP 5xx: "Server error. Try again later."
└─ Network error: "Cannot reach server. Check connection."

UI RESPONSE:
├─ Show error toast (top-right)
├─ Disable buttons during retry
├─ Show retry button
└─ Log to console for debugging
```

---

## Summary Table: Request Types & Handlers

| Endpoint | Method | Purpose | Cache? | ML? | DB Write? |
|----------|--------|---------|--------|-----|-----------|
| `/api/news/topic/{topic}` | GET | Fetch & enrich articles | ✅ 900s | ✅ Sentiment | ❌ |
| `/api/news/trending/headlines` | GET | Get trending ticker | ✅ 600s | ❌ | ❌ |
| `/api/summary/` | POST | Generate summary | ✅ 900s | ✅ TF-IDF | ❌ |
| `/api/sentiment/` | POST | Sentiment analysis | ✅ 900s | ✅ HF | ❌ |
| `/api/bookmarks/` | GET | List user bookmarks | ❌ | ❌ | ❌ |
| `/api/bookmarks/` | POST | Create bookmark | ❌ | ❌ | ✅ |
| `/api/bookmarks/{id}` | DELETE | Delete bookmark | ❌ | ❌ | ✅ |
| `/api/comments/` | GET | List comments | ❌ | ❌ | ❌ |
| `/api/comments/` | POST | Post comment | ❌ | ❌ | ✅ |
| `/api/news/refresh/{category}` | POST | Manual refresh | ❌ Reset | ✅ | ❌ |
| `/api/news/admin/reset-hits` | POST | Reset quota | ❌ Reset | ❌ | ❌ |

---

**End of Flow Structure Documentation**

This document provides a complete view of how data, requests, and components flow through the NewsAura project from user action to final UI render. Reference this during development, debugging, and presentations.
