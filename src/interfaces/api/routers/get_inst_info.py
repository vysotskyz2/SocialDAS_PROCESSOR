from fastapi import APIRouter, HTTPException, Depends
from httpx import AsyncClient
import json
#instagram router

def get_token_ig(ig_user_id: str) -> str:
    try:
        with open("tokens.json", "r", encoding="utf-8") as f:
            tokens = json.load(f)

    except FileNotFoundError:
        raise HTTPException(status_code=401, detail="Tokens file not found")

    if ig_user_id not in tokens:
        raise HTTPException(
            status_code=401,
            detail=f" instagram account {ig_user_id} not connected"
        )
    return tokens[ig_user_id]



async def get_api_client() -> AsyncClient:
    async with AsyncClient() as client:
        yield client


BASE_URL = "https://socialdas-ig.loca.lt/"
TT_BASE_URL = "https://open.tiktokapis.com/v2"
INSTAGRAM_CONFIG = {
    "client_id": "1120894473412015",
    "client_secret": "b0cabfd4ed1f3aeb3f2fae79e1951518",
    "redirect_uri": f"{BASE_URL}/api/v1/auth/instagram/callback",
    "api_version": "v24.0",
    "graph_host": "https://graph.facebook.com/",
    "verify_token": "socialdas_webhook_verify_2026"
}

router = APIRouter(tags=["instagram"])

#instagram
@router.get("/api/v1/analytics/instagram/{ig_user_id}")
async def get_insights(
        ig_user_id: str,
        period: str = "day",
        api_client: AsyncClient = Depends(get_api_client)
):
    token = get_token_ig(ig_user_id)

    data = {}
    urls = {
        'profile_data': (
            f"{INSTAGRAM_CONFIG['graph_host']}/{INSTAGRAM_CONFIG['api_version']}/{ig_user_id}",
            {
                "fields": "id,username,name,profile_picture_url,followers_count,follows_count,media_count,biography,"
                          "website",
                "access_token": token
            }),
        'media_data': (
            f"{INSTAGRAM_CONFIG['graph_host']}/{INSTAGRAM_CONFIG['api_version']}/{ig_user_id}/media",
            {
                "fields": "id,caption,media_type,media_url,thumbnail_url,permalink,"
                          "timestamp,like_count,comments_count",
                "access_token": token
            }),
        'reach_data': (
            f"{INSTAGRAM_CONFIG['graph_host']}/{INSTAGRAM_CONFIG['api_version']}/{ig_user_id}/insights",
            {
                "metric": "reach,profile_views,views,likes,comments,website_clicks,shares,saves,replies,reposts",
                "metric_type": "total_value",
                "period": period,
                "access_token": token
            }),
        'demographic_data': (
            f"{INSTAGRAM_CONFIG['graph_host']}/{INSTAGRAM_CONFIG['api_version']}/{ig_user_id}/insights",
            {
                "metric": "follower_demographics",
                "breakdown": "age,gender,country",
                "metric_type": "total_value",
                "period": "lifetime",
                "access_token": token
            }
        ),
        'stories_data': (
            f"{INSTAGRAM_CONFIG['graph_host']}/{INSTAGRAM_CONFIG['api_version']}/{ig_user_id}/stories",
            {
                "fields": "id,media_type,media_url,thumbnail_url,timestamp,owner,"
                          "caption,permalink,like_count,comments_count",
                "access_token": token
            }
        )
    }
    for resource, url in urls.items():
        response = await api_client.get(url[0], params=url[1])
        res = response.json()
        if 'data' in data:
            data[resource] = res.get('data')
        else:
            data[resource] = res
    return data

@router.get("/api/v1/instagram/media/{media_id}/insights")
async def get_media_insights(
        media_id: int,
        ig_user_id: str,
        api_client: AsyncClient = Depends(get_api_client)
):
    token = get_token_ig(ig_user_id)

    data = {}

    urls = {
        'media_insights': (
            f"{INSTAGRAM_CONFIG['graph_host']}/{INSTAGRAM_CONFIG['api_version']}/{media_id}/insights",
            {
                "metric": "reach,saved,views,comments,shares",
                "access_token": token
            }),
        'comments_insights': (
            f"{INSTAGRAM_CONFIG['graph_host']}/{INSTAGRAM_CONFIG['api_version']}/{media_id}/comments",
            {
                "fields": "id,text,username,timestamp,like_count,replies{id,text,username,timestamp}",
                "access_token": token
            })
    }

    for resource, url in urls.items():
        response = await api_client.get(url[0], params=url[1])
        res = response.json()
        if 'data' in res:

            data[resource] = res['data']
        else:
            data[resource] = response

    return data

