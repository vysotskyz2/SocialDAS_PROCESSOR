from pydantic_settings import BaseSettings, SettingsConfigDict


class InstagramSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="instagram_", env_file=".env", extra="ignore")

    client_id: str = ""
    client_secret: str = ""
    verify_token: str = ""
    graph_host: str = "https://graph.facebook.com"
    api_version: str = "v24.0"
    tokens_file: str = "tokens.json"
    http_timeout: float = 30.0
