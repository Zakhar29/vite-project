from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status
from fastapi import Request
from typing import List, Optional
from pydantic import BaseModel
import json

from src.api.dependencies import (
    get_current_user,
    CurrentUser,
    get_users_client,
    get_music_client,
    get_comment_client,
    get_social_client
)
from src.api.schemas import TrackCommentCreate, TrackCommentUpdate, CommentReplyCreate
from src.clients.music_service import MusicClient
from src.clients.comments_service import CommentClient
from src.clients.social_feed_service import SocialClient


router = APIRouter(prefix="/social", tags=["Music Social"])


@router.post("/track/{track_id}/comment", status_code=201)
async def create_track_comment(
        request: Request,
        track_id: str,
        data: TrackCommentCreate,
        current_user: CurrentUser = Depends(get_current_user),
        music_client: MusicClient = Depends(get_music_client),
        comment_client: CommentClient = Depends(get_comment_client)
):
    """
    Создание комментария к треку.
    Увеличивает счётчик комментариев в music_catalog_service.
    """

    # Получаем токен из заголовка
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    # 1. Проверяем, существует ли трек
    track = await music_client.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # 2. Создаём комментарий в comment_service
    try:
        comment_result = await comment_client.create_track_comment(
            track_id=track_id,
            comment=data.comment,
            token=token,
            track_timecode=data.track_timecode
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")

    # 3. Увеличиваем счётчик комментариев в music_catalog_service
    try:
        await music_client.inc_track_comments(
            track_id=track_id,
            token=token
        )
    except Exception as e:
        # Логируем ошибку, но не откатываем комментарий (или можно откатить?)
        print(f"Warning: Failed to increment track comments counter: {e}")

    return {
        "message": "Comment created successfully",
        "comment": comment_result
    }


@router.put("/track/{track_id}/comment/{comment_id}", status_code=200)
async def update_track_comment(
        request: Request,
        track_id: str,
        comment_id: str,
        data: TrackCommentUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        music_client: MusicClient = Depends(get_music_client),
        comment_client: CommentClient = Depends(get_comment_client)
):
    """
    Обновление комментария к треку.
    """

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    # 1. Проверяем, существует ли трек
    track = await music_client.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # 2. Обновляем комментарий в comment_service
    try:
        comment_result = await comment_client.update_track_comment(
            track_id=track_id,
            comment_id=comment_id,
            comment=data.comment,
            token=token,
            track_timecode=data.track_timecode
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")

    return {
        "message": "Comment updated successfully",
        "comment": comment_result
    }


@router.delete("/track/{track_id}/comment/{comment_id}", status_code=200)
async def delete_track_comment(
        request: Request,
        track_id: str,
        comment_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        music_client: MusicClient = Depends(get_music_client),
        comment_client: CommentClient = Depends(get_comment_client)
):
    """
    Удаление комментария к треку.
    Уменьшает счётчик комментариев в music_catalog_service.
    """

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    # 1. Проверяем, существует ли трек
    track = await music_client.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    # 2. Удаляем комментарий из comment_service
    try:
        await comment_client.delete_track_comment(
            track_id=track_id,
            comment_id=comment_id,
            token=token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")

    # 3. Уменьшаем счётчик комментариев в music_catalog_service
    try:
        await music_client.dec_track_comments(
            track_id=track_id,
            token=token
        )
    except Exception as e:
        print(f"Warning: Failed to decrement track comments counter: {e}")

    return {
        "message": "Comment deleted successfully"
    }


@router.post("/track/{track_id}/comment/{comment_id}/reply", status_code=201)
async def reply_to_track_comment(
        request: Request,
        track_id: str,
        comment_id: str,
        data: CommentReplyCreate,
        current_user: CurrentUser = Depends(get_current_user),
        music_client: MusicClient = Depends(get_music_client),
        comment_client: CommentClient = Depends(get_comment_client)
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    track = await music_client.get_track(track_id)
    if not track:
        raise HTTPException(status_code=404, detail="Track not found")

    try:
        comment_result = await comment_client.reply_to_track_comment(
            track_id=track_id,
            comment_id=comment_id,
            comment=data.comment,
            token=token,
            track_timecode=data.track_timecode,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create reply: {str(e)}")

    return {
        "message": "Reply created successfully",
        "comment": comment_result
    }


@router.post("/track/{track_id}/like")
async def track_like(
        request: Request,
        track_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        music_client: MusicClient = Depends(get_music_client),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(401, "Missing authorization token")
    track = await music_client.get_track(track_id)
    if not track:
        raise HTTPException(401, "Track not found")

    await music_client.inc_track_likes(track_id=track_id, token=token)


@router.post("/track/{track_id}/unlike")
async def track_unlike(
        request: Request,
        track_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        music_client: MusicClient = Depends(get_music_client),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(401, "Missing authorization token")
    track = await music_client.get_track(track_id)
    if not track:
        raise HTTPException(401, "Track not found")

    await music_client.dec_track_likes(track_id=track_id, token=token)

@router.post("/album/{album_id}/like")
async def album_like(
        request: Request,
        album_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        music_client: MusicClient = Depends(get_music_client),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(401, "Missing authorization token")
    album = await music_client.get_album(album_id)
    if not album:
        raise HTTPException(401, "Track not found")

    await music_client.inc_album_likes(album_id=album_id, token=token)


@router.post("/album/{album_id}/unlike")
async def album_unlike(
        request: Request,
        album_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        music_client: MusicClient = Depends(get_music_client),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(401, "Missing authorization token")
    album = await music_client.get_album(album_id)
    if not album:
        raise HTTPException(401, "Track not found")

    await music_client.dec_album_likes(album_id=album_id, token=token)


@router.post("/track/{track_id}/listening")
async def track_listening(
        track_id: str,
        music_client: MusicClient = Depends(get_music_client),
):
    track = await music_client.get_track(track_id)
    if not track:
        raise HTTPException(401, "Track not found")

    await music_client.inc_track_listening(track_id=track_id)
    await music_client.inc_album_listening(album_id=track["album_id"])


@router.post("/album/{album_id}/follow")
async def album_follow(
        request: Request,
        album_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        music_client: MusicClient = Depends(get_music_client),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(401, "Missing authorization token")
    album = await music_client.get_album(album_id)
    if not album:
        raise HTTPException(401, "Track not found")

    await music_client.album_follow(album_id=album_id, token=token)


@router.post("/album/{album_id}/unfollow")
async def album_unfollow(
        request: Request,
        album_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        music_client: MusicClient = Depends(get_music_client),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(401, "Missing authorization token")
    album = await music_client.get_album(album_id)
    if not album:
        raise HTTPException(401, "Track not found")

    await music_client.album_unfollow(album_id=album_id, token=token)


