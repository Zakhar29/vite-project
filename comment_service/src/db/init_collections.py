"""Инициализация коллекции comments и валидаторов MongoDB."""

from config import settings
from src.db.mongo_client import mongodb_client
from src.utils.logger import logger

COMMENTS_VALIDATOR = {
    "$and": [
        {
            "$jsonSchema": {
                "bsonType": "object",
                "required": [
                    "author_id",
                    "entity_type",
                    "entity_id",
                    "comment",
                    "created_at",
                ],
                "properties": {
                    "author_id": {
                        "bsonType": "string",
                        "description": "UUID автора комментария",
                    },
                    "entity_type": {
                        "enum": ["post", "track", "album", "playlist"],
                        "description": "тип сущности",
                    },
                    "entity_id": {
                        "bsonType": "string",
                        "description": "UUID или ID сущности",
                    },
                    "answer_id": {
                        "bsonType": ["objectId", "null"],
                        "description": "ID родительского комментария",
                    },
                    "comment": {
                        "bsonType": "string",
                        "minLength": 1,
                        "maxLength": 2000,
                        "description": "текст комментария",
                    },
                    "track_timecode": {
                        "bsonType": ["int", "null"],
                        "minimum": 0,
                        "description": "время на треке (только для track)",
                    },
                    "created_at": {"bsonType": "date"},
                    "updated_at": {"bsonType": ["date", "null"]},
                    "likes_quantity": {"bsonType": "int", "minimum": 0},
                    "dislikes_quantity": {"bsonType": "int", "minimum": 0},
                    "rating_quantity": {"bsonType": "int"},
                    "answer_quantity": {"bsonType": "int", "minimum": 0},
                },
            }
        },
        {
            "$expr": {
                "$or": [
                    {"$eq": ["$entity_type", "track"]},
                    {"$eq": [{"$ifNull": ["$track_timecode", None]}, None]},
                ]
            }
        },
    ]
}


async def init_collections() -> None:
    db = mongodb_client.db
    if db is None:
        raise RuntimeError("MongoDB is not connected")

    name = settings.COMMENTS_COLLECTION
    existing = await db.list_collection_names()

    if name not in existing:
        await db.create_collection(
            name,
            validator=COMMENTS_VALIDATOR,
            validationLevel="strict",
            validationAction="error",
        )
        logger.info("Created collection %s", name)
    else:
        await db.command(
            "collMod",
            name,
            validator=COMMENTS_VALIDATOR,
            validationLevel="strict",
            validationAction="error",
        )
        logger.info("Updated validator for collection %s", name)

    comments = db[name]
    await comments.create_index([("entity_type", 1), ("entity_id", 1), ("created_at", -1)])
    await comments.create_index([("answer_id", 1), ("created_at", -1)])
    await comments.create_index([("author_id", 1), ("created_at", -1)])
