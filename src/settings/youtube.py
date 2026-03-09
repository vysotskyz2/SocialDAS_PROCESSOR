from pydantic_settings import BaseSettings, SettingsConfigDict


class YouTubeSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_prefix='youtube_',
        extra='ignore'
    )

    client_id: str = ""
    project_id: str = ""
    client_secret: str = ""
    auth_uri: str = "https://accounts.google.com/o/oauth2/auth"
    token_uri: str = "https://oauth2.googleapis.com/token"
    auth_provider: str = "https://www.googleapis.com/oauth2/v1/certs"
    redirect_uris: str = ""
    javascript_origins: str = ""
    scopes: str = "https://www.googleapis.com/auth/youtube.readonly"
    tokens_file: str = "tokens3.json"
    max_videos_per_page: int = 50

    @property
    def client_config(self) -> dict:
        return {
            "web": {
                "client_id": self.client_id,
                "project_id": self.project_id,
                "auth_uri": self.auth_uri,
                "token_uri": self.token_uri,
                "auth_provider_x509_cert_url": self.auth_provider,
                "client_secret": self.client_secret,
                "redirect_uris": self.redirect_uris.split(",") if self.redirect_uris else [],
                "javascript_origins": self.javascript_origins.split(",") if self.javascript_origins else [],
            }
        }
