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
