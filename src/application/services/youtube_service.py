from httpx import AsyncClient
from loguru import logger

from src.infrastructure.repositories.youtube_repository import YouTubeRepository
from src.schemas.youtube import YTChannelListResponse, YTSearchResponse, YTVideoListResponse

YT_BASE = "https://www.googleapis.com/youtube/v3"
CHANNEL_PARTS = "snippet,statistics"
VIDEO_PARTS = "snippet,statistics,contentDetails"
MAX_VIDEOS_PER_PAGE = 50


class YouTubeService:

    def __init__(self, repository: YouTubeRepository, api_key: str):
        self.repo = repository
        self.api_key = api_key

    async def collect(self, yt_channel_id: str) -> None:
        """Загружает информацию о канале и последние видео YouTube, сохраняет в БД."""
        async with AsyncClient(timeout=30.0) as client:
            channel_item = await self._fetch_channel(client, yt_channel_id)
            if not channel_item:
                logger.warning("Канал {} не найден на YouTube", yt_channel_id)
                return

            channel_id = await self.repo.upsert_channel(channel_item)
            await self.repo.upsert_channel_snapshot(channel_id, channel_item)

            await self._collect_videos(client, yt_channel_id, channel_id)

        logger.info("Сбор данных YouTube завершён для {}", yt_channel_id)

    async def _fetch_channel(self, client: AsyncClient, yt_channel_id: str):
        resp = await client.get(
            f"{YT_BASE}/channels",
            params={"part": CHANNEL_PARTS, "id": yt_channel_id, "key": self.api_key},
        )
        resp.raise_for_status()
        parsed = YTChannelListResponse.model_validate(resp.json())
        return parsed.items[0] if parsed.items else None

    async def _collect_videos(self, client: AsyncClient, yt_channel_id: str, channel_id) -> None:
        # Шаг 1: получаем ID видео через поиск
        search_resp = await client.get(
            f"{YT_BASE}/search",
            params={
                "part": "snippet",
                "channelId": yt_channel_id,
                "type": "video",
                "order": "date",
                "maxResults": MAX_VIDEOS_PER_PAGE,
                "key": self.api_key,
            },
        )
        search_resp.raise_for_status()
        search_data = YTSearchResponse.model_validate(search_resp.json())

        video_ids = [
            item.id["videoId"]
            for item in search_data.items
            if item.id and item.id.get("videoId")
        ]
        if not video_ids:
            return

        # Шаг 2: загружаем полные данные видео одним запросом
        details_resp = await client.get(
            f"{YT_BASE}/videos",
            params={
                "part": VIDEO_PARTS,
                "id": ",".join(video_ids),
                "key": self.api_key,
            },
        )
        details_resp.raise_for_status()
        details_data = YTVideoListResponse.model_validate(details_resp.json())

        for item in details_data.items:
            try:
                video_id = await self.repo.upsert_video(channel_id, item)
                await self.repo.upsert_video_snapshot(video_id, item)
            except Exception:
                logger.exception("Ошибка сохранения видео YouTube {}", item.id)
