import asyncio
from src.application.services.instagram_service import InstagramService
from src.application.services.tiktok_service import TikTokService
from src.application.services.youtube_service import YouTubeService

# Используй mock-репозиторий чтобы не нужна была БД
class MockRepo:
   async def upsert_user(self, *a, **kw): print("upsert_user", a); return "fake-uuid"
   async def upsert_user_snapshot(self, *a, **kw): print("upsert_user_snapshot")
   async def upsert_post(self, *a, **kw): print("upsert_post"); return "fake-uuid"
   async def upsert_story(self, *a, **kw): print("upsert_story")
   async def upsert_profile_insight(self, *a, **kw): print("upsert_insight")

async def main():
   # Instagram
   from src.infrastructure.tokens import get_instagram_token
   ig_id = "17841480728603779"  # твой реальный IG user ID из tokens.json
   token = get_instagram_token(ig_id)
   svc = InstagramService(MockRepo(), token)
   await svc.collect(ig_id)

asyncio.run(main())
