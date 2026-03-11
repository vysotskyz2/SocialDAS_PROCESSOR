from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.infrastructure.models.youtube import YouTubeChannel, YouTubeChannelSnapshot, YouTubeVideo, YouTubeVideoSnapshot
from src.infrastructure.repositories.base import BaseRepository
from src.schemas.youtube import YTChannelItem, YTVideoItem


def _safe_int(value: str | None) -> int | None:
    try:
        return int(value) if value is not None else None
    except (ValueError, TypeError):
        return None


class YouTubeRepository(BaseRepository):

    async def upsert_channel(self, item: YTChannelItem) -> UUID:
        snippet = item.snippet or {}
        stats = item.statistics

        thumbnail_url = None
        if snippet and snippet.thumbnails:
            thumb = snippet.thumbnails.get("high") or snippet.thumbnails.get("default")
            thumbnail_url = thumb.get("url") if isinstance(thumb, dict) else None

        values = {
            "yt_channel_id": item.id,
            "title": snippet.title if snippet else None,
            "description": snippet.description if snippet else None,
            "custom_url": snippet.customUrl if snippet else None,
            "thumbnail_url": thumbnail_url,
            "country": snippet.country if snippet else None,
            "published_at": snippet.publishedAt if snippet else None,
        }
        stmt = (
            pg_insert(YouTubeChannel)
            .values(**values)
            .on_conflict_do_update(
                index_elements=["yt_channel_id"],
                set_={k: v for k, v in values.items() if k != "yt_channel_id"},
            )
            .returning(YouTubeChannel.id)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    async def upsert_channel_snapshot(self, channel_id: UUID, item: YTChannelItem) -> None:
        stats = item.statistics
        today = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        values = {
            "channel_id": channel_id,
            "date": today,
            "subscriber_count": _safe_int(stats.subscriberCount) if stats else None,
            "video_count": _safe_int(stats.videoCount) if stats else None,
            "view_count": _safe_int(stats.viewCount) if stats else None,
        }
        stmt = (
            pg_insert(YouTubeChannelSnapshot)
            .values(**values)
            .on_conflict_do_update(
                constraint="uix_yt_channel_snapshot_date",
                set_={k: v for k, v in values.items() if k not in ("channel_id", "date")},
            )
            .returning(YouTubeChannelSnapshot.id)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def upsert_video(self, channel_id: UUID, item: YTVideoItem) -> UUID:
        snippet = item.snippet
        thumbnail_url = None
        if snippet and snippet.thumbnails:
            thumb = snippet.thumbnails.get("high") or snippet.thumbnails.get("default")
            thumbnail_url = thumb.get("url") if isinstance(thumb, dict) else None

        values = {
            "yt_video_id": item.id,
            "channel_id": channel_id,
            "title": snippet.title if snippet else None,
            "description": snippet.description if snippet else None,
            "thumbnail_url": thumbnail_url,
            "published_at": snippet.publishedAt if snippet else None,
            "duration": item.contentDetails.duration if item.contentDetails else None,
            "last_updated": datetime.now(tz=timezone.utc),
        }
        stmt = (
            pg_insert(YouTubeVideo)
            .values(**values)
            .on_conflict_do_update(
                index_elements=["yt_video_id"],
                set_={k: v for k, v in values.items() if k not in ("yt_video_id", "channel_id")},
            )
            .returning(YouTubeVideo.id)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    async def upsert_video_snapshot(self, video_id: UUID, item: YTVideoItem) -> None:
        stats = item.statistics
        today = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        values = {
            "video_id": video_id,
            "date": today,
            "view_count": _safe_int(stats.viewCount) if stats else None,
            "like_count": _safe_int(stats.likeCount) if stats else None,
            "comment_count": _safe_int(stats.commentCount) if stats else None,
        }
        stmt = (
            pg_insert(YouTubeVideoSnapshot)
            .values(**values)
            .on_conflict_do_update(
                constraint="uix_yt_video_snapshot_date",
                set_={k: v for k, v in values.items() if k not in ("video_id", "date")},
            )
            .returning(YouTubeVideoSnapshot.id)
        )
        await self._session.execute(stmt)
        await self._session.flush()
