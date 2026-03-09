from fastapi import APIRouter, HTTPException, Depends
from httpx import AsyncClient

from src.infrastructure.tokens import get_tiktok_token, TokenNotFoundError
from src.settings import tiktok_settings


async def get_api_client() -> AsyncClient:
    async with AsyncClient() as client:
        yield client


router = APIRouter(tags=["tiktok_analytics"])


async def _get_token_tt(tt_user_id: str) -> str:
    try:
        return await get_tiktok_token(tt_user_id)
    except TokenNotFoundError:
        raise HTTPException(status_code=401, detail=f"TikTok account {tt_user_id} not connected")


# --- Эндпоинты ---

@router.get("/api/v1/tiktok/analytics/{tt_user_id}")
async def get_full_tiktok_analytics(
        tt_user_id: str,
        api_client: AsyncClient = Depends(get_api_client)
):
    """Сводная аналитика: профиль + последние видео"""
    token = await _get_token_tt(tt_user_id)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    user_info_url = f"{tiktok_settings.base_url}/user/info/"
    user_params = {
        "fields": "open_id,union_id,avatar_url,display_name,bio_description,follower_count,following_count,likes_count,video_count"
    }

    video_list_url = f"{tiktok_settings.base_url}/video/list/"
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
    token = await _get_token_tt(tt_user_id)
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    url = f"{tiktok_settings.base_url}/video/list/"
    params = {"fields": "id,title,like_count,comment_count,view_count,create_time,cover_image_url"}
    body = {"max_count": max_count, "cursor": cursor}

    response = await api_client.post(url, params=params, json=body, headers=headers)
    return response.json()