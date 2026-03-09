import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Text, String, DateTime, func, text, UniqueConstraint, Index, BigInteger
from sqlalchemy.dialects.postgresql import UUID as Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.infrastructure.models.base import Base


class YouTubeChannel(Base):
    __tablename__ = "youtube_channels"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    yt_channel_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(500))
    description: Mapped[Optional[str]] = mapped_column(Text)
    custom_url: Mapped[Optional[str]] = mapped_column(String(200))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)
    country: Mapped[Optional[str]] = mapped_column(String(10))
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    snapshots: Mapped[list["YouTubeChannelSnapshot"]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )
    videos: Mapped[list["YouTubeVideo"]] = relationship(
        back_populates="channel", cascade="all, delete-orphan"
    )


class YouTubeChannelSnapshot(Base):
    __tablename__ = "youtube_channel_snapshots"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    channel_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    subscriber_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    video_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    view_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("channel_id", "date", name="uix_yt_channel_snapshot_date"),
        Index("ix_yt_channel_snapshots_channel_id_date", "channel_id", "date"),
    )

    channel: Mapped["YouTubeChannel"] = relationship(back_populates="snapshots")


class YouTubeVideo(Base):
    __tablename__ = "youtube_videos"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    yt_video_id: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    channel_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("youtube_channels.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(Text)
    description: Mapped[Optional[str]] = mapped_column(Text)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(Text)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    duration: Mapped[Optional[str]] = mapped_column(String(20))  # ISO 8601, e.g. "PT4M13S"
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_yt_videos_channel_id_published_at", "channel_id", "published_at"),)

    channel: Mapped["YouTubeChannel"] = relationship(back_populates="videos")
    snapshots: Mapped[list["YouTubeVideoSnapshot"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )


class YouTubeVideoSnapshot(Base):
    __tablename__ = "youtube_video_snapshots"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    video_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("youtube_videos.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    view_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    like_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    comment_count: Mapped[Optional[int]] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("video_id", "date", name="uix_yt_video_snapshot_date"),
        Index("ix_yt_video_snapshots_video_id_date", "video_id", "date"),
    )

    video: Mapped["YouTubeVideo"] = relationship(back_populates="snapshots")
