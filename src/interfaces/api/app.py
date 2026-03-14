import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from loguru import logger
from src.infrastructure.logging_config import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logging()
    from src.infrastructure.kafka.instagram_consumer import InstagramConsumer
    from src.infrastructure.kafka.tiktok_consumer import TikTokConsumer
    from src.infrastructure.kafka.youtube_consumer import YouTubeConsumer

    consumers = [InstagramConsumer(), TikTokConsumer(), YouTubeConsumer()]
    tasks = [asyncio.create_task(c.run()) for c in consumers]
    logger.info("Kafka-консьюмеры и цикл обновления токенов TikTok запущены")

    yield

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Kafka-консьюмеры и цикл обновления токенов остановлены")


app = FastAPI(
    lifespan=lifespan,
    docs_url=None
)


@app.get("/health")
async def health():
    return {"status": "ok"}
