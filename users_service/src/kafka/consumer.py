import logging

logger = logging.getLogger("users_service.kafka")


async def handle_user_registered(payload: dict) -> None:
    logger.info("Kafka event user.registered: %s", payload)
