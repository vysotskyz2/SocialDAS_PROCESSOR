from datetime import datetime, timezone
from uuid import UUID
from sqlalchemy.dialects.postgresql import insert as pg_insert
from src.infrastructure.models.tiktok import TikTokUser, TikTokUserSnapshot, TikTokVideo, TikTokVideoSnapshot
from src.infrastructure.repositories.base import BaseRepository
from src.schemas.tiktok import TTUserData, TTVideoItem


class TikTokRepository(BaseRepository):

    async def upsert_user(self, data: TTUserData) -> UUID:
        values = {
            "tt_open_id": data.open_id,
            "display_name": data.display_name,
            "avatar_url": data.avatar_url,
            "bio_description": data.bio_description,
            "follower_count": data.follower_count,
            "following_count": data.following_count,
            "likes_count": data.likes_count,
            "video_count": data.video_count,
        }
        stmt = (
            pg_insert(TikTokUser)
            .values(**values)
            .on_conflict_do_update(
                index_elements=["tt_open_id"],
                set_={k: v for k, v in values.items() if k != "tt_open_id"},
            )
            .returning(TikTokUser.id)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    async def upsert_user_snapshot(self, user_id: UUID, data: TTUserData) -> None:
        today = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        values = {
            "user_id": user_id,
            "date": today,
            "follower_count": data.follower_count,
            "following_count": data.following_count,
            "likes_count": data.likes_count,
            "video_count": data.video_count,
        }
        stmt = (
            pg_insert(TikTokUserSnapshot)
            .values(**values)
            .on_conflict_do_update(
                constraint="uix_tt_user_snapshot_date",
                set_={k: v for k, v in values.items() if k not in ("user_id", "date")},
            )
            .returning(TikTokUserSnapshot.id)
        )
        await self._session.execute(stmt)
        await self._session.flush()

    async def upsert_video(self, user_id: UUID, item: TTVideoItem) -> UUID:
        create_time = (
            datetime.fromtimestamp(item.create_time, tz=timezone.utc) if item.create_time else None
        )
        values = {
            "tt_video_id": item.id,
            "user_id": user_id,
            "title": item.title,
            "video_description": item.video_description,
            "duration": item.duration,
            "cover_image_url": item.cover_image_url,
            "share_url": item.share_url,
            "like_count": item.like_count,
            "comment_count": item.comment_count,
            "share_count": item.share_count,
            "view_count": item.view_count,
            "create_time": create_time,
            "last_updated": datetime.now(tz=timezone.utc),
        }
        stmt = (
            pg_insert(TikTokVideo)
            .values(**values)
            .on_conflict_do_update(
                index_elements=["tt_video_id"],
                set_={k: v for k, v in values.items() if k not in ("tt_video_id", "user_id")},
            )
            .returning(TikTokVideo.id)
        )
        result = await self._session.execute(stmt)
        await self._session.flush()
        return result.scalar_one()

    async def upsert_video_snapshot(self, video_id: UUID, item: TTVideoItem) -> None:
        today = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        values = {
            "video_id": video_id,
            "date": today,
            "like_count": item.like_count,
            "comment_count": item.comment_count,
            "share_count": item.share_count,
            "view_count": item.view_count,
        }
        stmt = (
            pg_insert(TikTokVideoSnapshot)
            .values(**values)
            .on_conflict_do_update(
                constraint="uix_tt_video_snapshot_date",
                set_={k: v for k, v in values.items() if k not in ("video_id", "date")},
            )
            .returning(TikTokVideoSnapshot.id)
        )
        await self._session.execute(stmt)
        await self._session.flush()

