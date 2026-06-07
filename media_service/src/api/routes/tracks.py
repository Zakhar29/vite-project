from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from src.api.dependencies import get_media_service, get_s3_client
from src.utils.helpers import (
    convert_image_to_avif_sizes,
    convert_audio_to_aac256,
    convert_video_to_mp4_h264,
    convert_video_multiple_versions,
)
from src.S3client.minio_client import S3Client
from src.services.media import MediaService
from src.utils.media_validate import prepare_upload_response, validate_file
from pathlib import Path  

router = APIRouter(prefix="/track", tags=["Track"])


@router.post("/{album_id}/{track_number}")
async def upload_track(
        album_id: str,
        track_number: int,
        file: UploadFile = File(...),
        media_service: MediaService = Depends(get_media_service),
        s3_client: S3Client = Depends(get_s3_client),
):
    """Загрузка аудио-трека с конвертацией в AAC 256kbps"""

    validate_file(file, "track")

    # Конвертация аудио
    file_bytes, ext_or_error = await convert_audio_to_aac256(file)
    if file_bytes is None:
        raise HTTPException(400, f"Ошибка конвертации аудио: {ext_or_error}")

    # Получение пути и загрузка
    path = media_service.get_track_path(album_id=album_id, track_number=track_number, format=ext_or_error)

    await s3_client.client.put_object(
        Bucket=path.bucket,
        Key=path.key,
        Body=file_bytes,
        ContentType=f"audio/{ext_or_error}",
        CacheControl="public, max-age=31536000"
    )

    return prepare_upload_response([path], [path.key])[0]


@router.delete("/{album_id}/{track_number}")
async def delete_track(
        album_id: str,
        track_number: int,
        media_service: MediaService = Depends(get_media_service),
        s3_client: S3Client = Depends(get_s3_client),
):
    """Удаление трека"""

    path = media_service.get_track_path(album_id=album_id, track_number=track_number)

    try:
        await s3_client.client.delete_object(Bucket=path.bucket, Key=path.key)
        return {"success": True, "key": path.key}
    except Exception as e:
        raise HTTPException(500, f"Ошибка удаления: {str(e)}")
