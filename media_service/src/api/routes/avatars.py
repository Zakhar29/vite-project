from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Query
from src.api.dependencies import CurrentUser, get_current_user, get_media_service, get_s3_client
from src.utils.helpers import convert_image_to_avif_sizes
from src.S3client.minio_client import S3Client
from src.services.media import MediaService
from src.utils.media_validate import prepare_upload_response, validate_file
from pathlib import Path  

router = APIRouter(prefix="/avatar", tags=["Avatar"])


@router.post("")
async def upload_avatar(
        user: CurrentUser = Depends(get_current_user),
        file: UploadFile = File(...),
        replace: bool = Form(True),
        media_service: MediaService = Depends(get_media_service),
        s3_client: S3Client = Depends(get_s3_client),
):
    """Загрузка аватарки пользователя с конвертацией в AVIF (3 размера)"""

    validate_file(file, "avatar")

    result, error = await convert_image_to_avif_sizes(file)
    if error or result is None:
        raise HTTPException(400, f"Ошибка конвертации изображения: {error}")

    uploaded_keys = []
    media_paths = []

    for file_bytes, ext, size_name in result:
        path = media_service.get_avatar_path(user_id=user.id, size=size_name)

        if not replace:
            try:
                await s3_client.client.head_object(Bucket=path.bucket, Key=path.key)
                continue
            except s3_client.client.exceptions.ClientError:
                pass

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


@router.delete("")
async def delete_avatar(
        user: CurrentUser = Depends(get_current_user),
        sizes: list[str] = Query(["small", "medium", "large"]),
        media_service: MediaService = Depends(get_media_service),
        s3_client: S3Client = Depends(get_s3_client),
):
    """Удаление аватарки пользователя"""

    deleted = []
    for size in sizes:
        path = media_service.get_avatar_path(user_id=user.id, size=size)
        try:
            await s3_client.client.delete_object(Bucket=path.bucket, Key=path.key)
            deleted.append({"size": size, "key": path.key, "success": True})
        except Exception as e:
            deleted.append({"size": size, "key": path.key, "success": False, "error": str(e)})

    return {"deleted": deleted}
