from loguru import logger

from src.application.services.instagram_service import InstagramService
from src.infrastructure.kafka.base_consumer import BaseConsumer
from src.infrastructure.repositories.instagram_repository import InstagramRepository
from src.infrastructure.tokens import get_instagram_token, TokenNotFoundError
from src.schemas.kafka import KafkaMessage
from src.settings import kafka_settings


class InstagramConsumer(BaseConsumer):
    topic = kafka_settings.topic_instagram

    async def process_message(self, message: KafkaMessage) -> None:
        ig_user_id = message.account_id
        try:
            token = get_instagram_token(ig_user_id)
        except TokenNotFoundError:
            logger.warning(f"Токен Instagram для аккаунта {ig_user_id} не найден")
            return

        service = InstagramService(InstagramRepository(), token)
        await service.collect(ig_user_id)
