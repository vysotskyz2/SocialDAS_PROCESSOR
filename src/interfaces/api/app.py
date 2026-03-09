import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI
from loguru import logger

from src.infrastructure.logging_config import setup_logging
from src.interfaces.api.routers.instagram import router as router_inst
from src.interfaces.api.routers.tiktok import router as router_tt
from src.interfaces.api.routers.youtube import router as router_yt

_TOKEN_REFRESH_INTERVAL = 60 * 60  # every hour


async def _tiktok_token_refresh_loop() -> None:
    """Фоновая задача: опережающее обновление токенов TikTok, истекающих в ближайшие 2 часа."""
    from src.infrastructure.tiktok_token_manager import refresh_all_expiring
    from datetime import timedelta
    while True:
        try:
            await refresh_all_expiring(buffer=timedelta(hours=2))
        except Exception:
            logger.exception("Ошибка в цикле обновления токенов TikTok")
        await asyncio.sleep(_TOKEN_REFRESH_INTERVAL)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    from src.infrastructure.kafka.instagram_consumer import InstagramConsumer
    from src.infrastructure.kafka.tiktok_consumer import TikTokConsumer
    from src.infrastructure.kafka.youtube_consumer import YouTubeConsumer

    consumers = [InstagramConsumer(), TikTokConsumer(), YouTubeConsumer()]
    tasks = [asyncio.create_task(c.run()) for c in consumers]
    refresh_task = asyncio.create_task(_tiktok_token_refresh_loop())
    logger.info("Kafka-консьюмеры и цикл обновления токенов TikTok запущены")

    yield

    refresh_task.cancel()
    for task in tasks:
        task.cancel()
    await asyncio.gather(refresh_task, *tasks, return_exceptions=True)
    logger.info("Kafka-консьюмеры и цикл обновления токенов остановлены")


app = FastAPI(lifespan=lifespan, docs_url=None)

app.include_router(router_inst)
app.include_router(router_tt)
app.include_router(router_yt)


@app.get("/health")
async def health():
    return {"status": "ok"}
