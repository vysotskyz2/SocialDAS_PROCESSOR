from fastapi import APIRouter, HTTPException
from loguru import logger
from pydantic import BaseModel

from src.application.services.tiktok_service import TikTokService
from src.infrastructure.repositories.tiktok_repository import TikTokRepository
from src.infrastructure.tokens import TokenNotFoundError
from src.infrastructure.tiktok_token_manager import save_token_pair
router = APIRouter(prefix="/api/v1", tags=["tiktok"])


@router.post("/analytics/tiktok/{tt_user_id}", summary="Trigger TikTok data collection")
async def collect_tiktok(tt_user_id: str):
    """Ручной запуск сбора данных для TikTok-аккаунта."""
    try:
        service = TikTokService(TikTokRepository(), tt_user_id)
        await service.collect(tt_user_id)
    except TokenNotFoundError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except RuntimeError as exc:
        raise HTTPException(status_code=401, detail=str(exc))
    except Exception as exc:
        logger.exception(f"Сбор данных TikTok завершился с ошибкой для {tt_user_id}")
        raise HTTPException(status_code=502, detail=f"TikTok API error: {exc}")
    return {"status": "ok", "tt_user_id": tt_user_id}


class TikTokTokenRequest(BaseModel):
    access_token: str
    refresh_token: str
    expires_in: int = 86400
    refresh_expires_in: int = 31536000
    scope: str = ""


@router.post("/tiktok/token/{tt_user_id}", summary="Save TikTok token pair")
async def save_tiktok_token(tt_user_id: str, body: TikTokTokenRequest):
    """
    Сохраняет начальную пару токенов доступа и обновления для пользователя TikTok.
    Вызывается после завершения OAuth-потока в сервисе сборщика данных.
    """
    await save_token_pair(
        user_id=tt_user_id,
        access_token=body.access_token,
        refresh_token=body.refresh_token,
        expires_in=body.expires_in,
        refresh_expires_in=body.refresh_expires_in,
        scope=body.scope,
    )
    return {"status": "ok", "tt_user_id": tt_user_id}
