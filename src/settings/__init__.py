from src.settings.kafka import KafkaSettings
from src.settings.instagram import InstagramSettings
from src.settings.tiktok import TikTokSettings
from src.settings.youtube import YouTubeSettings
from src.settings.db import DatabaseConfig

kafka_settings = KafkaSettings()
instagram_settings = InstagramSettings()
tiktok_settings = TikTokSettings()
youtube_settings = YouTubeSettings()
db = DatabaseConfig

__all__ = [
    "KafkaSettings", "InstagramSettings", "TikTokSettings", "YouTubeSettings", "DatabaseConfig",
    "kafka_settings", "instagram_settings", "tiktok_settings", "youtube_settings", "db"
]
