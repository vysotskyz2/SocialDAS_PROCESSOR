from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Raw API response schemas ---

class IGProfileResponse(BaseModel):
    id: str
    username: Optional[str] = None
    name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    followers_count: Optional[int] = None
    follows_count: Optional[int] = None
    media_count: Optional[int] = None
    biography: Optional[str] = None
    website: Optional[str] = None


class IGMediaItem(BaseModel):
    id: str
    caption: Optional[str] = None
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    permalink: Optional[str] = None
    timestamp: Optional[datetime] = None
    like_count: Optional[int] = None
    comments_count: Optional[int] = None


class IGMediaList(BaseModel):
    data: list[IGMediaItem] = Field(default_factory=list)


class IGInsightValue(BaseModel):
    value: int = 0
    end_time: Optional[str] = None


class IGInsightMetric(BaseModel):
    name: str
    period: str
    values: Optional[list[IGInsightValue]] = None
    total_value: Optional[dict] = None


class IGInsightList(BaseModel):
    data: list[IGInsightMetric] = Field(default_factory=list)


class IGStoryItem(BaseModel):
    id: str
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    timestamp: Optional[datetime] = None
    like_count: Optional[int] = None
    comments_count: Optional[int] = None
    caption: Optional[str] = None
    permalink: Optional[str] = None


class IGStoryList(BaseModel):
    data: list[IGStoryItem] = Field(default_factory=list)


# --- Normalized output (passed between service → repository) ---

class NormalizedIGProfile(BaseModel):
    ig_id: str
    username: Optional[str] = None
    name: Optional[str] = None
    profile_picture_url: Optional[str] = None
    biography: Optional[str] = None
    website: Optional[str] = None
    followers_count: Optional[int] = None
    follows_count: Optional[int] = None
    media_count: Optional[int] = None
