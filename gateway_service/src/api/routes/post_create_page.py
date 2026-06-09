from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile, File, Form, status
from typing import List, Optional
from pydantic import BaseModel
import uuid

from src.api.dependencies import get_current_user, CurrentUser, get_social_client, get_media_client
from src.api.schemas import MediaItem
from src.clients.social_feed_service import SocialClient
from src.clients.media_service import MediaClient
from src.api.helpers.post_create_page import (
    extract_media_url,
    extract_full_key_from_url,
    extract_post_id_from_key
)
router = APIRouter(prefix="/post", tags=["Post Creation"])


@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_post(
        request: Request,
        text: str = Form(""),
        images: Optional[List[UploadFile]] = File(None, description="Изображения (до 5 шт)"),
        video: Optional[UploadFile] = File(None, description="Видео (1 шт)"),
        current_user: CurrentUser = Depends(get_current_user),
        social_client: SocialClient = Depends(get_social_client),
        media_client: MediaClient = Depends(get_media_client)
):
    """
    Создание поста с медиафайлами.

    Процесс:
    1. Создаём пост без медиа (только текст)
    2. Загружаем медиа в S3 с реальным post_id
    3. Обновляем пост, добавляя ссылки на медиа
    """

    # Получаем токен из заголовка
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    # ========== 1. ВАЛИДАЦИЯ КОЛИЧЕСТВА МЕДИА ==========

    image_count = len(images) if images else 0
    video_count = 1 if video else 0

    if image_count > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 images per post")
    if video_count > 1:
        raise HTTPException(status_code=400, detail="Maximum 1 video per post")

    total_media = image_count + video_count
    if total_media > 6:
        raise HTTPException(status_code=400, detail="Maximum 6 media items per post")

    # ========== 2. СОЗДАНИЕ ПОСТА БЕЗ МЕДИА ==========
    try:
        post_result = await social_client.create_post(
            text=text,
            token=token,
            media=None  # пока без медиа
        )
        post_id = post_result.get("id")
        if not post_id:
            raise ValueError("Post ID not returned from social service")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create post: {str(e)}"
        )
    media_list = []

    # Загрузка изображений
    if images:
        for image in images:
            try:
                result = await media_client.upload_post_image(
                    post_id=post_id,  # используем реальный ID поста
                    file=image
                )
                url = extract_media_url(result)
                if url:
                    media_list.append({"type": "image", "url": url})
            except Exception as e:
                # TODO: Удалить уже загруженные медиа из S3
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload image {image.filename}: {str(e)}"
                )

    # Загрузка видео
    if video:
        try:
            result = await media_client.upload_post_video(
                post_id=post_id,  # используем реальный ID поста
                file=video,
            )
            url = extract_media_url(result)
            if url:
                media_list.append({"type": "video", "url": url})
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload video: {str(e)}"
            )

    # ========== 4. ОБНОВЛЕНИЕ ПОСТА С МЕДИА ==========
    if media_list:
        try:
            post_result = await social_client.update_post(
                post_id=post_id,
                token=token,
                text=text,  # текст остаётся тот же
                media=media_list
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update post with media: {str(e)}"
            )

    return {
        "message": "Post created successfully",
        "post": post_result,
        "media": media_list
    }


@router.get("/{post_id}/edit")
async def get_post_for_edit(
        post_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        social_client: SocialClient = Depends(get_social_client)
):
    """
    Получение поста для редактирования.
    Возвращает текст и список медиа с полными ключами.
    """

    # Получаем пост
    post = await social_client.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Проверяем авторство
    if post.get("author_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="You are not the author of this post")

    # Извлекаем полные ключи из URL медиа
    media_with_keys = []
    for media in post.get("media", []):
        url = media.get("url")
        if url:
            full_key = extract_full_key_from_url(url)
            media_with_keys.append({
                "type": media.get("type"),
                "url": url,
                "key": full_key  # полный ключ с бакетом
            })

    return {
        "post_id": post_id,
        "text": post.get("text", ""),
        "media": media_with_keys
    }


# ========== ОБНОВЛЕНИЕ ПОСТА ==========

@router.put("/{post_id}/edit", status_code=status.HTTP_200_OK)
async def update_post(
        request: Request,
        post_id: str,
        text: str = Form(""),
        # Новые медиафайлы
        new_images: Optional[List[UploadFile]] = File(None, description="Новые изображения (до 5 шт)"),
        new_video: Optional[UploadFile] = File(None, description="Новое видео (1 шт)"),
        # Списки полных ключей медиа, которые нужно оставить
        keep_image_keys: Optional[List[str]] = Form(None,
                                                    description="Полные ключи изображений, которые нужно оставить"),
        keep_video_key: Optional[str] = Form(None, description="Полный ключ видео, которое нужно оставить"),
        current_user: CurrentUser = Depends(get_current_user),
        social_client: SocialClient = Depends(get_social_client),
        media_client: MediaClient = Depends(get_media_client)
):
    """
    Редактирование поста.

    Процесс:
    1. Получаем текущий пост
    2. Сравниваем существующие медиа с keep списками
    3. Удаляем из S3 те медиа, которых нет в keep списках
    4. Загружаем новые медиа
    5. Обновляем пост с новым текстом и медиа
    """

    # Получаем токен из заголовка
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    # ========== 1. ПОЛУЧАЕМ ТЕКУЩИЙ ПОСТ ==========
    current_post = await social_client.get_post(post_id)

    if not current_post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Проверяем авторство
    if current_post.get("author_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="You are not the author of this post")

    # ========== 2. АНАЛИЗ ТЕКУЩИХ МЕДИА ==========
    current_media = current_post.get("media", [])

    # Извлекаем полные ключи текущих медиа
    current_image_keys = set()
    current_video_key = None

    for media in current_media:
        url = media.get("url")
        if url:
            full_key = extract_full_key_from_url(url)
            if full_key:
                if media.get("type") == "image":
                    current_image_keys.add(full_key)
                elif media.get("type") == "video":
                    current_video_key = full_key

    # Преобразуем keep списки в множества
    keep_images = set(keep_image_keys) if keep_image_keys else set()
    keep_video = keep_video_key if keep_video_key else None

    # ========== 3. УДАЛЕНИЕ МЕДИА, КОТОРЫХ НЕТ В KEEP СПИСКАХ ==========
    keys_to_delete = []

    # Удаляем изображения, которых нет в keep_images
    for key in current_image_keys:
        if key not in keep_images:
            keys_to_delete.append(key)

    # Удаляем видео, если оно изменилось
    if current_video_key and current_video_key != keep_video:
        keys_to_delete.append(current_video_key)

    # Выполняем удаление из S3
    if keys_to_delete:
        try:
            await media_client.delete_post_media(
                post_id=post_id,
                media_keys=keys_to_delete
            )
        except Exception as e:
            print(f"Warning: Failed to delete media from S3: {e}")

    # ========== 4. ЗАГРУЗКА НОВЫХ МЕДИА ==========
    new_media_list = []

    # Загружаем новые изображения
    if new_images:
        for image in new_images:
            try:
                result = await media_client.upload_post_image(
                    post_id=post_id,
                    file=image
                )
                url = extract_media_url(result)
                if url:
                    new_media_list.append({"type": "image", "url": url})
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to upload image {image.filename}: {str(e)}"
                )

    # Загружаем новое видео
    if new_video:
        try:
            result = await media_client.upload_post_video(
                post_id=post_id,
                file=new_video,
                quality="1080p"
            )
            url = extract_media_url(result)
            if url:
                new_media_list.append({"type": "video", "url": url})
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to upload video: {str(e)}"
            )

    # ========== 5. ФОРМИРОВАНИЕ ИТОГОВОГО СПИСКА МЕДИА ==========
    final_media = []

    # Добавляем оставшиеся старые медиа (те, что в keep списках)
    for media in current_media:
        url = media.get("url")
        if url:
            full_key = extract_full_key_from_url(url)
            if full_key:
                if media.get("type") == "image" and full_key in keep_images:
                    final_media.append({"type": "image", "url": url})
                elif media.get("type") == "video" and full_key == keep_video:
                    final_media.append({"type": "video", "url": url})

    # Добавляем новые медиа
    final_media.extend(new_media_list)

    # ========== 6. ОБНОВЛЕНИЕ ПОСТА ==========
    try:
        updated_post = await social_client.update_post(
            post_id=post_id,
            token=token,
            text=text,
            media=final_media if final_media else None
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update post: {str(e)}"
        )

    return {
        "message": "Post updated successfully",
        "post": updated_post
    }


# ========== УДАЛЕНИЕ ПОСТА ==========

@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
async def delete_post(
        request: Request,
        post_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        social_client: SocialClient = Depends(get_social_client),
        media_client: MediaClient = Depends(get_media_client)
):
    """
    Удаление поста.
    Сначала удаляет все медиа из S3, затем удаляет пост из БД.
    """

    # Получаем токен из заголовка
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    # ========== 1. ПОЛУЧАЕМ ПОСТ ==========
    post = await social_client.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # Проверяем авторство
    if post.get("author_id") != str(current_user.id):
        raise HTTPException(status_code=403, detail="You are not the author of this post")

    # ========== 2. УДАЛЕНИЕ МЕДИА ИЗ S3 ==========
    media_list = post.get("media", [])
    keys_to_delete = []

    for media in media_list:
        url = media.get("url")
        if url:
            full_key = extract_full_key_from_url(url)
            if full_key:
                keys_to_delete.append(full_key)

    if keys_to_delete:
        try:
            await media_client.delete_post_media(
                post_id=post_id,
                media_keys=keys_to_delete
            )
        except Exception as e:
            print(f"Warning: Failed to delete media from S3: {e}")
            # Не прерываем удаление поста, даже если S3 удаление не удалось

    # ========== 3. УДАЛЕНИЕ ПОСТА ИЗ БД ==========
    await social_client.delete_post(post_id=post_id, token=token)

    return {
        "message": "Post deleted successfully",
        "post_id": post_id,
        "deleted_media_count": len(keys_to_delete)
    }