"""Kafka consumer stub for social_feed_service."""

import json
import logging

logger = logging.getLogger("social_feed_service.kafka")

TOPIC_POST_CREATED = "melo.posts.created"


async def handle_post_created(payload: dict) -> None:
    logger.info("Kafka event post.created: %s", payload)


def parse_message(raw: bytes) -> dict:
    return json.loads(raw.decode("utf-8"))
