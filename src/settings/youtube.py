from pydantic_settings import BaseSettings, SettingsConfigDict


class YouTubeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='youtube_',
        extra='ignore'
    )

    client_id: str
    project_id: str
    client_secret: str
    token_uri: str
    max_videos_per_page: int = 50
