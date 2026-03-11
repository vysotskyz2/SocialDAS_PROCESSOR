import httpx
from httpx import AsyncClient
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from src.infrastructure.repositories.tiktok_repository import TikTokRepository
from src.schemas.tiktok import TTUserInfoResponse, TTVideoListResponse
from src.settings import tiktok_settings

VIDEO_FIELDS = ("id,title,video_description,duration,cover_image_url,share_url,"
                "like_count,comment_count,share_count,view_count,create_time")


class TikTokService:
    def __init__(self, session: AsyncSession, token: str, tt_user_id: str):
        self.session = session
        self.token = token
        self.tt_user_id = tt_user_id

    @property
    def _headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    async def _get(self, client: AsyncClient, url: str, **kwargs) -> httpx.Response:
        resp = await client.get(url, headers=self._headers, **kwargs)
        resp.raise_for_status()
        return resp

    async def _post(self, client: AsyncClient, url: str, **kwargs) -> httpx.Response:
        resp = await client.post(url, headers=self._headers, **kwargs)
        resp.raise_for_status()
        return resp

    async def collect(self, tt_user_id: str) -> None:
        """Загружает профиль и список видео TikTok-аккаунта, сохраняет в БД через переданную сессию."""
        async with AsyncClient(timeout=tiktok_settings.http_timeout) as client:
            user_data = await self.fetch_user(client)
            if not user_data:
                logger.warning(f"Данные пользователя TikTok {tt_user_id} не получены")
                return
            video_list = await self.fetch_videos(client)

        repo = TikTokRepository(self.session)
        user_id = await repo.upsert_user(user_data)
        await repo.upsert_user_snapshot(user_id, user_data)
        for item in video_list:
            try:
                video_id = await repo.upsert_video(user_id, item)
                await repo.upsert_video_snapshot(video_id, item)
            except Exception:
                logger.exception(f"Ошибка сохранения видео TikTok {item.id}")

        logger.info(f"Сбор данных TikTok завершён для {tt_user_id}")

    async def fetch_user(self, client: AsyncClient):
        resp = await self._get(
            client,
            f"{tiktok_settings.base_url}/user/info/",
            params={"fields": "open_id,union_id,avatar_url,display_name,bio_description,"
                              "follower_count,following_count,likes_count,video_count"},
        )
        parsed = TTUserInfoResponse.model_validate(resp.json())
        return parsed.data

    async def fetch_videos(self, client: AsyncClient, cursor: int = 0, max_count: int = 20) -> list:
        resp = await self._post(
            client,
            f"{tiktok_settings.base_url}/video/list/",
            params={"fields": VIDEO_FIELDS},
            json={"max_count": max_count, "cursor": cursor},
        )
        parsed = TTVideoListResponse.model_validate(resp.json())
        return parsed.data.videos if parsed.data else []
