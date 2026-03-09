import json
from pathlib import Path

from loguru import logger

_BASE = Path(__file__).parent.parent.parent  # project root (src/../)


class TokenNotFoundError(Exception):
    pass


def _load_tokens(filename: str) -> dict:
    path = _BASE / filename
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
            # удаляем служебный ключ из шаблонных файлов
            return {k: v for k, v in data.items() if not k.startswith("_")}
    except FileNotFoundError:
        logger.warning(f"Файл токенов {filename} не найден")
        return {}


# Кеши на уровне модуля — перезагружаются только при старте
_ig_tokens: dict | None = None
_yt_tokens: dict | None = None


def get_instagram_token(user_id: str) -> str:
    global _ig_tokens
    if _ig_tokens is None:
        _ig_tokens = _load_tokens("tokens.json")
    if user_id not in _ig_tokens:
        raise TokenNotFoundError(f"Instagram account {user_id} not connected")
    return _ig_tokens[user_id]


async def get_tiktok_token(user_id: str) -> str:
    """Возвращает валидный токен доступа TikTok, автоматически обновляя его при истечении."""
    from src.infrastructure.tiktok_token_manager import get_valid_access_token
    return await get_valid_access_token(user_id)


def get_youtube_token(channel_id: str) -> str:
    global _yt_tokens
    if _yt_tokens is None:
        _yt_tokens = _load_tokens("tokens3.json")
    if channel_id not in _yt_tokens:
        raise TokenNotFoundError(f"YouTube channel {channel_id} not connected")
    token = _yt_tokens[channel_id]
    # поддерживаем как строку, так и словарь {"api_key": "..."}
    return token if isinstance(token, str) else token["api_key"]


def reload_all() -> None:
    """Принудительная перезагрузка файлов токенов Instagram и YouTube."""
    global _ig_tokens, _yt_tokens
    _ig_tokens = _load_tokens("tokens.json")
    _yt_tokens = _load_tokens("tokens3.json")
    # Кеш TikTok хранится в tiktok_token_manager — сбрасываем там
    from src.infrastructure import tiktok_token_manager
    tiktok_token_manager._cache = None

