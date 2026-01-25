import hashlib
from fastapi import APIRouter, HTTPException
from app.core.cache import summary_cache, get_from_cache, set_in_cache
from app.services.summarizer import TextSummarizer
from app.services.text_utils import extract_article_text

router = APIRouter()

summarizer = TextSummarizer()


@router.get("/")
async def generate_summary(article_url: str):
    """
    Generate summary for a given article URL.
    Uses extractive NLP-based summarization (no AI).
    Fallback: returns placeholder for paywall-protected content.
    """

    cache_key = "summary:" + hashlib.md5(article_url.encode()).hexdigest()

    # --------------------------------------------------
    # 1. Cache check
    # --------------------------------------------------
    cached = get_from_cache(summary_cache, cache_key)
    if cached:
        return {
            "source": "cache",
            "summary": cached,
        }

    # --------------------------------------------------
    # 2. Fetch article content
    # --------------------------------------------------
    article_text = None
    try:
        article_text = await extract_article_text(article_url)
    except Exception as exc:
        # Log the error but don't fail - return placeholder
        print(f"[Summary] Failed to extract text from {article_url}: {exc}")
        article_text = None

    # If extraction failed or content is too short, return placeholder
    if not article_text or len(article_text) < 300:
        placeholder_summary = "Unable to generate a summary for this article. It may be behind a paywall or require authentication. Please visit the article directly to read the full content."
        set_in_cache(summary_cache, cache_key, placeholder_summary)
        return {
            "source": "placeholder",
            "summary": placeholder_summary,
        }

    # --------------------------------------------------
    # 3. Generate summary
    # --------------------------------------------------
    summary = summarizer.summarize(article_text)

    # --------------------------------------------------
    # 4. Cache result
    # --------------------------------------------------
    set_in_cache(summary_cache, cache_key, summary)

    return {
        "source": "generated",
        "summary": summary,
    }

