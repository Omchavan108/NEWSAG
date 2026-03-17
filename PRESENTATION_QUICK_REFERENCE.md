# NewsAura - Presentation Quick Reference Card

## 🎯 1-Minute Elevator Pitch

**What:** NewsAura is an intelligent news aggregator that fetches headlines from GNews, enriches them with AI sentiment analysis and extractive summaries, and displays them in a unified, user-friendly interface with bookmarking and read-later features.

**Why:** Users suffer from information overload—reading full articles takes too long and many are paywalled. NewsAura reduces time-to-insight via AI summaries and sentiment badges.

**How:** FastAPI backend fetches + enriches articles from GNews API, caches results in Redis to meet rate quotas, and a React frontend displays them with on-demand AI summaries via TF-IDF extraction.

---

## 📊 System at a Glance

| Component | Technology | Role |
|-----------|-----------|------|
| Frontend | React + TypeScript (Vite) | User-facing SPA |
| Backend | FastAPI + Python 3.11 | REST API + business logic |
| News Source | GNews.io API | Aggregated headlines |
| Cache | Redis | Article + sentiment + summary + quota caching |
| DB | MongoDB | User bookmarks, comments, read-later |
| ML (Sentiment) | HuggingFace `cardiffnlp/twitter-roberta` | Classify tone (Positive/Neutral/Negative) |
| NLP (Summary) | Custom TF-IDF + lead-bias | Extractive summarization |
| Scraping | httpx + BeautifulSoup | Extract full article text |
| Auth | Clerk | User sessions & tokens |

---

## 🔄 Three Key Flows

### 1. **Get News (Cache-First)**
```
Frontend: "Show me Technology news"
  ↓
Backend: Check Redis "gnews:technology"
  ├─ HIT: Return cached articles + sentiment
  └─ MISS:
      ├─ Check daily quota (100 hits/day via Redis counter)
      ├─ Call GNews API
      ├─ Run sentiment ML on each article
      ├─ Cache everything
      └─ Return to Frontend
  ↓
Frontend: Render NewsGrid with sentiment badges
```

### 2. **Generate Summary (On-Demand)**
```
User: "Show AI Summary for this article"
  ↓
Backend: 
  ├─ Check Redis cache (avoid repeat work)
  ├─ Scrape full article text (httpx + BeautifulSoup)
  ├─ Run TF-IDF extractive summarizer
  ├─ Fallback to GNews description if scrape fails
  └─ Cache + return summary
  ↓
Frontend: Display in newspaper-style modal
```

### 3. **User Actions (CRUD)**
```
User: "Bookmark this article"
  ↓
Frontend: POST /api/bookmarks/ with Bearer token (Clerk)
  ↓
Backend: Validate token → Insert into MongoDB
  ↓
Frontend: Update UI (bookmark icon → filled)
```

---

## 🏗️ Architecture Layers (Simplified)

```
┌─────────────────────────────────────────┐
│  React SPA (TypeScript, Axios)          │
│  Components: NewsCard, NewsGrid, Modal  │
└──────────────────┬──────────────────────┘
                   │ HTTP
                   ↓
┌─────────────────────────────────────────┐
│  FastAPI Routers (news, summary, etc)   │
└──────────────────┬──────────────────────┘
                   │
         ┌─────────┴──────────┐
         ↓                    ↓
    ┌─────────────────┐  ┌──────────────────┐
    │ Services Layer  │  │ External APIs    │
    │ - GNewsService  │  │ - GNews.io       │
    │ - Sentiment ML  │  │ - HuggingFace    │
    │ - TextSummarizer│  │ - Article Pages  │
    │ - text_utils    │  │   (via scraping) │
    └────────┬────────┘  └──────────────────┘
             │
      ┌──────┴────────┐
      ↓               ↓
   Redis         MongoDB
  (cache)     (bookmarks,
  (articles)   comments)
  (sentiment)
  (quota)
```

---

## 🔑 Key Statistics

- **Cache TTL:** 900 seconds (15 minutes) for articles, sentiment, summaries
- **GNews Quota:** 100 requests/day (free tier) enforced via daily counter
- **Article extraction:** MD5 hash of URL for deterministic IDs
- **Sentiment model:** Runs on CPU (no GPU required for production safety)
- **Summarizer:** Extractive TF-IDF with lead-bias weighting and redundancy filtering

---

## 📁 File Quick Navigation

| Need | File(s) |
|------|---------|
| **Add new API route** | `backend/app/routers/*.py` + import in `main.py` |
| **Change GNews quota** | `backend/app/core/gnews_counter.py` (MAX_HITS_PER_DAY) |
| **Modify cache TTL** | `backend/app/core/config.py` (CACHE_TTL_NEWS) |
| **Add new MongoDB model** | `backend/app/models/newmodel.py` (inherit from MongoBase) |
| **Change UI layout** | `frontend/src/components/news/NewsCard.tsx` or `NewsGrid.tsx` |
| **Modify sentiment label** | `frontend/src/components/news/SentimentBadge.tsx` |
| **Add new page** | `frontend/src/pages/NewPage.tsx` + add to router |

---

## 🎮 Live Demo Script (2 minutes)

1. **Show Home page** → Click "Technology" category
   - *"Fetches fresh news from GNews API, caches for 15 minutes"*
   
2. **Hover over sentiment badges** → Point out Positive/Neutral/Negative labels + confidence scores
   - *"Real-time ML sentiment classification—helps users assess tone at a glance"*
   
3. **Click "AI Summary"** → Show modal with extractive summary
   - *"Uses TF-IDF + lead-bias algorithm to pick the most important sentences"*
   
4. **Click bookmark icon** → Show it toggle to filled state
   - *"Saved to MongoDB—users can sync across devices"*
   
5. **Refresh page** → Note articles still display (cached!)
   - *"Redis cache prevents redundant API calls and meets rate limits"*

---

## ❓ Expected Interview Q&A

**Q: Why FastAPI instead of Django/Express?**
> A: FastAPI is async-native, which is crucial for I/O-bound operations (fetching GNews, scraping pages, ML inference). Async reduces latency and thread overhead under concurrent load.

**Q: How do you handle API rate limits?**
> A: Via `GNewsCounter` in Redis—tracks daily hits (100 limit), warns at 80%, blocks further calls when capped, and allows admin resets. Caching is the first defense; manual/scheduled refreshes distribute hits over time.

**Q: Why extractive summarization instead of generative LLMs?**
> A: Extractive is deterministic, fast (no external API), cost-free, and production-safe. Generative LLMs are on the roadmap once usage justifies the cost.

**Q: How do you prevent ML inference from slowing down requests?**
> A: Per-text caching in Redis. First request for text X infers sentiment; second request hits Redis cache instantly. Batching + background workers are planned for scale.

**Q: What if GNews scraping fails?**
> A: We have a fallback hierarchy: scraped text → GNews content → GNews description → placeholder message. Never leaves user without content.

**Q: How is user data secured?**
> A: Clerk tokens validate sessions. Bearer tokens in requests map to user_id in MongoDB. Passwords never stored (Clerk handles auth). Recommended: add RBAC middleware for admin routes.

---

## 🚀 Deployment Checklist

- [ ] Set `GNEWS_API_KEY` in environment (get from gnews.io)
- [ ] Set `MONGO_URI` (local or cloud; e.g., MongoDB Atlas)
- [ ] Set `REDIS_URL` (local or cloud; e.g., Redis Cloud)
- [ ] Set `VITE_CLERK_PUBLISHABLE_KEY` in frontend (from Clerk dashboard)
- [ ] Backend: `pip install -r requirements.txt` → `uvicorn app.main:app`
- [ ] Frontend: `npm install` → `npm run dev` (Vite dev server)
- [ ] Test: Open http://localhost:5173, click a category, verify articles load

---

## 📈 Future Roadmap (Next 6 months)

1. **Batch ML inference** (background workers, RQ/Celery)
2. **Model quantization** (ONNX exports, faster CPU inference)
3. **Multi-source aggregator** (fallback news APIs, source credibility)
4. **Personalization** (user embeddings, collaborative filtering)
5. **Generative summarization** (small LLM, A/B tested vs extractive)
6. **CI/CD pipeline** (GitHub Actions, auto-deploy on main)
7. **Observability** (Prometheus/Grafana for monitoring)
8. **Offline mode** (service workers, local caching)

---

## 💡 Final Talking Point

> "NewsAura solves the information overload problem by intelligently aggregating news, reducing read time via AI summaries, and surfacing sentiment tone so users can quickly triage what matters to them. The architecture is production-ready: async stack for concurrent I/O, Redis caching to respect API quotas, and MongoDB for user-specific data. It's a practical demonstration of modern full-stack engineering—combining real-world constraints (rate limits, paywalls) with practical AI (sentiment classification, extractive summarization) and proven deployment patterns."

---

## 📞 Contact / Questions

If presenting, end with:
- "Questions?"
- Tech deep-dive available upon request (show code, run demo, discuss trade-offs)
