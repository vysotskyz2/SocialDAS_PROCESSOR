from fastapi import APIRouter, HTTPException
from loguru import logger

from src.application.services.instagram_service import InstagramService
from src.infrastructure.repositories.instagram_repository import InstagramRepository
from src.infrastructure.tokens import get_instagram_token, TokenNotFoundError
router = APIRouter(prefix="/api/v1", tags=["instagram"])


def _get_service(ig_user_id: str) -> InstagramService:
    try:
        token = get_instagram_token(ig_user_id)
    except TokenNotFoundError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    return InstagramService(InstagramRepository(), token)


@router.post("/analytics/instagram/{ig_user_id}", summary="Trigger Instagram data collection")
async def collect_instagram(ig_user_id: str, period: str = "day"):
    """Ручной запуск сбора данных для Instagram-аккаунта."""
    service = _get_service(ig_user_id)
    try:
        await service.collect(ig_user_id, period)
    except Exception as exc:
        logger.exception("Сбор данных Instagram завершился с ошибкой для {}", ig_user_id)
        raise HTTPException(status_code=502, detail=f"Instagram API error: {exc}")
    return {"status": "ok", "ig_user_id": ig_user_id}
