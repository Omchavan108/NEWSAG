from datetime import datetime
from pydantic import Field
from app.models.base import MongoBase


class ReadLaterModel(MongoBase):
    """
    Read Later model for deferred articles.
    """

    
    article_id: str
    title: str
    source: str
    category: str | None = None
    url: str
    image_url: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
