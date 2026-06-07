from datetime import datetime, timezone
from typing import Any, Optional
from uuid import UUID

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from pymongo.errors import DocumentTooLarge, WriteError

from config import settings
from src.api.schemas import MediaItem, PostCreate, PostUpdate
from src.db.mongo_client import mongodb_client


def _serialize_post(doc: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": str(doc["_id"]),
        "author_id": doc["author_id"],
        "text": doc.get("text"),
        "media": doc.get("media") or [],
        "created_at": doc["created_at"],
        "updated_at": doc.get("updated_at"),
        "likes_quantity": doc.get("likes_quantity", 0),
        "comments_quantity": doc.get("comments_quantity", 0),
    }


def _media_to_bson(media: list[MediaItem]) -> list[dict[str, str]]:
    return [item.model_dump() for item in media]


class PostService:
    def __init__(self):
        self.collection = mongodb_client.get_collection(settings.POSTS_COLLECTION)

    @staticmethod
    def _parse_post_id(post_id: str) -> ObjectId:
        try:
            return ObjectId(post_id)
        except InvalidId as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid post id",
            ) from exc

    async def create(self, author_id: UUID, data: PostCreate) -> dict[str, Any]:
        now = datetime.now(timezone.utc)
        document = {
            "author_id": str(author_id),
            "text": data.text,
            "media": _media_to_bson(data.media),
            "created_at": now,
            "updated_at": None,
            "likes_quantity": 0,
            "comments_quantity": 0,
        }
        try:
            result = await self.collection.insert_one(document)
        except WriteError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {exc.details.get('errInfo', exc)}",
            ) from exc

        document["_id"] = result.inserted_id
        return _serialize_post(document)

    async def get_by_id(self, post_id: str) -> dict[str, Any]:
        oid = self._parse_post_id(post_id)
        doc = await self.collection.find_one({"_id": oid})
        if not doc:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        return _serialize_post(doc)

    async def list_posts(
        self,
        *,
        author_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "desc",
        created_after=None, 
        created_before=None
    ) -> tuple[list[dict[str, Any]], int]:
        query: dict[str, Any] = {}
        if author_id is not None:
            query["author_id"] = str(author_id)
        if created_after:
            query["created_at"] = {"$gte": created_after}
        if created_before:
            query.setdefault("created_at", {})
            query["created_at"]["$lte"] = created_before
        
        total = await self.collection.count_documents(query)
        sort_direction = -1 if sort_order == "desc" else 1
        cursor = (
            self.collection.find(query)
            .sort(sort_by, sort_direction)
            .skip(skip)
            .limit(limit)
        )
        items = [_serialize_post(doc) async for doc in cursor]
        return items, total

    async def update(
        self, post_id: str, author_id: UUID, data: PostUpdate
    ) -> dict[str, Any]:
        oid = self._parse_post_id(post_id)
        existing = await self.collection.find_one({"_id": oid})
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if existing["author_id"] != str(author_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the author can update this post",
            )

        update_fields: dict[str, Any] = {"updated_at": datetime.now(timezone.utc)}
        if data.text is not None:
            update_fields["text"] = data.text
        if data.media is not None:
            update_fields["media"] = _media_to_bson(data.media)

        new_text = update_fields.get("text", existing.get("text"))
        new_media = update_fields.get("media", existing.get("media") or [])

        try:
            await self.collection.update_one({"_id": oid}, {"$set": update_fields})
        except (WriteError, DocumentTooLarge) as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {getattr(exc, 'details', exc)}",
            ) from exc

        updated = await self.collection.find_one({"_id": oid})
        return _serialize_post(updated)

    async def delete(self, post_id: str, author_id: UUID) -> None:
        oid = self._parse_post_id(post_id)
        existing = await self.collection.find_one({"_id": oid})
        if not existing:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
        if existing["author_id"] != str(author_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the author can delete this post",
            )
        await self.collection.delete_one({"_id": oid})

    async def like(self, post_id: str, user_id: str) -> dict[str, Any]:
        oid = self._parse_post_id(post_id)
        
        # Проверка, не лайкнул ли уже (потребуется отдельная коллекция likes)
        result = await self.collection.update_one(
            {"_id": oid},
            {"$inc": {"likes_quantity": 1}}
        )
        if result.matched_count == 0:
            raise HTTPException(404, "Post not found")
        
        return await self.get_by_id(post_id)

    async def unlike(self, post_id: str, user_id: str) -> dict[str, Any]:
        oid = self._parse_post_id(post_id)
        
        result = await self.collection.update_one(
            {"_id": oid},
            {"$inc": {"likes_quantity": -1}}
        )
        if result.matched_count == 0:
            raise HTTPException(404, "Post not found")
        
        return await self.get_by_id(post_id)

    async def increment_comments(self, post_id: str) -> dict[str, Any] | None:
        """Увеличить счётчик комментариев поста"""
        oid = self._parse_post_id(post_id)
        
        result = await self.collection.find_one_and_update(
            {"_id": oid},
            {"$inc": {"comments_quantity": 1}},
            return_document=True
        )
        
        if not result:
            return None
        
        return _serialize_post(result)


    async def decrement_comments(self, post_id: str) -> dict[str, Any] | None:
        """Уменьшить счётчик комментариев поста"""
        oid = self._parse_post_id(post_id)
        
        result = await self.collection.find_one_and_update(
            {"_id": oid, "comments_quantity": {"$gt": 0}},
            {"$inc": {"comments_quantity": -1}},
            return_document=True
        )
        
        if not result:
            return None
        
        return _serialize_post(result)
