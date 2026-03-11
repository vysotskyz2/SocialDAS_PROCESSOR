from loguru import logger
from src.application.services.tiktok_service import TikTokService
from src.infrastructure.database import async_session_factory
from src.infrastructure.kafka.base_consumer import BaseConsumer
from src.schemas.kafka import KafkaMessage
from src.settings import kafka_settings


class TikTokConsumer(BaseConsumer):
    topic = kafka_settings.topic_tiktok

    async def process_message(self, message: KafkaMessage) -> None:
        tt_user_id = message.account_id
        try:
            token = message.access_token
            async with async_session_factory() as session:
                async with session.begin():
                    await TikTokService(session, token, tt_user_id).collect(tt_user_id)
        except RuntimeError as exc:
            logger.error(f"Ошибка токена TikTok для {tt_user_id}: {exc}")
