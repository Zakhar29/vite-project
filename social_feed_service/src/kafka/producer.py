"""Kafka producer stub for social_feed_service."""

import json
import logging
from typing import Any

logger = logging.getLogger("social_feed_service.kafka")


async def publish_event(producer, topic: str, payload: dict[str, Any]) -> None:
    if producer is None:
        logger.debug("Kafka producer disabled, skip %s", topic)
        return
    await producer.send_and_wait(topic, json.dumps(payload, default=str).encode("utf-8"))
