import logging

logger = logging.getLogger("media_service.kafka")


async def handle_album_published(payload: dict) -> None:
    logger.info("Kafka event album.published (media): %s", payload)
