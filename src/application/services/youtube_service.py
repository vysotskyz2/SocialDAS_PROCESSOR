import google.oauth2.credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.concurrency import run_in_threadpool

from src.infrastructure.repositories.youtube_repository import YouTubeRepository
from src.schemas.youtube import YTChannelItem, YTVideoItem
from src.settings import youtube_settings


def _fetch_sync(
    creds: google.oauth2.credentials.Credentials,
    yt_channel_id: str,
    max_per_page: int,
) -> tuple[dict | None, list[dict]]:
    """Синхронный сбор данных канала и всех видео через Google API client."""
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())

    youtube = build("youtube", "v3", credentials=creds)

    # 1. Данные канала
    channel_resp = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=yt_channel_id,
    ).execute()

    if not channel_resp.get("items"):
        return None, []

    channel = channel_resp["items"][0]
    uploads_id = (
        channel.get("contentDetails", {})
        .get("relatedPlaylists", {})
        .get("uploads")
    )
    if not uploads_id:
        return channel, []

    # 2. Все ID видео из плейлиста Uploads (с пагинацией)
    video_ids: list[str] = []
    next_page_token = None
    while True:
        playlist_resp = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=uploads_id,
            maxResults=max_per_page,
            pageToken=next_page_token,
        ).execute()
        for item in playlist_resp.get("items", []):
            video_ids.append(item["contentDetails"]["videoId"])
        next_page_token = playlist_resp.get("nextPageToken")
        if not next_page_token:
            break

    # 3. Детали видео пачками по max_per_page
    videos: list[dict] = []
    for i in range(0, len(video_ids), max_per_page):
        batch = video_ids[i : i + max_per_page]
        videos_resp = youtube.videos().list(
            part="snippet,statistics,contentDetails",
            id=",".join(batch),
        ).execute()
        videos.extend(videos_resp.get("items", []))

    return channel, videos


class YouTubeService:

    def __init__(self, session: AsyncSession, creds: google.oauth2.credentials.Credentials):
        self.session = session
        self.creds = creds

    async def collect(self, yt_channel_id: str) -> None:
        """Загружает информацию о канале и все видео YouTube, сохраняет в БД через переданную сессию."""
        channel_dict, video_dicts = await run_in_threadpool(
            _fetch_sync,
            creds=self.creds,
            yt_channel_id=yt_channel_id,
            max_per_page=youtube_settings.max_videos_per_page,
        )

        if not channel_dict:
            logger.warning(f"Канал {yt_channel_id} не найден на YouTube")
            return

        repo = YouTubeRepository(self.session)
        channel_item = YTChannelItem.model_validate(channel_dict)
        channel_id = await repo.upsert_channel(channel_item)
        await repo.upsert_channel_snapshot(channel_id, channel_item)

        for video_dict in video_dicts:
            try:
                video_item = YTVideoItem.model_validate(video_dict)
                video_id = await repo.upsert_video(channel_id, video_item)
                await repo.upsert_video_snapshot(video_id, video_item)
            except Exception:
                logger.exception(f"Ошибка сохранения видео YouTube {video_dict.get('id')}")

        logger.info(f"Сбор данных YouTube завершён для {yt_channel_id}: {len(video_dicts)} видео")

