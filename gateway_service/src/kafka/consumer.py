import json
import logging

from aiokafka import AIOKafkaConsumer

from config import settings
from src.kafka.topics import TOPIC_ALBUM_PUBLISHED, TOPIC_POST_CREATED, TOPIC_USER_REGISTERED

logger = logging.getLogger("gateway_service.kafka")


class EventConsumer:
    def __init__(self):
        self._consumer: AIOKafkaConsumer | None = None

    async def start(self) -> None:
        self._consumer = AIOKafkaConsumer(
            TOPIC_POST_CREATED,
            TOPIC_ALBUM_PUBLISHED,
            TOPIC_USER_REGISTERED,
            bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
            group_id="gateway_service_group",
            value_deserializer=lambda v: json.loads(v.decode("utf-8")),
            auto_offset_reset="earliest",
        )
        await self._consumer.start()
        logger.info("Kafka consumer started")

    async def stop(self) -> None:
        if self._consumer:
            await self._consumer.stop()

    async def run(self) -> None:
        if not self._consumer:
            return
        async for message in self._consumer:
            logger.info(
                "Event received topic=%s payload=%s",
                message.topic,
                message.value,
            )


event_consumer = EventConsumer()
