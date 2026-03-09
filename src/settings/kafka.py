from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="kafka_", env_file=".env", extra="ignore")

    bootstrap_servers: str = "localhost:9092"
    group_id: str = "socialdas_processor"
    topic_instagram: str = "instagram"
    topic_tiktok: str = "tiktok"
    topic_youtube: str = "youtube"
