from loguru import logger

from src.application.services.youtube_service import YouTubeService
from src.infrastructure.kafka.base_consumer import BaseConsumer
from src.infrastructure.repositories.youtube_repository import YouTubeRepository
from src.infrastructure.tokens import get_youtube_token, TokenNotFoundError
from src.schemas.kafka import KafkaMessage
from src.settings import kafka_settings


class YouTubeConsumer(BaseConsumer):
    topic = kafka_settings.topic_youtube

    async def process_message(self, message: KafkaMessage) -> None:
        yt_channel_id = message.account_id
        try:
            api_key = get_youtube_token(yt_channel_id)
        except TokenNotFoundError:
            logger.warning("API-ключ YouTube для канала {} не найден — пропускаем", yt_channel_id)
            return

        service = YouTubeService(YouTubeRepository(), api_key)
        await service.collect(yt_channel_id)
