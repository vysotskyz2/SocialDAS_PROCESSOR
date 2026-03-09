from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# --- Raw API response schemas ---

class TTUserData(BaseModel):
    open_id: str
    union_id: Optional[str] = None
    avatar_url: Optional[str] = None
    display_name: Optional[str] = None
    bio_description: Optional[str] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    likes_count: Optional[int] = None
    video_count: Optional[int] = None


class TTUserInfoResponse(BaseModel):
    data: Optional[TTUserData] = None
    error: Optional[dict] = None


class TTVideoItem(BaseModel):
    id: str
    title: Optional[str] = None
    video_description: Optional[str] = None
    duration: Optional[int] = None
    cover_image_url: Optional[str] = None
    embed_link: Optional[str] = None
    share_url: Optional[str] = None
    like_count: Optional[int] = None
    comment_count: Optional[int] = None
    share_count: Optional[int] = None
    view_count: Optional[int] = None
    create_time: Optional[int] = None  # Unix timestamp


class TTVideoListData(BaseModel):
    videos: list[TTVideoItem] = Field(default_factory=list)
    cursor: Optional[int] = None
    has_more: Optional[bool] = None


class TTVideoListResponse(BaseModel):
    data: Optional[TTVideoListData] = None
    error: Optional[dict] = None


# --- Normalized output ---

class NormalizedTTUser(BaseModel):
    tt_open_id: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    bio_description: Optional[str] = None
    follower_count: Optional[int] = None
    following_count: Optional[int] = None
    likes_count: Optional[int] = None
    video_count: Optional[int] = None
