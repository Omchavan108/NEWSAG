from cachetools import TTLCache
from app.core.config import settings

# -----------------------------
# NEWS CACHE (GNEWS)
# -----------------------------
news_cache = TTLCache(
    maxsize=50,
    ttl=settings.CACHE_TTL_NEWS
)

# -----------------------------
# SUMMARY CACHE
# -----------------------------
summary_cache = TTLCache(
    maxsize=100,
    ttl=settings.CACHE_TTL_NEWS
)

# -----------------------------
# SENTIMENT CACHE
# -----------------------------
sentiment_cache = TTLCache(
    maxsize=100,
    ttl=settings.CACHE_TTL_NEWS
)

def get_from_cache(cache: TTLCache, key: str):
    return cache.get(key)

def set_in_cache(cache: TTLCache, key: str, value):
    cache[key] = value
