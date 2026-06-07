"""Kafka producer stub for comment_service."""

import json
import logging
from typing import Any

logger = logging.getLogger("comment_service.kafka")


async def publish_event(producer, topic: str, payload: dict[str, Any]) -> None:
    if producer is None:
        return
    await producer.send_and_wait(topic, json.dumps(payload, default=str).encode("utf-8"))
