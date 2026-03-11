from pydantic_settings import BaseSettings, SettingsConfigDict


class TikTokSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="tiktok_",
        env_file=".env",
        extra="ignore"
    )

    client_key: str
    client_secret: str
    base_url: str
    http_timeout: float = 30.0
    access_token_ttl: int = 86400
    refresh_token_ttl: int = 31536000
    refresh_buffer_hours: int = 1
    refresh_interval_seconds: int = 3600
    proactive_refresh_buffer_hours: int = 2
