from pydantic_settings import BaseSettings
from src.settings.kafka import KafkaSettings
from src.settings.instagram import InstagramSettings
from src.settings.tiktok import TikTokSettings
from src.settings.youtube import YouTubeSettings
from src.settings.db import DatabaseConfig


class Settings(BaseSettings):
    kafka_settings: KafkaSettings = KafkaSettings()
    instagram_settings: InstagramSettings = InstagramSettings()
    tiktok_settings: TikTokSettings = TikTokSettings()
    youtube_settings: YouTubeSettings = YouTubeSettings()
    db: DatabaseConfig = DatabaseConfig()


settings = Settings()
