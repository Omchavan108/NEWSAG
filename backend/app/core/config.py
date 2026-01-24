import os
from dotenv import load_dotenv

# --------------------------------------------------
# Load environment variables from .env
# --------------------------------------------------
load_dotenv()


class Settings:
    """
    Centralized application configuration.
    All environment variables are accessed through this class.
    """

    # --------------------------------------------------
    # Application
    # --------------------------------------------------
    APP_NAME: str = "NewsAura Backend"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True

    # --------------------------------------------------
    # Server
    # --------------------------------------------------
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", 8000))

    # --------------------------------------------------
    # Database (MongoDB)
    # --------------------------------------------------
    MONGO_URI: str = os.getenv("MONGO_URI", "")

    # --------------------------------------------------
    # News API (Data source only, NOT AI)
    # --------------------------------------------------
    NEWS_API_KEY: str = os.getenv("NEWS_API_KEY", "")
    NEWS_API_BASE_URL: str = "https://newsapi.org/v2"

    # --------------------------------------------------
    # Caching
    # --------------------------------------------------
    CACHE_TTL_NEWS: int = 60 * 10      # 10 minutes
    CACHE_TTL_SUMMARY: int = 60 * 60   # 1 hour
    CACHE_TTL_SENTIMENT: int = 60 * 60 # 1 hour


# --------------------------------------------------
# Create a single settings object
# --------------------------------------------------
settings = Settings()
