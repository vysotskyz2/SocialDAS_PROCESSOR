import json
from abc import ABC, abstractmethod
from aiokafka import AIOKafkaConsumer
from loguru import logger
from pydantic import ValidationError
from src.infrastructure.schemas.kafka import KafkaMessage
from src.settings import settings


class BaseConsumer(ABC):
    """Базовый Kafka-консьюмер. Подклассы реализуют метод `process_message`."""

    topic: str

    def __init__(self) -> None:
        self._consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=settings.kafka_settings.bootstrap_servers,
            group_id=settings.kafka_settings.group_id,
            value_deserializer=lambda m: json.loads(m.decode("utf-8")),
            auto_offset_reset="earliest",
            enable_auto_commit=True,
        )

    async def run(self) -> None:
        await self._consumer.start()
        logger.info(f"Консьюмер запущен для топика '{self.topic}'")
        try:
            async for msg in self._consumer:
                await self._handle(msg.value)
        finally:
            await self._consumer.stop()
            logger.info(f"Консьюмер остановлен для топика '{self.topic}'")

    async def stop(self) -> None:
        await self._consumer.stop()

    async def _handle(self, payload: dict) -> None:
        try:
            message = KafkaMessage.model_validate(payload)
            await self.process_message(message)
        except ValidationError as exc:
            logger.error(f"Некорректное сообщение Kafka в топике '{self.topic}': {exc} | payload={payload}")
            return
        except Exception:
            logger.exception(
                f"Необработанная ошибка при обработке сообщения для аккаунта {payload.get('account_id')} в топике '{self.topic}'"
            )

    @abstractmethod
    async def process_message(self, message: KafkaMessage) -> None: pass
