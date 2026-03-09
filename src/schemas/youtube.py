from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Raw API response schemas (YouTube Data API v3) ---

class YTThumbnail(BaseModel):
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class YTChannelSnippet(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    customUrl: Optional[str] = None
    publishedAt: Optional[datetime] = None
    thumbnails: Optional[dict] = None
    country: Optional[str] = None


class YTChannelStatistics(BaseModel):
    viewCount: Optional[str] = None
    subscriberCount: Optional[str] = None
    hiddenSubscriberCount: Optional[bool] = None
    videoCount: Optional[str] = None


class YTChannelItem(BaseModel):
    id: str
    snippet: Optional[YTChannelSnippet] = None
    statistics: Optional[YTChannelStatistics] = None


class YTChannelListResponse(BaseModel):
    items: list[YTChannelItem] = Field(default_factory=list)


class YTVideoSnippet(BaseModel):
    publishedAt: Optional[datetime] = None
    channelId: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    thumbnails: Optional[dict] = None
    channelTitle: Optional[str] = None


class YTVideoStatistics(BaseModel):
    viewCount: Optional[str] = None
    likeCount: Optional[str] = None
    favoriteCount: Optional[str] = None
    commentCount: Optional[str] = None


class YTVideoContentDetails(BaseModel):
    duration: Optional[str] = None  # ISO 8601, e.g. "PT4M13S"


class YTVideoItem(BaseModel):
    id: str
    snippet: Optional[YTVideoSnippet] = None
    statistics: Optional[YTVideoStatistics] = None
    contentDetails: Optional[YTVideoContentDetails] = None


class YTVideoListResponse(BaseModel):
    items: list[YTVideoItem] = Field(default_factory=list)
    nextPageToken: Optional[str] = None


class YTSearchItem(BaseModel):
    id: Optional[dict] = None  # {"kind": "youtube#video", "videoId": "..."}
    snippet: Optional[YTVideoSnippet] = None


class YTSearchResponse(BaseModel):
    items: list[YTSearchItem] = Field(default_factory=list)
    nextPageToken: Optional[str] = None


# --- Normalized output ---

class NormalizedYTChannel(BaseModel):
    yt_channel_id: str
    title: Optional[str] = None
    description: Optional[str] = None
    custom_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    country: Optional[str] = None
    published_at: Optional[datetime] = None
    subscriber_count: Optional[int] = None
    video_count: Optional[int] = None
    view_count: Optional[int] = None
