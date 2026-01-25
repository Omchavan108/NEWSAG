from datetime import datetime
from typing import Optional
from pydantic import Field
from app.models.base import MongoBase


class CommentModel(MongoBase):
    """
    Comment data model stored in MongoDB.
    """

    article_id: str
    article_title: str
    
    text: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
