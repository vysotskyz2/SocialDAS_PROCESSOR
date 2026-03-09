import json
from pathlib import Path

import google.oauth2.credentials
from loguru import logger

from src.settings import instagram_settings, youtube_settings

_BASE = Path(__file__).parent.parent.parent  # project root (src/../)


class TokenNotFoundError(Exception):
    pass


def _load_tokens(filename: str) -> dict:
    path = _BASE / filename
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            return {k: v for k, v in data.items() if not k.startswith("_")}
    except FileNotFoundError:
        logger.warning(f"Файл токенов {filename} не найден")
        return {}


_ig_tokens: dict | None = None
_yt_tokens: dict | None = None


def get_instagram_token(user_id: str) -> str:
    global _ig_tokens
    if _ig_tokens is None:
        _ig_tokens = _load_tokens(instagram_settings.tokens_file)
    if user_id not in _ig_tokens:
        raise TokenNotFoundError(f"Instagram account {user_id} not connected")
    return _ig_tokens[user_id]


async def get_tiktok_token(user_id: str) -> str:
    """Возвращает валидный токен доступа TikTok, автоматически обновляя его при истечении."""
    from src.infrastructure.tiktok_token_manager import get_valid_access_token
    return await get_valid_access_token(user_id)


def get_youtube_credentials(channel_id: str) -> google.oauth2.credentials.Credentials:
    """Возвращает Google OAuth2 Credentials для YouTube-канала из tokens3.json."""
    global _yt_tokens
    if _yt_tokens is None:
        _yt_tokens = _load_tokens(youtube_settings.tokens_file)
    if channel_id not in _yt_tokens:
        raise TokenNotFoundError(f"YouTube channel {channel_id} not connected")

    token_data = _yt_tokens[channel_id]
    # поддерживаем строку (refresh_token) и словарь {"refresh_token": "...", "token": "..."}
    if isinstance(token_data, str):
        refresh_token = token_data
        access_token = None
    else:
        refresh_token = token_data.get("refresh_token", "")
        access_token = token_data.get("token") or token_data.get("access_token")

    return google.oauth2.credentials.Credentials(
        token=access_token,
        refresh_token=refresh_token,
        token_uri=youtube_settings.token_uri,
        client_id=youtube_settings.client_id,
        client_secret=youtube_settings.client_secret,
    )


def reload_all() -> None:
    """Принудительная перезагрузка файлов токенов Instagram и YouTube."""
    global _ig_tokens, _yt_tokens
    _ig_tokens = _load_tokens(instagram_settings.tokens_file)
    _yt_tokens = _load_tokens(youtube_settings.tokens_file)
    from src.infrastructure import tiktok_token_manager
    tiktok_token_manager._cache = None

