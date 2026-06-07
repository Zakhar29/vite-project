from datetime import datetime, timezone
from typing import Any, Literal, Optional
from uuid import UUID

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException, status
from pymongo.errors import WriteError

from config import settings
from src.db.mongo_client import mongodb_client

EntityType = Literal["post", "track"]


def _serialize_post(doc: dict[str, Any]) -> dict[str, Any]:
    answer_id = doc.get("answer_id")
    return {
        "id": str(doc["_id"]),
        "author_id": doc["author_id"],
        "post_id": doc["entity_id"],
        "answer_id": str(answer_id) if answer_id else None,
        "comment": doc["comment"],
        "created_at": doc["created_at"],
        "updated_at": doc.get("updated_at"),
        "likes_quantity": doc.get("likes_quantity", 0),
        "dislikes_quantity": doc.get("dislikes_quantity", 0),
        "rating_quantity": doc.get("rating_quantity", 0),
        "answer_quantity": doc.get("answer_quantity", 0),
    }


def _serialize_track(doc: dict[str, Any]) -> dict[str, Any]:
    answer_id = doc.get("answer_id")
    return {
        "id": str(doc["_id"]),
        "author_id": doc["author_id"],
        "track_id": doc["entity_id"],
        "answer_id": str(answer_id) if answer_id else None,
        "comment": doc["comment"],
        "track_timecode": doc.get("track_timecode"),
        "created_at": doc["created_at"],
        "updated_at": doc.get("updated_at"),
        "likes_quantity": doc.get("likes_quantity", 0),
        "dislikes_quantity": doc.get("dislikes_quantity", 0),
        "rating_quantity": doc.get("rating_quantity", 0),
        "answer_quantity": doc.get("answer_quantity", 0),
    }


class CommentService:
    def __init__(self):
        self.collection = mongodb_client.get_collection(settings.COMMENTS_COLLECTION)

    @staticmethod
    def _parse_object_id(value: str, field_name: str = "id") -> ObjectId:
        try:
            return ObjectId(value)
        except InvalidId as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {field_name}",
            ) from exc

    def _ensure_entity(
        self, doc: dict[str, Any], entity_type: EntityType, entity_id: str
    ) -> None:
        if doc["entity_type"] != entity_type or doc["entity_id"] != entity_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found for this resource",
            )

    async def _get_parent(
        self, answer_id: str, entity_type: EntityType, entity_id: str
    ) -> dict[str, Any]:
        parent = await self.collection.find_one(
            {"_id": self._parse_object_id(answer_id, "answer_id")}
        )
        if not parent:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parent comment not found",
            )
        self._ensure_entity(parent, entity_type, entity_id)
        return parent


    async def create(
        self,
        author_id: UUID,
        *,
        entity_type: EntityType,
        entity_id: str,
        comment: str,
        answer_id: Optional[str] = None,
        track_timecode: Optional[int] = None,
    ) -> dict[str, Any]:
        answer_oid: ObjectId | None = None
        if answer_id:
            parent_oid = self._parse_comment_id(answer_id)
            await self.collection.update_one(
                {"_id": parent_oid},
                {"$inc": {"answer_quantity": 1}}
            )

        now = datetime.now(timezone.utc)
        document: dict[str, Any] = {
            "author_id": str(author_id),
            "entity_type": entity_type,
            "entity_id": entity_id,
            "answer_id": answer_oid,
            "comment": comment,
            "track_timecode": track_timecode if entity_type == "track" else None,
            "created_at": now,
            "updated_at": None,
            "likes_quantity": 0,
            "dislikes_quantity": 0,
            "rating_quantity": 0,
            "answer_quantity": 0,
        }

        try:
            result = await self.collection.insert_one(document)
        except WriteError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {exc.details.get('errInfo', exc)}",
            ) from exc

        if answer_oid is not None:
            await self.collection.update_one(
                {"_id": answer_oid},
                {"$inc": {"answer_quantity": 1}},
            )

        document["_id"] = result.inserted_id
        serializer = _serialize_track if entity_type == "track" else _serialize_post
        return serializer(document)

    async def get_for_entity(
        self, comment_id: str, entity_type: EntityType, entity_id: str
    ) -> dict[str, Any]:
        doc = await self.collection.find_one(
            {"_id": self._parse_object_id(comment_id)}
        )
        if not doc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        self._ensure_entity(doc, entity_type, entity_id)
        serializer = _serialize_track if entity_type == "track" else _serialize_post
        return serializer(doc)

    async def list_for_entity(
            self,
            entity_type: str,
            entity_id: str,
            root_only: bool = True,
            answer_id: Optional[str] = None,
            skip: int = 0,
            limit: int = 20,
            sort_by: str = "created_at",
            sort_order: str = "asc",
            extra_filters: Optional[dict] = None
    ) -> tuple[list[dict[str, Any]], int]:
        """Список комментариев для сущности с сортировкой"""

        query: dict[str, Any] = {
            "entity_type": entity_type,
            "entity_id": entity_id,
        }

        if answer_id:
            query["answer_id"] = ObjectId(answer_id)
        elif root_only:
            query["answer_id"] = None

        if extra_filters:
            query.update(extra_filters)

        total = await self.collection.count_documents(query)

        sort_direction = -1 if sort_order == "desc" else 1

        cursor = (
            self.collection.find(query)
            .sort(sort_by, sort_direction)
            .skip(skip)
            .limit(limit)
        )

        # Выбираем правильную функцию сериализации в зависимости от типа сущности
        if entity_type == "track":
            items = [_serialize_track(doc) async for doc in cursor]
        else:  # post, album, playlist
            items = [_serialize_post(doc) async for doc in cursor]

        return items, total

    async def update(
        self,
        comment_id: str,
        author_id: UUID,
        entity_type: EntityType,
        entity_id: str,
        *,
        comment: str,
        track_timecode: Optional[int] = None,
    ) -> dict[str, Any]:
        oid = self._parse_object_id(comment_id)
        existing = await self.collection.find_one({"_id": oid})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        self._ensure_entity(existing, entity_type, entity_id)
        if existing["author_id"] != str(author_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the author can update this comment",
            )

        update_fields: dict[str, Any] = {
            "comment": comment,
            "updated_at": datetime.now(timezone.utc),
        }
        if track_timecode is not None:
            if entity_type != "track":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="track_timecode допустим только для комментариев к треку",
                )
            update_fields["track_timecode"] = track_timecode

        try:
            await self.collection.update_one({"_id": oid}, {"$set": update_fields})
        except WriteError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Validation failed: {exc.details.get('errInfo', exc)}",
            ) from exc

        updated = await self.collection.find_one({"_id": oid})
        serializer = _serialize_track if entity_type == "track" else _serialize_post
        return serializer(updated)

    async def delete(
        self,
        comment_id: str,
        author_id: UUID,
        entity_type: EntityType,
        entity_id: str,
    ) -> None:
        oid = self._parse_object_id(comment_id)
        existing = await self.collection.find_one({"_id": oid})
        if not existing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Comment not found",
            )
        self._ensure_entity(existing, entity_type, entity_id)
        if existing["author_id"] != str(author_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the author can delete this comment",
            )
        if existing.get("answer_quantity", 0) > 0:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Нельзя удалить комментарий с ответами",
            )

        await self.collection.delete_one({"_id": oid})

        parent_id = existing.get("answer_id")
        if parent_id is not None:
            await self.collection.update_one(
                {"_id": parent_id},
                {"$inc": {"answer_quantity": -1}},
            )

    async def like(self, comment_id: str, user_id: str) -> dict:
        oid = self._parse_comment_id(comment_id)
        
        result = await self.collection.update_one(
            {"_id": oid},
            {"$inc": {"likes_quantity": 1, "rating_quantity": 1}}
        )
        if result.matched_count == 0:
            raise HTTPException(404, "Comment not found")
        
        return await self.get_by_id(comment_id)

    async def dislike(self, comment_id: str, user_id: str) -> dict:
        oid = self._parse_comment_id(comment_id)
        
        result = await self.collection.update_one(
            {"_id": oid},
            {"$inc": {"dislikes_quantity": 1, "rating_quantity": -1}}
        )
        if result.matched_count == 0:
            raise HTTPException(404, "Comment not found")
        
        return await self.get_by_id(comment_id)

    async def remove_like(self, comment_id: str, user_id: str) -> dict:
        oid = self._parse_comment_id(comment_id)
        
        result = await self.collection.update_one(
            {"_id": oid},
            {"$inc": {"likes_quantity": -1, "rating_quantity": -1}}
        )
        if result.matched_count == 0:
            raise HTTPException(404, "Comment not found")
        
        return await self.get_by_id(comment_id)

    async def remove_dislike(self, comment_id: str, user_id: str) -> dict:
        oid = self._parse_comment_id(comment_id)
        
        result = await self.collection.update_one(
            {"_id": oid},
            {"$inc": {"dislikes_quantity": -1, "rating_quantity": 1}}
        )
        if result.matched_count == 0:
            raise HTTPException(404, "Comment not found")
        
        return await self.get_by_id(comment_id)