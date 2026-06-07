import logging

logger = logging.getLogger("music_catalog_service.kafka")


async def handle_album_published(payload: dict) -> None:
    logger.info("Kafka event album.published: %s", payload)
