from typing import Optional
from pydantic import BaseModel, Field
from src.schemas.base import BaseIGItem


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


class IGMediaItem(BaseIGItem):
    pass


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


class IGStoryItem(BaseIGItem):
    pass


class IGStoryList(BaseModel):
    data: list[IGStoryItem] = Field(default_factory=list)


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
