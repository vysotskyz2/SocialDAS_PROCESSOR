from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    debug: bool = False
    frontend_url: str = ""
    secret_key: SecretStr = SecretStr("dev-secret")


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="kafka_", env_file=".env", extra="ignore")

    bootstrap_servers: str = "localhost:9092"
    group_id: str = "socialdas_processor"
    topic_instagram: str = "instagram"
    topic_tiktok: str = "tiktok"
    topic_youtube: str = "youtube"


class TikTokSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="tiktok_", env_file=".env", extra="ignore")

    client_key: str = ""
    client_secret: str = ""


class YouTubeSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="youtube_", env_file=".env", extra="ignore")

    api_key: str = ""


settings = Settings()
kafka_settings = KafkaSettings()
tiktok_settings = TikTokSettings()
youtube_settings = YouTubeSettings()
