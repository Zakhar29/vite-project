from fastapi import HTTPException, UploadFile
from src.services.media import MediaPath

MAX_FILE_SIZE = {
    "avatar": 10 * 1024 * 1024,
    "track": 50 * 1024 * 1024,
    "album_cover": 10 * 1024 * 1024,
    "chat_image": 100 * 1024 * 1024,
    "chat_video": 300 * 1024 * 1024,
    "chat_audio": 25 * 1024 * 1024,
    "post_image": 10 * 1024 * 1024,
    "post_video": 500 * 1024 * 1024,
}

ALLOWED_CONTENT_TYPES = {
    "avatar": ["image/jpeg", "image/png", "image/webp"],
    "track": ["audio/mpeg", "audio/wav", "audio/flac", "audio/aac"],
    "album_cover": ["image/jpeg", "image/png", "image/webp"],
    "chat_image": ["image/jpeg", "image/png", "image/webp", "image/gif"],
    "chat_video": ["video/mp4", "video/quicktime", "video/x-msvideo"],
    "chat_audio": ["audio/ogg"],
    "post_image": ["image/jpeg", "image/png", "image/webp", "image/gif"],
    "post_video": ["video/mp4", "video/quicktime"],
}


def validate_file(file: UploadFile, media_type: str) -> None:
    """Валидация файла: размер и content-type"""
    if file.size and file.size > MAX_FILE_SIZE[media_type]:
        max_mb = MAX_FILE_SIZE[media_type] // (1024 * 1024)
        raise HTTPException(400, f"Файл слишком большой. Максимум {max_mb}MB")

    if file.content_type and file.content_type not in ALLOWED_CONTENT_TYPES[media_type]:
        raise HTTPException(400, f"Неподдерживаемый формат файла: {file.content_type}")


def prepare_upload_response(paths: list[MediaPath], uploaded_keys: list[str]) -> list[dict]:
    """Формирование ответа после успешной загрузки"""
    return [
        {"url": path.url, "key": key, "bucket": path.bucket}
        for path, key in zip(paths, uploaded_keys)
    ]
