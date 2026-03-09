import httpx
from httpx import AsyncClient
from loguru import logger

from src.infrastructure.repositories.tiktok_repository import TikTokRepository
from src.infrastructure.tiktok_token_manager import get_valid_access_token, _do_refresh, _cache, _save_file
from src.schemas.tiktok import TTUserInfoResponse, TTVideoListResponse
from src.settings import tiktok_settings

VIDEO_FIELDS = "id,title,video_description,duration,cover_image_url,share_url,like_count,comment_count,share_count,view_count,create_time"


class TikTokService:

    def __init__(self, repository: TikTokRepository, tt_user_id: str):
        self.repo = repository
        self.tt_user_id = tt_user_id

    async def _headers(self) -> dict:
        token = await get_valid_access_token(self.tt_user_id)
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    async def _get(self, client: AsyncClient, url: str, **kwargs) -> httpx.Response:
        """GET-запрос с автоматическим обновлением токена при 401."""
        resp = await client.get(url, headers=await self._headers(), **kwargs)
        if resp.status_code == 401:
            logger.warning(f"TikTok 401 для пользователя {self.tt_user_id} — обновляем токен и повторяем запрос")
            # принудительное обновление, игнорируя кеш
            from src.infrastructure import tiktok_token_manager as mgr
            async with mgr._lock:
                if mgr._cache is None:
                    mgr._cache = mgr._load_file()
                token_data = mgr._cache[self.tt_user_id]
                refreshed = await _do_refresh(self.tt_user_id, token_data)
                mgr._cache[self.tt_user_id] = refreshed
                mgr._save_file(mgr._cache)
            resp = await client.get(url, headers=await self._headers(), **kwargs)
        resp.raise_for_status()
        return resp

    async def _post(self, client: AsyncClient, url: str, **kwargs) -> httpx.Response:
        """POST-запрос с автоматическим обновлением токена при 401."""
        resp = await client.post(url, headers=await self._headers(), **kwargs)
        if resp.status_code == 401:
            logger.warning(f"TikTok 401 для пользователя {self.tt_user_id} — обновляем токен и повторяем запрос")
            from src.infrastructure import tiktok_token_manager as mgr
            async with mgr._lock:
                if mgr._cache is None:
                    mgr._cache = mgr._load_file()
                token_data = mgr._cache[self.tt_user_id]
                refreshed = await _do_refresh(self.tt_user_id, token_data)
                mgr._cache[self.tt_user_id] = refreshed
                mgr._save_file(mgr._cache)
            resp = await client.post(url, headers=await self._headers(), **kwargs)
        resp.raise_for_status()
        return resp

    async def collect(self, tt_user_id: str) -> None:
        """Загружает профиль и список видео TikTok-аккаунта, сохраняет в БД."""
        async with AsyncClient(timeout=tiktok_settings.http_timeout) as client:
            user_data = await self._fetch_user(client)
            if not user_data:
                logger.warning(f"Данные пользователя TikTok {tt_user_id} не получены")
                return

            user_id = await self.repo.upsert_user(user_data)
            await self.repo.upsert_user_snapshot(user_id, user_data)

            await self._collect_videos(client, user_id)

        logger.info(f"Сбор данных TikTok завершён для {tt_user_id}")

    async def _fetch_user(self, client: AsyncClient):
        resp = await self._get(
            client,
            f"{tiktok_settings.base_url}/user/info/",
            params={"fields": "open_id,union_id,avatar_url,display_name,bio_description,"
                              "follower_count,following_count,likes_count,video_count"},
        )
        parsed = TTUserInfoResponse.model_validate(resp.json())
        return parsed.data

    async def _collect_videos(self, client: AsyncClient, user_id, cursor: int = 0, max_count: int = 20) -> None:
        resp = await self._post(
            client,
            f"{tiktok_settings.base_url}/video/list/",
            params={"fields": VIDEO_FIELDS},
            json={"max_count": max_count, "cursor": cursor},
        )
        parsed = TTVideoListResponse.model_validate(resp.json())
        if not parsed.data:
            return

        for item in parsed.data.videos:
            try:
                video_id = await self.repo.upsert_video(user_id, item)
                await self.repo.upsert_video_snapshot(video_id, item)
            except Exception:
                logger.exception(f"Ошибка сохранения видео TikTok {item.id}")
