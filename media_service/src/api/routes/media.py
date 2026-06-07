from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from src.api.dependencies import get_media_service, get_s3_client
from src.utils.helpers import (
    convert_image_to_avif,
    convert_video_to_mp4_h264,
    convert_video_multiple_versions,
)
from src.S3client.minio_client import S3Client
from src.services.media import MediaService
from src.utils.media_validate import prepare_upload_response, validate_file
from pathlib import Path  

router = APIRouter(prefix="/media", tags=["Media"])


@router.post("/{post_id}/image")
async def upload_post_image(
        post_id: str,
        file: UploadFile = File(...),
        media_service: MediaService = Depends(get_media_service),
        s3_client: S3Client = Depends(get_s3_client),
):
    """Загрузка изображения в пост"""

    validate_file(file, "post_image")

    image_name = Path(file.filename).stem
    result, error = await convert_image_to_avif(file)
    if error or result is None:
        raise HTTPException(400, f"Ошибка конвертации: {error}")

    uploaded_keys = []
    media_paths = []
    
    for file_bytes, ext in result:
        path = media_service.get_post_image_path(
            post_id=post_id, image_name=f"{image_name}", format=ext
        )

        await s3_client.client.put_object(
            Bucket=path.bucket,
            Key=path.key,
            Body=file_bytes,
            ContentType=f"image/{ext}",
            CacheControl="public, max-age=31536000, immutable"
        )
        uploaded_keys.append(path.key)
        media_paths.append(path)

    return prepare_upload_response(media_paths, uploaded_keys)


@router.post("/{post_id}/video")
async def upload_post_video(
        post_id: str,
        file: UploadFile = File(...),
        quality: str = Form("1080p"),
        media_service: MediaService = Depends(get_media_service),
        s3_client: S3Client = Depends(get_s3_client),
):
    """Загрузка видео в пост"""

    validate_file(file, "post_video")

    video_name = Path(file.filename).stem

    max_height = 1080 if quality == "1080p" else 720

    # === Обработка конвертации ===
    if quality == "all":
        # Для "all" функция возвращает (list, error)
        result, error = await convert_video_multiple_versions(file, max_height=1080)
    else:
        # Для одного качества функция возвращает (bytes, ext_or_error)
        file_bytes, ext_or_error = await convert_video_to_mp4_h264(file, max_height=max_height)
        if file_bytes is None:
            raise HTTPException(400, f"Ошибка конвертации видео: {ext_or_error}")

        # ✅ FIX: создаём список кортежей, а не кортеж со списком!
        result = [(file_bytes, ext_or_error, quality)]  # ← без запятой и "" в конце
        error = ""

    # === Проверка ошибок ===
    if error or result is None:
        raise HTTPException(400, f"Ошибка конвертации видео: {error}")

    # === Загрузка в S3 ===
    uploaded_keys = []
    media_paths = []

    # Теперь распаковка работает корректно
    for file_bytes, ext, version in result:
        path = media_service.get_post_video_path(
            post_id=post_id, video_name=f"{video_name}_{version}", format=ext
        )

        await s3_client.client.put_object(
            Bucket=path.bucket,
            Key=path.key,
            Body=file_bytes,
            ContentType=f"video/{ext}",
            CacheControl="public, max-age=31536000"
        )
        uploaded_keys.append(path.key)
        media_paths.append(path)

    return prepare_upload_response(media_paths, uploaded_keys)


@router.delete("/{post_id}")
async def delete_post_media(
        post_id: str,
        media_keys: list[str] = Query(...),
        s3_client: S3Client = Depends(get_s3_client),
):
    """Удаление медиа из поста по ключам"""
    # Жестко определяем bucket для постов
    bucket = "posts"  # или media_service.get_bucket_by_type("post")
    
    deleted = []
    for key in media_keys:
        # Проверка, что ключ относится к этому post_id
        if not key.startswith(f"posts/{post_id}/"):
            deleted.append({"key": key, "success": False, "error": "Key does not belong to this post"})
            continue
            
        try:
            await s3_client.client.delete_object(Bucket=bucket, Key=key)
            deleted.append({"key": key, "success": True})
        except Exception as e:
            deleted.append({"key": key, "success": False, "error": str(e)})
    
    return {"deleted": deleted}
