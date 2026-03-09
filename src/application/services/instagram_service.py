from datetime import datetime, timezone

from httpx import AsyncClient
from loguru import logger

from src.infrastructure.repositories.instagram_repository import InstagramRepository
from src.schemas.instagram import IGProfileResponse, IGMediaList, IGInsightList, IGStoryList

GRAPH_HOST = "https://graph.facebook.com"
API_VERSION = "v24.0"
BASE = f"{GRAPH_HOST}/{API_VERSION}"


class InstagramService:

    def __init__(self, repository: InstagramRepository, token: str):
        self.repo = repository
        self.token = token

    async def collect(self, ig_user_id: str, period: str = "day") -> None:
        """Загружает все данные Instagram-аккаунта и сохраняет их."""
        async with AsyncClient(timeout=30.0) as client:
            profile = await self._fetch_profile(client, ig_user_id)
            user_id = await self.repo.upsert_user(profile)
            await self.repo.upsert_user_snapshot(user_id, profile)

            await self._collect_media(client, ig_user_id, user_id)
            await self._collect_insights(client, ig_user_id, user_id, period)
            await self._collect_stories(client, ig_user_id, user_id)

        logger.info("Сбор данных Instagram завершён для {}", ig_user_id)

    async def _fetch_profile(self, client: AsyncClient, ig_user_id: str) -> IGProfileResponse:
        resp = await client.get(
            f"{BASE}/{ig_user_id}",
            params={
                "fields": "id,username,name,profile_picture_url,followers_count,follows_count,"
                          "media_count,biography,website",
                "access_token": self.token,
            },
        )
        resp.raise_for_status()
        return IGProfileResponse.model_validate(resp.json())

    async def _collect_media(self, client: AsyncClient, ig_user_id: str, user_id) -> None:
        resp = await client.get(
            f"{BASE}/{ig_user_id}/media",
            params={
                "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,"
                          "timestamp,like_count,comments_count",
                "access_token": self.token,
            },
        )
        resp.raise_for_status()
        media_list = IGMediaList.model_validate(resp.json())
        for item in media_list.data:
            try:
                await self.repo.upsert_post(user_id, item)
            except Exception:
                logger.exception("Ошибка сохранения поста {}", item.id)

    async def _collect_insights(self, client: AsyncClient, ig_user_id: str, user_id, period: str) -> None:
        resp = await client.get(
            f"{BASE}/{ig_user_id}/insights",
            params={
                "metric": "reach,profile_views,views,likes,comments,website_clicks,shares,saves,replies,reposts",
                "metric_type": "total_value",
                "period": period,
                "access_token": self.token,
            },
        )
        resp.raise_for_status()
        insight_list = IGInsightList.model_validate(resp.json())
        snapshot_date = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        for metric in insight_list.data:
            try:
                await self.repo.upsert_profile_insight(user_id, metric, snapshot_date)
            except Exception:
                logger.exception("Ошибка сохранения метрики {}", metric.name)

    async def _collect_stories(self, client: AsyncClient, ig_user_id: str, user_id) -> None:
        resp = await client.get(
            f"{BASE}/{ig_user_id}/stories",
            params={
                "fields": "id,media_type,media_url,thumbnail_url,timestamp,caption,permalink,"
                          "like_count,comments_count",
                "access_token": self.token,
            },
        )
        resp.raise_for_status()
        story_list = IGStoryList.model_validate(resp.json())
        for item in story_list.data:
            try:
                await self.repo.upsert_story(user_id, item)
            except Exception:
                logger.exception("Ошибка сохранения сторис {}", item.id)
