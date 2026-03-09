from loguru import logger

from src.application.services.tiktok_service import TikTokService
from src.infrastructure.kafka.base_consumer import BaseConsumer
from src.infrastructure.repositories.tiktok_repository import TikTokRepository
from src.infrastructure.tokens import TokenNotFoundError
from src.schemas.kafka import KafkaMessage
from src.settings import kafka_settings


class TikTokConsumer(BaseConsumer):
    topic = kafka_settings.topic_tiktok

    async def process_message(self, message: KafkaMessage) -> None:
        tt_user_id = message.account_id
        try:
            # Токен получается и обновляется внутри TikTokService
            service = TikTokService(TikTokRepository(), tt_user_id)
            await service.collect(tt_user_id)
        except TokenNotFoundError:
            logger.warning(f"Токен TikTok для аккаунта {tt_user_id} не найден — пропускаем")
        except RuntimeError as exc:
            # Рефреш-токен истёк — требуется повторная авторизация
            logger.error(f"Ошибка токена TikTok для {tt_user_id}: {exc}")
