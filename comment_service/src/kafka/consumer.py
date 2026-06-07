"""Kafka consumer stub for comment_service."""

import logging

logger = logging.getLogger("comment_service.kafka")

TOPIC_POST_CREATED = "melo.posts.created"


async def handle_post_created(payload: dict) -> None:
    logger.info("Kafka event post.created (comments): %s", payload)
