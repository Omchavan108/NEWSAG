from fastapi import APIRouter, HTTPException
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

    # --------------------------------------------------
    # Analyze sentiment using ML model (service handles caching)
    # --------------------------------------------------
    result = await SentimentService.analyze(text)

    return {
        "source": "computed",
        "result": result
    }
