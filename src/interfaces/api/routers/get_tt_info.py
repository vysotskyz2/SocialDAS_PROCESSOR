from fastapi import APIRouter, HTTPException, Depends
from httpx import AsyncClient
import json
#tt router

def get_token_tt(ig_user_id: str) -> str:
    try:
        with open("tokens2.json", "r", encoding="utf-8") as f:
            tokens = json.load(f)

    except FileNotFoundError:
        raise HTTPException(status_code=401, detail="Tokens file not found")

    if ig_user_id not in tokens:
        raise HTTPException(
            status_code=401,
            detail=f" tiktok account {ig_user_id} not connected"
        )
    return tokens[ig_user_id]


async def get_api_client() -> AsyncClient:
    async with AsyncClient() as client:
        yield client


# --- Конфигурация TikTok ---
TIKTOK_CONFIG = {
    "base_url": "https://open.tiktokapis.com/v2",
}

router = APIRouter( tags=["tiktok_analytics"])


# --- Вспомогательные функции ---
def get_token_tt(tt_user_id: str) -> str:
    """Загрузка токена из файла tokens2.json"""
    try:
        with open("tokens2.json", "r", encoding="utf-8") as f:
            tokens = json.load(f)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Tokens file (tokens2.json) not found")

    if tt_user_id not in tokens:
        raise HTTPException(
            status_code=401,
            detail=f"TikTok account {tt_user_id} not connected"
        )
    return tokens[tt_user_id]


async def get_api_client() -> AsyncClient:
    async with AsyncClient() as client:
        yield client


# --- Эндпоинты ---

@router.get("/api/v1/tiktok/analytics/{tt_user_id}")
async def get_full_tiktok_analytics(
        tt_user_id: str,
        api_client: AsyncClient = Depends(get_api_client)
):
    """Сводная аналитика: профиль + последние видео"""
    token = get_token_tt(tt_user_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # 1. Запрос данных профиля (GET)
    # Важно: В v2 поля передаются через query-параметр 'fields'
    user_info_url = f"{TIKTOK_CONFIG['base_url']}/user/info/"
    user_params = {
        "fields": "open_id,union_id,avatar_url,display_name,bio_description,follower_count,following_count,likes_count,video_count"
    }

    # 2. Запрос списка видео (POST)
    video_list_url = f"{TIKTOK_CONFIG['base_url']}/video/list/"
    video_params = {
        "fields": "id,title,video_description,duration,cover_image_url,embed_link,share_url,like_count,comment_count,share_count,view_count,create_time"
    }
    video_body = {
        "max_count": 10,
        "cursor": 0
    }

    try:
        # Выполняем запросы параллельно для скорости
        user_response = await api_client.get(user_info_url, params=user_params, headers=headers)
        video_response = await api_client.post(video_list_url, params=video_params, json=video_body, headers=headers)

        user_data = user_response.json()
        video_data = video_response.json()

        return {
            "profile": user_data.get("data", {}),
            "videos": video_data.get("data", {}),
            "status": {
                "profile_code": user_data.get("error", {}).get("code", "ok"),
                "videos_code": video_data.get("error", {}).get("code", "ok")
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TikTok API Connection Error: {str(e)}")


@router.get("/api/v1/tiktok/video-list/{tt_user_id}")
async def get_only_videos(
        tt_user_id: str,
        cursor: int = 0,
        max_count: int = 20,
        api_client: AsyncClient = Depends(get_api_client)
):
    """Только список видео с поддержкой пагинации"""
    token = get_token_tt(tt_user_id)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    url = f"{TIKTOK_CONFIG['base_url']}/video/list/"
    params = {"fields": "id,title,like_count,comment_count,view_count,create_time,cover_image_url"}
    body = {"max_count": max_count, "cursor": cursor}

    response = await api_client.post(url, params=params, json=body, headers=headers)
    return response.json()