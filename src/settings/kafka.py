from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="kafka_",
        env_file=".env",
        extra="ignore"
    )

    bootstrap_servers: str
    group_id: str
    topic_instagram: str
    topic_tiktok: str
    topic_youtube: str
