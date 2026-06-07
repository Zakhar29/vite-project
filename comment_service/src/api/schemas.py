from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator

EntityType = Literal["post", "track", "album", "playlist"]


def _strip_comment(value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError("Текст комментария не может быть пустым")
    return stripped


# --- Посты ---


class PostCommentCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"comment": "Отличный пост!"}]
        }
    )

    comment: str = Field(..., min_length=1, max_length=2000)

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        return _strip_comment(value)


class PostCommentUpdate(BaseModel):
    comment: str = Field(..., min_length=1, max_length=2000)

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        return _strip_comment(value)


class PostCommentResponse(BaseModel):
    id: str
    author_id: UUID
    post_id: str
    answer_id: Optional[str] = None
    comment: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    likes_quantity: int = 0
    dislikes_quantity: int = 0
    rating_quantity: int = 0
    answer_quantity: int = 0


# --- Треки ---


class TrackCommentCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [{"comment": "Крутой дроп!", "track_timecode": 125}]
        }
    )

    comment: str = Field(..., min_length=1, max_length=2000)
    track_timecode: Optional[int] = Field(None, ge=0)

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        return _strip_comment(value)


class TrackCommentUpdate(BaseModel):
    comment: str = Field(..., min_length=1, max_length=2000)
    track_timecode: Optional[int] = Field(None, ge=0)

    @field_validator("comment")
    @classmethod
    def validate_comment(cls, value: str) -> str:
        return _strip_comment(value)


class TrackCommentResponse(BaseModel):
    id: str
    author_id: UUID
    track_id: str
    answer_id: Optional[str] = None
    comment: str
    track_timecode: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    likes_quantity: int = 0
    dislikes_quantity: int = 0
    rating_quantity: int = 0
    answer_quantity: int = 0


class PostCommentListResponse(BaseModel):
    items: list[PostCommentResponse]
    total: int
    skip: int
    limit: int


class TrackCommentListResponse(BaseModel):
    items: list[TrackCommentResponse]
    total: int
    skip: int
    limit: int
