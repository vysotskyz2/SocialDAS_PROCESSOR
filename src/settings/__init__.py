from src.settings.app import Settings
from src.settings.kafka import KafkaSettings
from src.settings.instagram import InstagramSettings
from src.settings.tiktok import TikTokSettings
from src.settings.youtube import YouTubeSettings

settings = Settings()
kafka_settings = KafkaSettings()
instagram_settings = InstagramSettings()
tiktok_settings = TikTokSettings()
youtube_settings = YouTubeSettings()

__all__ = [
    "Settings", "KafkaSettings", "InstagramSettings", "TikTokSettings", "YouTubeSettings",
    "settings", "kafka_settings", "instagram_settings", "tiktok_settings", "youtube_settings",
]

