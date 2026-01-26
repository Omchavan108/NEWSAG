"""
GNews API Hit Counter
Tracks API calls for rate limiting (100 requests/day free tier)
"""

from datetime import datetime, timedelta
from typing import Dict
from app.core.cache import news_cache

class GNewsCounter:
    """
    Central counter for GNews API hits
    Uses cache to persist across requests
    Resets daily at midnight UTC
    """
    
    CACHE_KEY = "gnews:hits:today"
    MAX_HITS_PER_DAY = 100
    WARNING_THRESHOLD = 80  # Warn at 80% usage
    
    @staticmethod
    def get_today_key() -> str:
        """Get cache key for today"""
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        return f"{GNewsCounter.CACHE_KEY}:{date_str}"
    
    @staticmethod
    def increment_hit() -> Dict[str, int]:
        """
        Increment hit counter for today
        Returns: {"today_hits": int, "remaining_hits": int, "warning": bool}
        """
        cache_key = GNewsCounter.get_today_key()
        
        # Get current count (default 0 if not set)
        current_hits = news_cache.get(cache_key, 0)
        
        # Increment
        new_hits = current_hits + 1
        
        # Store back in cache with 24-hour TTL
        # TTL must be >= 24 hours to span the full day
        news_cache[cache_key] = new_hits
        
        remaining = max(0, GNewsCounter.MAX_HITS_PER_DAY - new_hits)
        is_warning = new_hits >= GNewsCounter.WARNING_THRESHOLD
        
        return {
            "today_hits": new_hits,
            "remaining_hits": remaining,
            "warning": is_warning,
            "max_hits": GNewsCounter.MAX_HITS_PER_DAY,
        }
    
    @staticmethod
    def get_hit_status() -> Dict[str, int]:
        """
        Get current hit status without incrementing
        Returns: {"today_hits": int, "remaining_hits": int}
        """
        cache_key = GNewsCounter.get_today_key()
        
        # Get current count (default 0 if not set)
        current_hits = news_cache.get(cache_key, 0)
        remaining = max(0, GNewsCounter.MAX_HITS_PER_DAY - current_hits)
        is_warning = current_hits >= GNewsCounter.WARNING_THRESHOLD
        
        return {
            "today_hits": current_hits,
            "remaining_hits": remaining,
            "warning": is_warning,
            "max_hits": GNewsCounter.MAX_HITS_PER_DAY,
        }
    
    @staticmethod
    def check_limit() -> tuple[bool, str]:
        """
        Check if we can make another API call
        Returns: (can_call: bool, message: str)
        """
        cache_key = GNewsCounter.get_today_key()
        current_hits = news_cache.get(cache_key, 0)
        
        if current_hits >= GNewsCounter.MAX_HITS_PER_DAY:
            return (
                False,
                f"GNews API limit reached ({GNewsCounter.MAX_HITS_PER_DAY}/day). Reset at midnight UTC."
            )
        
        if current_hits >= GNewsCounter.WARNING_THRESHOLD:
            remaining = GNewsCounter.MAX_HITS_PER_DAY - current_hits
            return (
                True,
                f"⚠️ WARNING: Only {remaining} API hits remaining today"
            )
        
        return (True, "OK")
    
    @staticmethod
    def reset_counter() -> Dict[str, int]:
        """
        Manually reset counter (for testing/admin)
        Returns: reset status
        """
        cache_key = GNewsCounter.get_today_key()
        news_cache.pop(cache_key, None)
        
        return {
            "status": "reset",
            "today_hits": 0,
            "remaining_hits": GNewsCounter.MAX_HITS_PER_DAY,
        }
