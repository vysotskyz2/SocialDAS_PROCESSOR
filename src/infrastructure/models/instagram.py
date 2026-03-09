"""Instagram ORM models. analytics.py re-exports from here for backward compatibility."""
import uuid
from datetime import datetime
from typing import Optional
from enum import StrEnum

from sqlalchemy import Text, String, DateTime, func, text, UniqueConstraint, Index, Integer
from sqlalchemy.dialects.postgresql import UUID as Uuid
from sqlalchemy.dialects.postgresql import ENUM as PgEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.infrastructure.models.base import Base


class MediaType(StrEnum):
    IMAGE = "IMAGE"
    VIDEO = "VIDEO"
    CAROUSEL_ALBUM = "CAROUSEL_ALBUM"


class InsightPeriod(StrEnum):
    DAY = "day"
    WEEK = "week"
    DAYS_28 = "28_days"


class User(Base):
    __tablename__ = "users"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=text("gen_random_uuid()")
    )
    ig_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    username: Mapped[Optional[str]] = mapped_column(String(100))
    name: Mapped[Optional[str]] = mapped_column(String(200))
    profile_picture_url: Mapped[Optional[str]] = mapped_column(Text)
    biography: Mapped[Optional[str]] = mapped_column(Text)
    website: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    snapshots: Mapped[list["UserSnapshot"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    posts: Mapped[list["Post"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    stories: Mapped[list["Story"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    profile_insights: Mapped[list["ProfileInsight"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserSnapshot(Base):
    __tablename__ = "user_snapshots"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    followers_count: Mapped[Optional[int]] = mapped_column(Integer)
    follows_count: Mapped[Optional[int]] = mapped_column(Integer)
    media_count: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uix_user_snapshot_date"),
        Index("ix_user_snapshots_user_id_date", "user_id", "date"),
    )

    user: Mapped["User"] = relationship(back_populates="snapshots")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    ig_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    media_type: Mapped[Optional[MediaType]] = mapped_column(
        PgEnum(MediaType, name="mediatype_enum", create_type=True)
    )
    caption: Mapped[Optional[str]] = mapped_column(Text)
    media_url: Mapped[Optional[str]] = mapped_column(Text)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)
    permalink: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    like_count: Mapped[Optional[int]] = mapped_column(Integer)
    comments_count: Mapped[Optional[int]] = mapped_column(Integer)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_posts_user_id_timestamp", "user_id", "timestamp"),)

    user: Mapped["User"] = relationship(back_populates="posts")
    insights: Mapped[list["PostInsight"]] = relationship(back_populates="post", cascade="all, delete-orphan")


class PostInsight(Base):
    __tablename__ = "post_insights"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    post_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("posts.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reach: Mapped[Optional[int]] = mapped_column(Integer)
    saved: Mapped[Optional[int]] = mapped_column(Integer)
    views: Mapped[Optional[int]] = mapped_column(Integer)
    shares: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("post_id", "date", name="uix_post_insight_date"),
        Index("ix_post_insights_post_id_date", "post_id", "date"),
    )

    post: Mapped["Post"] = relationship(back_populates="insights")


class Story(Base):
    __tablename__ = "stories"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    ig_id: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    user_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    media_type: Mapped[Optional[MediaType]] = mapped_column(
        PgEnum(MediaType, name="mediatype_enum", create_type=True)
    )
    media_url: Mapped[Optional[str]] = mapped_column(Text)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)
    permalink: Mapped[Optional[str]] = mapped_column(Text)
    timestamp: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    like_count: Mapped[Optional[int]] = mapped_column(Integer)
    comments_count: Mapped[Optional[int]] = mapped_column(Integer)
    caption: Mapped[Optional[str]] = mapped_column(Text)
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_stories_user_id_timestamp", "user_id", "timestamp"),)

    user: Mapped["User"] = relationship(back_populates="stories")


class ProfileInsight(Base):
    __tablename__ = "profile_insights"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    period: Mapped[InsightPeriod] = mapped_column(
        PgEnum(InsightPeriod, name="insightperiod_enum", create_type=True), nullable=False
    )
    reach: Mapped[Optional[int]] = mapped_column(Integer)
    profile_views: Mapped[Optional[int]] = mapped_column(Integer)
    views: Mapped[Optional[int]] = mapped_column(Integer)
    likes: Mapped[Optional[int]] = mapped_column(Integer)
    comments: Mapped[Optional[int]] = mapped_column(Integer)
    website_clicks: Mapped[Optional[int]] = mapped_column(Integer)
    shares: Mapped[Optional[int]] = mapped_column(Integer)
    saves: Mapped[Optional[int]] = mapped_column(Integer)
    replies: Mapped[Optional[int]] = mapped_column(Integer)
    reposts: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "date", "period", name="uix_profile_insight_user_date_period"),
        Index("ix_profile_insights_user_id_date_period", "user_id", "date", "period"),
    )

    user: Mapped["User"] = relationship(back_populates="profile_insights")
