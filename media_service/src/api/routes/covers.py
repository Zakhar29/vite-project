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

router = APIRouter(prefix="/cover", tags=["Cover"])


@router.post("/{album_id}/upload")
async def upload_album_cover(
        album_id: str,
        file: UploadFile = File(...),
        media_service: MediaService = Depends(get_media_service),
        s3_client: S3Client = Depends(get_s3_client),
):
    """Загрузка обложки альбома с конвертацией в AVIF (3 размера)"""

    validate_file(file, "album_cover")

    result, error = await convert_image_to_avif_sizes(file)
    if error or result is None:
        raise HTTPException(400, f"Ошибка конвертации изображения: {error}")

    uploaded_keys = []
    media_paths = []

    for file_bytes, ext, size_name in result:
        path = media_service.get_album_cover_path(album_id=album_id, size=size_name)

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


@router.delete("/{album_id}/cover")
async def delete_album_cover(
        album_id: str,
        sizes: list[str] = Query(["small", "medium", "large"]),
        media_service: MediaService = Depends(get_media_service),
        s3_client: S3Client = Depends(get_s3_client),
):
    """Удаление обложки альбома"""

    deleted = []
    for size in sizes:
        path = media_service.get_album_cover_path(album_id=album_id, size=size)
        try:
            await s3_client._client.delete_object(Bucket=path.bucket, Key=path.key)
            deleted.append({"size": size, "key": path.key, "success": True})
        except Exception as e:
            deleted.append({"size": size, "key": path.key, "success": False, "error": str(e)})

    return {"deleted": deleted}
