from loguru import logger
from google.auth.transport.requests import Request as GoogleRequest
import google.oauth2.credentials
from src.application.services.youtube_service import YouTubeService
from src.infrastructure.database import async_session_factory
from src.infrastructure.kafka.base_consumer import BaseConsumer
from src.schemas.kafka import KafkaMessage
from src.settings import kafka_settings, youtube_settings


class YouTubeConsumer(BaseConsumer):
    topic = kafka_settings.topic_youtube

    async def process_message(self, message: KafkaMessage) -> None:
        yt_channel_id = message.account_id
        try:
            creds = google.oauth2.credentials.Credentials(
                token=message.access_token,
                refresh_token=message.refresh_token,
                token_uri=youtube_settings.token_uri,
                client_id=youtube_settings.client_id,
                client_secret=youtube_settings.client_secret,
            )

            if not creds or not creds.valid:
                if creds and creds.expired and creds.refresh_token:
                    creds.refresh(GoogleRequest())

            async with async_session_factory() as session:
                async with session.begin():
                    await YouTubeService(session, creds).collect(yt_channel_id)
        except RuntimeError as exc:
            logger.error(f"Ошибка токена YouTube для {yt_channel_id}: {exc}")
