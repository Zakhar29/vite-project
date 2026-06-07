from enum import Enum
from dataclasses import dataclass
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"

    USERS_SERVICE_URL: str = "http://localhost:8000"

    class Config:
        env_file = ".env"


settings = Settings()


class MediaType(Enum):
    TRACK = "media-music"
    IMAGE = "media-images"
    VIDEO = "media-videos"
    AVATAR = "avatars"
    COVER = "covers"
    CHAT_AUDIO = "chat-audio"
    CHAT_IMAGE = "chat-images"
    CHAT_VIDEO = "chat-videos"


class MediaCategory(Enum):
    AVATAR = "avatars"
    COVER = "covers"
    IMAGE = "images"
    AUDIO = "audio"
    VIDEO = "videos"


@dataclass
class MediaPath:
    bucket: str
    key: str
    url: str


LIFECYCLE_POLICIES = {
    "media-chat": {
        "expiration_days": 30,  # Автоудаление медиа чатов
        "transition_days": 7,     # Перемещение в glacier после 7 дней
        "noncurrent_version_expiration": 7
    },
    "media-images": {
        "transition_to_ia_days": 90,  # Редко запрашиваемые обложки
        "noncurrent_version_expiration": 30
    },
    "media-videos": {
        "transition_to_ia_days": 180,
        "abort_incomplete_multipart_upload_days": 7
    }
}

