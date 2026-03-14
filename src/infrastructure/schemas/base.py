from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class BaseYTSnippet(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnails: Optional[dict] = None
    publishedAt: Optional[datetime] = None


class BaseYTStatistic(BaseModel):
    viewCount: Optional[str] = None


class BaseIGItem(BaseModel):
    id: str
    caption: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    timestamp: Optional[datetime] = None
    like_count: Optional[int] = None
    permalink: Optional[str] = None
    comments_count: Optional[int] = None
