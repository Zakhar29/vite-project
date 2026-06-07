"""Инициализация коллекций MongoDB и JSON Schema валидаторов."""

from config import settings
from src.db.mongo_client import mongodb_client
from src.utils.logger import logger

POSTS_VALIDATOR = {
    "$and": [
        {
            "$jsonSchema": {
                "bsonType": "object",
                "required": ["author_id", "created_at"],
                "properties": {
                    "author_id": {
                        "bsonType": "string",
                        "description": "UUID автора",
                    },
                    "text": {
                        "bsonType": ["string", "null"],
                        "maxLength": 5000,
                        "description": "текст поста",
                    },
                    "media": {
                        "bsonType": "array",
                        "maxItems": 11,
                        "items": {
                            "bsonType": "object",
                            "required": ["type", "url"],
                            "properties": {
                                "type": {
                                    "enum": ["image", "video", "audio"],
                                    "description": "тип медиа",
                                },
                                "url": {
                                    "bsonType": "string",
                                    "description": "ссылка на файл в S3",
                                },
                            },
                            "additionalProperties": False,
                        },
                    },
                    "created_at": {
                        "bsonType": "date",
                    },
                    "updated_at": {
                        "bsonType": ["date", "null"],
                    },
                    "likes_quantity": {
                        "bsonType": "int",
                        "minimum": 0,
                    },
                    "comments_quantity": {
                        "bsonType": "int",
                        "minimum": 0,
                    },
                },
            }
        },
        {
            "$expr": {
                "$let": {
                    "vars": {"m": {"$ifNull": ["$media", []]}},
                    "in": {
                        "$and": [
                            {
                                "$lte": [
                                    {
                                        "$size": {
                                            "$filter": {
                                                "input": "$$m",
                                                "as": "item",
                                                "cond": {"$eq": ["$$item.type", "image"]},
                                            }
                                        }
                                    },
                                    5,
                                ]
                            },
                            {
                                "$lte": [
                                    {
                                        "$size": {
                                            "$filter": {
                                                "input": "$$m",
                                                "as": "item",
                                                "cond": {"$eq": ["$$item.type", "video"]},
                                            }
                                        }
                                    },
                                    1,
                                ]
                            },
                            {
                                "$lte": [
                                    {
                                        "$size": {
                                            "$filter": {
                                                "input": "$$m",
                                                "as": "item",
                                                "cond": {"$eq": ["$$item.type", "audio"]},
                                            }
                                        }
                                    },
                                    5,
                                ]
                            },
                        ]
                    },
                }
            }
        },
    ]
}


async def init_collections() -> None:
    db = mongodb_client.db
    if db is None:
        raise RuntimeError("MongoDB is not connected")

    collection_name = settings.POSTS_COLLECTION
    existing = await db.list_collection_names()

    if collection_name not in existing:
        await db.create_collection(
            collection_name,
            validator=POSTS_VALIDATOR,
            validationLevel="strict",
            validationAction="error",
        )
        logger.info("Created collection %s with validator", collection_name)
    else:
        await db.command(
            "collMod",
            collection_name,
            validator=POSTS_VALIDATOR,
            validationLevel="strict",
            validationAction="error",
        )
        logger.info("Updated validator for collection %s", collection_name)

    posts = db[collection_name]
    await posts.create_index([("author_id", 1), ("created_at", -1)])
    await posts.create_index([("created_at", -1)])
