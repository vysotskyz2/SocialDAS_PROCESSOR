from pydantic_settings import BaseSettings, SettingsConfigDict


class TikTokSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="tiktok_", env_file=".env", extra="ignore")

    client_key: str = ""
    client_secret: str = ""
    base_url: str = "https://open.tiktokapis.com/v2"
    tokens_file: str = "tokens2.json"
    http_timeout: float = 30.0
    access_token_ttl: int = 86400        # seconds (24 h)
    refresh_token_ttl: int = 31536000    # seconds (365 d)
    refresh_buffer_hours: int = 1        # refresh access token this many hours before expiry
    refresh_interval_seconds: int = 3600  # background proactive-refresh loop interval
    proactive_refresh_buffer_hours: int = 2  # proactively refresh if expiring within N hours
