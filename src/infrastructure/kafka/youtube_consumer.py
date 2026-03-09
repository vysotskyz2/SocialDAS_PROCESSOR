from loguru import logger

from src.application.services.youtube_service import YouTubeService
from src.infrastructure.database import async_session_factory
from src.infrastructure.kafka.base_consumer import BaseConsumer
from src.infrastructure.tokens import get_youtube_credentials, TokenNotFoundError
from src.schemas.kafka import KafkaMessage
from src.settings import kafka_settings


class YouTubeConsumer(BaseConsumer):
    topic = kafka_settings.topic_youtube

    async def process_message(self, message: KafkaMessage) -> None:
        yt_channel_id = message.account_id
        try:
            creds = get_youtube_credentials(yt_channel_id)
        except TokenNotFoundError:
            logger.warning(f"Credentials YouTube для канала {yt_channel_id} не найдены — пропускаем")
            return

        async with async_session_factory() as session:
            async with session.begin():
                await YouTubeService(session, creds).collect(yt_channel_id)
