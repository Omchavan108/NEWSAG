import logging
from fastapi import APIRouter, HTTPException
from app.services.news_service import GNewsService
from app.core.cache import news_cache, get_from_cache, set_in_cache

router = APIRouter()
logger = logging.getLogger(__name__)

# Default categories
CATEGORIES = ["general", "nation", "business", "technology", "sports", "entertainment", "health"]

# -----------------------------
# GET NEWS BY TOPIC (CACHE FIRST)
# -----------------------------
@router.get("/topic/{topic}")
async def get_news_by_topic(topic: str):
    """Fetch news by topic/category with caching"""
    cache_key = f"gnews:{topic}"

    cached = get_from_cache(news_cache, cache_key)
    if cached:
        logger.info(f"[CACHE HIT] {topic}")
        return {
            "source": "cache",
            "count": len(cached),
            "articles": cached,
        }

    logger.info(f"[GNEWS HIT] {topic}")
    try:
        articles = await GNewsService.fetch_category(topic)
    except Exception as e:
        logger.error(f"Error fetching news for {topic}: {str(e)}")
        raise HTTPException(status_code=502, detail=str(e))

    set_in_cache(news_cache, cache_key, articles)

    return {
        "source": "api",
        "count": len(articles),
        "articles": articles,
    }

# Backward compatibility
@router.get("/{category}")
async def get_news(category: str):
    """Fetch news by category (backward compatibility)"""
    return await get_news_by_topic(category)


# -----------------------------
# MANUAL REFRESH (1 HIT)
# -----------------------------
@router.post("/refresh/{category}")
async def refresh_category(category: str):
    """Manually refresh news for a specific category"""
    cache_key = f"gnews:{category}"
    news_cache.pop(cache_key, None)

    logger.warning(f"[MANUAL REFRESH] {category}")
    try:
        articles = await GNewsService.fetch_category(category)
    except Exception as e:
        logger.error(f"Error refreshing {category}: {str(e)}")
        raise HTTPException(status_code=502, detail=str(e))
    
    set_in_cache(news_cache, cache_key, articles)

    return {
        "message": f"{category} refreshed",
        "hits_used": 1,
        "articles": len(articles),
    }


# -----------------------------
# REFRESH ALL (7 HITS)
# -----------------------------
@router.post("/refresh-all")
async def refresh_all():
    """Refresh all categories at once"""
    categories = CATEGORIES
    total_articles = 0
    errors = []

    for cat in categories:
        try:
            news_cache.pop(f"gnews:{cat}", None)
            articles = await GNewsService.fetch_category(cat)
            set_in_cache(news_cache, f"gnews:{cat}", articles)
            total_articles += len(articles)
        except Exception as e:
            logger.error(f"Error refreshing {cat}: {str(e)}")
            errors.append(f"{cat}: {str(e)}")

    logger.warning(f"[MANUAL REFRESH ALL] categories={len(categories)}, articles={total_articles}")

    return {
        "message": "All categories refreshed",
        "categories_refreshed": len(categories),
        "total_articles": total_articles,
        "errors": errors if errors else None,
    }
