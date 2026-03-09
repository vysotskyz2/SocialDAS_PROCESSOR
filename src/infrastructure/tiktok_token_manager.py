"""
Менеджер токенов TikTok.

Формат tokens2.json:
{
  "<tt_open_id>": {
    "access_token":              "act.xxx",
    "refresh_token":             "rft.xxx",
    "expires_at":                "2026-03-09T12:00:00+00:00",
    "refresh_token_expires_at":  "2027-03-08T12:00:00+00:00",
    "scope":                     "user.info.basic,video.list"
  }
}

Токены доступа живут 24 ч. Рефреш-токены — до 365 дней.
get_valid_access_token() автоматически обновляет токен при истечении.
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

import httpx
from loguru import logger

from src.infrastructure.tokens import TokenNotFoundError
from src.settings import tiktok_settings

_BASE = Path(__file__).parent.parent.parent  # project root
_TOKEN_FILE = _BASE / tiktok_settings.tokens_file
_REFRESH_URL = f"{tiktok_settings.base_url}/oauth/token/"
_REFRESH_BUFFER = timedelta(hours=tiktok_settings.refresh_buffer_hours)

# Кеш в памяти (user_id -> данные токена)
_cache: dict[str, dict] | None = None
_lock = asyncio.Lock()


def _load_file() -> dict:
    try:
        with open(_TOKEN_FILE, encoding="utf-8") as f:
            data = json.load(f)
        # обратная совместимость: строка → новый формат (уже просрочен, чтобы сработал рефреш)
        result = {}
        for uid, val in data.items():
            if uid.startswith("_"):
                continue
            if isinstance(val, str):
                result[uid] = {
                    "access_token": val,
                    "refresh_token": "",
                    "expires_at": datetime.now(tz=timezone.utc).isoformat(),
                    "refresh_token_expires_at": (
                        datetime.now(tz=timezone.utc) + timedelta(days=365)
                    ).isoformat(),
                    "scope": "",
                }
            else:
                result[uid] = val
        return result
    except FileNotFoundError:
        logger.warning("Файл tokens2.json не найден")
        return {}


def _save_file(data: dict) -> None:
    with open(_TOKEN_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _parse_dt(value: str) -> datetime:
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def _is_expired(token_data: dict, key: str = "expires_at") -> bool:
    try:
        exp = _parse_dt(token_data[key])
        return datetime.now(tz=timezone.utc) >= exp - _REFRESH_BUFFER
    except (KeyError, ValueError):
        return True


def _is_refresh_token_valid(token_data: dict) -> bool:
    try:
        exp = _parse_dt(token_data["refresh_token_expires_at"])
        return datetime.now(tz=timezone.utc) < exp
    except (KeyError, ValueError):
        return False


async def _do_refresh(user_id: str, token_data: dict) -> dict:
    """Вызывает TikTok /oauth/token с grant_type=refresh_token."""
    from src.settings import tiktok_settings

    if not tiktok_settings.client_key or not tiktok_settings.client_secret:
        raise RuntimeError(
            "TIKTOK_CLIENT_KEY and TIKTOK_CLIENT_SECRET must be set to refresh tokens"
        )

    refresh_token = token_data.get("refresh_token", "")
    if not refresh_token:
        raise RuntimeError(
            f"No refresh_token stored for TikTok user {user_id}. "
            "Re-authorize the account to obtain a new token pair."
        )

    if not _is_refresh_token_valid(token_data):
        raise RuntimeError(
            f"Refresh token for TikTok user {user_id} has expired. "
            "Re-authorize the account."
        )

    async with httpx.AsyncClient(timeout=tiktok_settings.http_timeout) as client:
        resp = await client.post(
            _REFRESH_URL,
            data={
                "client_key": tiktok_settings.client_key,
                "client_secret": tiktok_settings.client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        resp.raise_for_status()
        body = resp.json()

    if "error" in body and body["error"] != "ok":
        raise RuntimeError(
            f"TikTok token refresh failed for {user_id}: "
            f"{body.get('error')} — {body.get('error_description', '')}"
        )

    now = datetime.now(tz=timezone.utc)
    expires_in: int = body.get("expires_in", tiktok_settings.access_token_ttl)
    refresh_expires_in: int = body.get("refresh_expires_in", tiktok_settings.refresh_token_ttl)

    updated = {
        "access_token": body["access_token"],
        "refresh_token": body.get("refresh_token", refresh_token),
        "expires_at": (now + timedelta(seconds=expires_in)).isoformat(),
        "refresh_token_expires_at": (now + timedelta(seconds=refresh_expires_in)).isoformat(),
        "scope": body.get("scope", token_data.get("scope", "")),
    }

    logger.info(f"Токен TikTok обновлён для пользователя {user_id} — новый expires_at={updated['expires_at']}")
    return updated


async def get_valid_access_token(user_id: str) -> str:
    """Возвращает валидный токен доступа, автоматически обновляя его при необходимости."""
    global _cache
    async with _lock:
        if _cache is None:
            _cache = _load_file()

        if user_id not in _cache:
            raise TokenNotFoundError(f"TikTok account {user_id} not connected")

        token_data = _cache[user_id]

        if _is_expired(token_data):
            logger.info(f"Токен доступа TikTok истёк для {user_id}, обновляем...")
            token_data = await _do_refresh(user_id, token_data)
            _cache[user_id] = token_data
            _save_file(_cache)

        return token_data["access_token"]


async def save_token_pair(
    user_id: str,
    access_token: str,
    refresh_token: str,
    expires_in: int = tiktok_settings.access_token_ttl,
    refresh_expires_in: int = tiktok_settings.refresh_token_ttl,
    scope: str = "",
) -> None:
    """Сохраняет начальную или обновлённую пару токенов (например, после OAuth-колбека)."""
    global _cache
    async with _lock:
        if _cache is None:
            _cache = _load_file()

        now = datetime.now(tz=timezone.utc)
        _cache[user_id] = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": (now + timedelta(seconds=expires_in)).isoformat(),
            "refresh_token_expires_at": (now + timedelta(seconds=refresh_expires_in)).isoformat(),
            "scope": scope,
        }
        _save_file(_cache)
    logger.info(f"Новая пара токенов TikTok сохранена для пользователя {user_id}")


async def refresh_all_expiring(buffer: timedelta = timedelta(hours=2)) -> None:
    """Опережающее обновление всех токенов, истекающих в течение `buffer`. Вызывается фоновой задачей."""
    global _cache
    async with _lock:
        if _cache is None:
            _cache = _load_file()
        snapshot = list(_cache.items())

    for user_id, token_data in snapshot:
        try:
            exp = _parse_dt(token_data.get("expires_at", ""))
            if datetime.now(tz=timezone.utc) >= exp - buffer:
                async with _lock:
                    refreshed = await _do_refresh(user_id, token_data)
                    _cache[user_id] = refreshed
                    _save_file(_cache)
        except Exception:
            logger.exception(f"Ошибка опережающего обновления токена TikTok для {user_id}")


def all_user_ids() -> list[str]:
    """Возвращает все ID пользователей TikTok из файла токенов (для фонового обновления)."""
    global _cache
    if _cache is None:
        _cache = _load_file()
    return list(_cache.keys())
