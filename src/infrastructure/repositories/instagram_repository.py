from datetime import date, datetime, timezone
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.infrastructure.database import async_session_factory
from src.infrastructure.models.instagram import (
    User, UserSnapshot, Post, PostInsight, Story, ProfileInsight, MediaType, InsightPeriod,
)
from src.schemas.instagram import IGProfileResponse, IGMediaItem, IGStoryItem, IGInsightMetric


class InstagramRepository:

    async def upsert_user(self, profile: IGProfileResponse) -> UUID:
        """Вставляет или обновляет пользователя Instagram по ig_id. Возвращает внутренний UUID."""
        values = {
            "ig_id": profile.id,
            "username": profile.username,
            "name": profile.name,
            "profile_picture_url": profile.profile_picture_url,
            "biography": profile.biography,
            "website": profile.website,
        }
        stmt = (
            pg_insert(User)
            .values(**values)
            .on_conflict_do_update(
                index_elements=["ig_id"],
                set_={k: v for k, v in values.items() if k != "ig_id"},
            )
            .returning(User.id)
        )
        async with async_session_factory() as session:
            async with session.begin():
                result = await session.execute(stmt)
                return result.scalar_one()

    async def upsert_user_snapshot(self, user_id: UUID, profile: IGProfileResponse) -> None:
        today = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        values = {
            "user_id": user_id,
            "date": today,
            "followers_count": profile.followers_count,
            "follows_count": profile.follows_count,
            "media_count": profile.media_count,
        }
        stmt = (
            pg_insert(UserSnapshot)
            .values(**values)
            .on_conflict_do_update(
                constraint="uix_ig_user_snapshot_date",
                set_={k: v for k, v in values.items() if k not in ("user_id", "date")},
            )
        )
        async with async_session_factory() as session:
            async with session.begin():
                await session.execute(stmt)

    async def upsert_post(self, user_id: UUID, item: IGMediaItem) -> UUID:
        try:
            media_type = MediaType(item.media_type) if item.media_type else None
        except ValueError:
            media_type = None

        values = {
            "ig_id": item.id,
            "user_id": user_id,
            "media_type": media_type,
            "caption": item.caption,
            "media_url": item.media_url,
            "thumbnail_url": item.thumbnail_url,
            "permalink": item.permalink,
            "timestamp": item.timestamp,
            "like_count": item.like_count,
            "comments_count": item.comments_count,
            "last_updated": datetime.now(tz=timezone.utc),
        }
        stmt = (
            pg_insert(Post)
            .values(**values)
            .on_conflict_do_update(
                index_elements=["ig_id"],
                set_={k: v for k, v in values.items() if k not in ("ig_id", "user_id")},
            )
            .returning(Post.id)
        )
        async with async_session_factory() as session:
            async with session.begin():
                result = await session.execute(stmt)
                return result.scalar_one()

    async def upsert_story(self, user_id: UUID, item: IGStoryItem) -> None:
        try:
            media_type = MediaType(item.media_type) if item.media_type else None
        except ValueError:
            media_type = None

        values = {
            "ig_id": item.id,
            "user_id": user_id,
            "media_type": media_type,
            "media_url": item.media_url,
            "thumbnail_url": item.thumbnail_url,
            "permalink": item.permalink,
            "timestamp": item.timestamp,
            "like_count": item.like_count,
            "comments_count": item.comments_count,
            "caption": item.caption,
            "last_updated": datetime.now(tz=timezone.utc),
        }
        stmt = (
            pg_insert(Story)
            .values(**values)
            .on_conflict_do_update(
                index_elements=["ig_id"],
                set_={k: v for k, v in values.items() if k not in ("ig_id", "user_id")},
            )
        )
        async with async_session_factory() as session:
            async with session.begin():
                await session.execute(stmt)

    async def upsert_profile_insight(
        self, user_id: UUID, metric: IGInsightMetric, snapshot_date: datetime
    ) -> None:
        try:
            period = InsightPeriod(metric.period)
        except ValueError:
            logger.warning(f"Неизвестный период метрики: {metric.period}")
            return

        total = (metric.total_value or {}).get("value", 0)
        values = {
            "user_id": user_id,
            "date": snapshot_date,
            "period": period,
            metric.name: total,
        }
        stmt = (
            pg_insert(ProfileInsight)
            .values(**values)
            .on_conflict_do_update(
                constraint="uix_ig_profile_insight_user_date_period",
                set_={metric.name: total},
            )
        )
        async with async_session_factory() as session:
            async with session.begin():
                await session.execute(stmt)
