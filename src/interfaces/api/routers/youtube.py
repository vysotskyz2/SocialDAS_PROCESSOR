from fastapi import APIRouter, Depends, HTTPException
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.services.youtube_service import YouTubeService
from src.interfaces.dependencies import get_db_session
from src.infrastructure.tokens import get_youtube_credentials, TokenNotFoundError

router = APIRouter(prefix="/api/v1", tags=["youtube"])


@router.post("/analytics/youtube/{yt_channel_id}", summary="Trigger YouTube data collection")
async def collect_youtube(
    yt_channel_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """Ручной запуск сбора данных для YouTube-канала."""
    try:
        creds = get_youtube_credentials(yt_channel_id)
    except TokenNotFoundError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    try:
        await YouTubeService(session, creds).collect(yt_channel_id)
    except Exception as exc:
        logger.exception(f"Сбор данных YouTube завершился с ошибкой для {yt_channel_id}")
        raise HTTPException(status_code=502, detail=f"YouTube API error: {exc}")
    return {"status": "ok", "yt_channel_id": yt_channel_id}
