import json
import logging
from typing import Any

from aiokafka import AIOKafkaProducer

from config import settings
from src.kafka.topics import TOPIC_ALBUM_PUBLISHED, TOPIC_POST_CREATED, TOPIC_USER_REGISTERED

logger = logging.getLogger("gateway_service.kafka")


class EventProducer:
    def __init__(self):
        self._producer: AIOKafkaProducer | None = None

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            client_id=settings.KAFKA_CLIENT_ID,
            value_serializer=lambda v: json.dumps(v, default=str).encode("utf-8"),
        )
        await self._producer.start()
        logger.info("Kafka producer started")

    async def stop(self) -> None:
        if self._producer:
            await self._producer.stop()
            logger.info("Kafka producer stopped")

    async def publish(self, topic: str, payload: dict[str, Any]) -> None:
        if not self._producer:
            logger.warning("Kafka producer not ready, skip event %s", topic)
            return
        await self._producer.send_and_wait(topic, payload)

    async def post_created(self, payload: dict[str, Any]) -> None:
        await self.publish(TOPIC_POST_CREATED, payload)

    async def album_published(self, payload: dict[str, Any]) -> None:
        await self.publish(TOPIC_ALBUM_PUBLISHED, payload)

    async def user_registered(self, payload: dict[str, Any]) -> None:
        await self.publish(TOPIC_USER_REGISTERED, payload)


event_producer = EventProducer()
