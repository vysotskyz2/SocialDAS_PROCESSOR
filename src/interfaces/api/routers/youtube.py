from fastapi import APIRouter, HTTPException
from loguru import logger

from src.application.services.youtube_service import YouTubeService
from src.infrastructure.repositories.youtube_repository import YouTubeRepository
from src.infrastructure.tokens import get_youtube_credentials, TokenNotFoundError

router = APIRouter(prefix="/api/v1", tags=["youtube"])


def _get_service(yt_channel_id: str) -> YouTubeService:
    try:
        creds = get_youtube_credentials(yt_channel_id)
    except TokenNotFoundError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    return YouTubeService(YouTubeRepository(), creds)


@router.post("/analytics/youtube/{yt_channel_id}", summary="Trigger YouTube data collection")
async def collect_youtube(yt_channel_id: str):
    """Ручной запуск сбора данных для YouTube-канала."""
    service = _get_service(yt_channel_id)
    try:
        await service.collect(yt_channel_id)
    except Exception as exc:
        logger.exception(f"Сбор данных YouTube завершился с ошибкой для {yt_channel_id}")
        raise HTTPException(status_code=502, detail=f"YouTube API error: {exc}")
    return {"status": "ok", "yt_channel_id": yt_channel_id}
