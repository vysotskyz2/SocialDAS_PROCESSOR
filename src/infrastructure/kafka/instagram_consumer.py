from loguru import logger
from src.application.services.instagram_service import InstagramService
from src.infrastructure.database import async_session_factory
from src.infrastructure.kafka.base_consumer import BaseConsumer
from src.schemas.kafka import KafkaMessage
from src.settings import kafka_settings


class InstagramConsumer(BaseConsumer):
    topic = kafka_settings.topic_instagram

    async def process_message(self, message: KafkaMessage) -> None:
        ig_user_id = message.account_id
        try:
            token = message.access_token
            async with async_session_factory() as session:
                async with session.begin():
                    await InstagramService(session, token).collect(ig_user_id)
        except RuntimeError as exc:
            logger.error(f"Ошибка токена Instagram для {ig_user_id}: {exc}")
