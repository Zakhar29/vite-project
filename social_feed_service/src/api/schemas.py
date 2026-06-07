from datetime import datetime
from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


MediaType = Literal["image", "video", "audio"]

MEDIA_LIMITS: dict[MediaType, int] = {
    "image": 5,
    "video": 1,
    "audio": 5,
}


class MediaItem(BaseModel):
    type: MediaType
    url: str = Field(..., min_length=1)


def validate_media_limits(media: list[MediaItem]) -> list[MediaItem]:
    counts = {t: 0 for t in MEDIA_LIMITS}
    for item in media:
        counts[item.type] += 1

    for media_type, limit in MEDIA_LIMITS.items():
        if counts[media_type] > limit:
            raise ValueError(
                f"Не более {limit} файлов типа '{media_type}' "
                f"(получено {counts[media_type]})"
            )
    return media


class PostCreate(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "text": "Привет, лента!",
                    "media": [
                        {
                            "type": "image",
                            "url": "http://localhost:9000/media/posts/img1.jpg",
                        }
                    ],
                }
            ]
        }
    )

    text: Optional[str] = Field(None, max_length=5000)
    media: list[MediaItem] = Field(default_factory=list)

    @field_validator("media", mode="before")
    @classmethod
    def normalize_media(cls, media: object) -> object:
        if media is None:
            return []
        return media

    @field_validator("media")
    @classmethod
    def check_media(cls, media: list[MediaItem]) -> list[MediaItem]:
        return validate_media_limits(media)

    @model_validator(mode="after")
    def check_content(self) -> "PostCreate":
        text = (self.text or "").strip()
        if not text and not self.media:
            raise ValueError("Пост должен содержать текст или медиа")
        return self


class PostUpdate(BaseModel):
    text: Optional[str] = Field(None, max_length=5000)
    media: Optional[list[MediaItem]] = None

    @field_validator("media")
    @classmethod
    def check_media(cls, media: Optional[list[MediaItem]]) -> Optional[list[MediaItem]]:
        if media is None:
            return media
        return validate_media_limits(media)


class PostResponse(BaseModel):
    id: str
    author_id: UUID
    text: Optional[str] = None
    media: list[MediaItem] = Field(default_factory=list)
    created_at: datetime
    updated_at: Optional[datetime] = None
    likes_quantity: int = 0
    comments_quantity: int = 0


class PostListResponse(BaseModel):
    items: list[PostResponse]
    total: int
    skip: int
    limit: int
