import hashlib
from fastapi import APIRouter, HTTPException
from app.core.cache import get_from_cache, set_in_cache
from app.services.sentiment_ml import SentimentService  # ✅ Use new ML-based sentiment

router = APIRouter()


@router.post("/")
async def analyze_sentiment(payload: dict):
    """
    Analyze sentiment of input text using ML model.
    Returns label (Positive/Neutral/Negative) and confidence score (0-1).
    """
    text = payload.get("text")

    if not text or len(text.strip()) < 3:
        raise HTTPException(
            status_code=400,
            detail="Text is too short for sentiment analysis (minimum 3 characters)"
        )

    cache_key = SentimentService.get_sentiment_cache_key(text)

    # --------------------------------------------------
    # Cache check - reuse cached sentiment
    # --------------------------------------------------
    cached = await get_from_cache(cache_key)
    if cached:
        return {
            "source": "cache",
            "result": cached
        }

    # --------------------------------------------------
    # Analyze sentiment using ML model
    # --------------------------------------------------
    result = SentimentService.analyze(text)

    # --------------------------------------------------
    # Cache result for future requests
    # --------------------------------------------------
    await set_in_cache(cache_key, result)

    return {
        "source": "computed",
        "result": result
    }
