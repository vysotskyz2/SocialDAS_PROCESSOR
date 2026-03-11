from datetime import datetime, timezone
from httpx import AsyncClient
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.repositories.instagram_repository import InstagramRepository
from src.schemas.instagram import IGProfileResponse, IGMediaList, IGInsightList, IGStoryList
from src.settings import instagram_settings


class InstagramService:
    def __init__(self, session: AsyncSession, token: str):
        self.session = session
        self.token = token

    async def collect(self, ig_user_id: str, period: str = "day") -> None:
        """Загружает все данные Instagram-аккаунта и сохраняет их в переданной сессии БД."""
        base = f"{instagram_settings.graph_host}/{instagram_settings.api_version}"
        async with AsyncClient(timeout=instagram_settings.http_timeout) as client:
            profile = await self.fetch_profile(client, ig_user_id, base)
            media_list = await self.fetch_media(client, ig_user_id, base)
            insight_list = await self.fetch_insights(client, ig_user_id, period, base)
            story_list = await self.fetch_stories(client, ig_user_id, base)

        repo = InstagramRepository(self.session)
        user_id = await repo.upsert_user(profile)
        await repo.upsert_user_snapshot(user_id, profile)

        for item in media_list.data:
            try:
                await repo.upsert_post(user_id, item)
            except Exception:
                logger.exception(f"Ошибка сохранения поста {item.id}")

        snapshot_date = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        for metric in insight_list.data:
            try:
                await repo.upsert_profile_insight(user_id, metric, snapshot_date)
            except Exception:
                logger.exception(f"Ошибка сохранения метрики {metric.name}")

        for item in story_list.data:
            try:
                await repo.upsert_story(user_id, item)
            except Exception:
                logger.exception(f"Ошибка сохранения сторис {item.id}")

        logger.info(f"Сбор данных Instagram завершён для {ig_user_id}")

    async def fetch_profile(self, client: AsyncClient, ig_user_id: str, base: str) -> IGProfileResponse:
        resp = await client.get(
            f"{base}/{ig_user_id}",
            params={
                "fields": "id,username,name,profile_picture_url,followers_count,follows_count,"
                          "media_count,biography,website",
                "access_token": self.token,
            },
        )
        resp.raise_for_status()
        return IGProfileResponse.model_validate(resp.json())

    async def fetch_media(self, client: AsyncClient, ig_user_id: str, base: str) -> IGMediaList:
        resp = await client.get(
            f"{base}/{ig_user_id}/media",
            params={
                "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,"
                          "timestamp,like_count,comments_count",
                "access_token": self.token,
            },
        )
        resp.raise_for_status()
        return IGMediaList.model_validate(resp.json())

    async def fetch_insights(self, client: AsyncClient, ig_user_id: str, period: str, base: str) -> IGInsightList:
        resp = await client.get(
            f"{base}/{ig_user_id}/insights",
            params={
                "metric": "reach,profile_views,views,likes,comments,website_clicks,shares,saves,replies,reposts",
                "metric_type": "total_value",
                "period": period,
                "access_token": self.token,
            },
        )
        resp.raise_for_status()
        return IGInsightList.model_validate(resp.json())

    async def fetch_stories(self, client: AsyncClient, ig_user_id: str, base: str) -> IGStoryList:
        resp = await client.get(
            f"{base}/{ig_user_id}/stories",
            params={
                "fields": "id,media_type,media_url,thumbnail_url,timestamp,caption,permalink,"
                          "like_count,comments_count",
                "access_token": self.token,
            },
        )
        resp.raise_for_status()
        return IGStoryList.model_validate(resp.json())
