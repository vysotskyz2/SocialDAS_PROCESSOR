import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import Text, String, DateTime, func, text, UniqueConstraint, Index, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID as Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

from src.infrastructure.models.base import Base


class TikTokUser(Base):
    __tablename__ = "tiktok_users"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    tt_open_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(String(200))
    avatar_url: Mapped[Optional[str]] = mapped_column(Text)
    bio_description: Mapped[Optional[str]] = mapped_column(Text)
    follower_count: Mapped[Optional[int]] = mapped_column(Integer)
    following_count: Mapped[Optional[int]] = mapped_column(Integer)
    likes_count: Mapped[Optional[int]] = mapped_column(Integer)
    video_count: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), onupdate=func.now())

    snapshots: Mapped[list["TikTokUserSnapshot"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    videos: Mapped[list["TikTokVideo"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )


class TikTokUserSnapshot(Base):
    __tablename__ = "tiktok_user_snapshots"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    user_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tiktok_users.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    follower_count: Mapped[Optional[int]] = mapped_column(Integer)
    following_count: Mapped[Optional[int]] = mapped_column(Integer)
    likes_count: Mapped[Optional[int]] = mapped_column(Integer)
    video_count: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("user_id", "date", name="uix_tt_user_snapshot_date"),
        Index("ix_tiktok_user_snapshots_user_id_date", "user_id", "date"),
    )

    user: Mapped["TikTokUser"] = relationship(back_populates="snapshots")


class TikTokVideo(Base):
    __tablename__ = "tiktok_videos"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    tt_video_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    user_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tiktok_users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[Optional[str]] = mapped_column(Text)
    video_description: Mapped[Optional[str]] = mapped_column(Text)
    duration: Mapped[Optional[int]] = mapped_column(Integer)
    cover_image_url: Mapped[Optional[str]] = mapped_column(Text)
    share_url: Mapped[Optional[str]] = mapped_column(Text)
    like_count: Mapped[Optional[int]] = mapped_column(Integer)
    comment_count: Mapped[Optional[int]] = mapped_column(Integer)
    share_count: Mapped[Optional[int]] = mapped_column(Integer)
    view_count: Mapped[Optional[int]] = mapped_column(Integer)
    create_time: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    last_updated: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (Index("ix_tiktok_videos_user_id_create_time", "user_id", "create_time"),)

    user: Mapped["TikTokUser"] = relationship(back_populates="videos")
    snapshots: Mapped[list["TikTokVideoSnapshot"]] = relationship(
        back_populates="video", cascade="all, delete-orphan"
    )


class TikTokVideoSnapshot(Base):
    __tablename__ = "tiktok_video_snapshots"

    id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, server_default=text("gen_random_uuid()")
    )
    video_id: Mapped[Uuid] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("tiktok_videos.id", ondelete="CASCADE"), nullable=False
    )
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    like_count: Mapped[Optional[int]] = mapped_column(Integer)
    comment_count: Mapped[Optional[int]] = mapped_column(Integer)
    share_count: Mapped[Optional[int]] = mapped_column(Integer)
    view_count: Mapped[Optional[int]] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("video_id", "date", name="uix_tt_video_snapshot_date"),
        Index("ix_tiktok_video_snapshots_video_id_date", "video_id", "date"),
    )

    video: Mapped["TikTokVideo"] = relationship(back_populates="snapshots")
