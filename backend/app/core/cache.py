from cachetools import TTLCache
from app.core.config import settings

# --------------------------------------------------
# Centralized Cache Objects
# --------------------------------------------------

# Cache for news articles (by category)
news_cache = TTLCache(
    maxsize=100,
    ttl=settings.CACHE_TTL_NEWS
)

# Cache for article summaries
summary_cache = TTLCache(
    maxsize=200,
    ttl=settings.CACHE_TTL_SUMMARY
)

# Cache for sentiment analysis results
sentiment_cache = TTLCache(
    maxsize=300,
    ttl=settings.CACHE_TTL_SENTIMENT
)


# --------------------------------------------------
# Helper Functions
# --------------------------------------------------

def get_from_cache(cache: TTLCache, key: str):
    """
    Safely get value from cache.
    Returns None if key does not exist.
    """
    return cache.get(key)


def set_in_cache(cache: TTLCache, key: str, value):
    """
    Store value in cache.
    """
    cache[key] = value
