from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from src.schemas.base import BaseYTStatistic, BaseYTSnippet


class YTThumbnail(BaseModel):
    url: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class YTChannelSnippet(BaseYTSnippet):
    customUrl: Optional[str] = None
    country: Optional[str] = None


class YTChannelStatistics(BaseYTStatistic):
    subscriberCount: Optional[str] = None
    hiddenSubscriberCount: Optional[bool] = None
    videoCount: Optional[str] = None


class YTChannelItem(BaseModel):
    id: str
    snippet: Optional[YTChannelSnippet] = None
    statistics: Optional[YTChannelStatistics] = None


class YTChannelListResponse(BaseModel):
    items: list[YTChannelItem] = Field(default_factory=list)


class YTVideoSnippet(BaseYTSnippet):
    channelId: Optional[str] = None
    channelTitle: Optional[str] = None


class YTVideoStatistics(BaseYTStatistic):
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
