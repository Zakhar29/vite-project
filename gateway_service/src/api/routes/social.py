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
from src.api.schemas import PostCommentCreate, PostCommentUpdate, CommentReplyCreate
from src.clients.music_service import MusicClient
from src.clients.comments_service import CommentClient
from src.clients.social_feed_service import SocialClient


router = APIRouter(prefix="/social", tags=["Post Social"])

@router.post("/posts/{post_id}/comment", status_code=201)
async def create_post_comment(
        request: Request,
        post_id: str,
        data: PostCommentCreate,
        current_user: CurrentUser = Depends(get_current_user),
        social_client: SocialClient = Depends(get_social_client),
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
    post = await social_client.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 2. Создаём комментарий в comment_service
    try:
        comment_result = await comment_client.create_post_comment(
            post_id=post_id,
            comment=data.comment,
            token=token,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create comment: {str(e)}")

    # 3. Увеличиваем счётчик комментариев в music_catalog_service
    try:
        await social_client.inc_post_comments(
            post_id=post_id,
            token=token
        )
    except Exception as e:
        # Логируем ошибку, но не откатываем комментарий (или можно откатить?)
        print(f"Warning: Failed to increment post comments counter: {e}")

    return {
        "message": "Comment created successfully",
        "comment": comment_result
    }


@router.put("/posts/{post_id}/comment/{comment_id}", status_code=200)
async def update_post_comment(
        request: Request,
        post_id: str,
        comment_id: str,
        data: PostCommentUpdate,
        current_user: CurrentUser = Depends(get_current_user),
        social_client: SocialClient = Depends(get_social_client),
        comment_client: CommentClient = Depends(get_comment_client)
):
    """
    Обновление комментария к посту.
    """

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    # 1. Проверяем, существует ли пост
    post = await social_client.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 2. Обновляем комментарий в comment_service
    try:
        comment_result = await comment_client.update_post_comment(
            post_id=post_id,
            comment_id=comment_id,
            comment=data.comment,
            token=token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update comment: {str(e)}")

    return {
        "message": "Comment updated successfully",
        "comment": comment_result
    }


@router.delete("/posts/{post_id}/comment/{comment_id}", status_code=200)
async def delete_post_comment(
        request: Request,
        post_id: str,
        comment_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        social_client: SocialClient = Depends(get_social_client),
        comment_client: CommentClient = Depends(get_comment_client)
):
    """
    Удаление комментария к посту.
    Уменьшает счётчик комментариев в social_feed_service.
    """

    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    # 1. Проверяем, существует ли пост
    post = await social_client.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    # 2. Удаляем комментарий из comment_service
    try:
        await comment_client.delete_post_comment(
            post_id=post_id,
            comment_id=comment_id,
            token=token
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete comment: {str(e)}")

    # 3. Уменьшаем счётчик комментариев в social_feed_service
    try:
        await social_client.dec_post_comments(
            post_id=post_id,
            token=token
        )
    except Exception as e:
        print(f"Warning: Failed to decrement post comments counter: {e}")

    return {
        "message": "Comment deleted successfully"
    }


@router.post("/posts/{post_id}/comment/{comment_id}/reply", status_code=201)
async def reply_to_post_comment(
        request: Request,
        post_id: str,
        comment_id: str,
        data: CommentReplyCreate,
        current_user: CurrentUser = Depends(get_current_user),
        social_client: SocialClient = Depends(get_social_client),
        comment_client: CommentClient = Depends(get_comment_client)
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(status_code=401, detail="Missing authorization token")

    post = await social_client.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    try:
        comment_result = await comment_client.reply_to_post_comment(
            post_id=post_id,
            comment_id=comment_id,
            comment=data.comment,
            token=token,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create reply: {str(e)}")

    return {
        "message": "Reply created successfully",
        "comment": comment_result
    }


@router.post("/post/{post_id}/like")
async def post_like(
        request: Request,
        post_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        social_client: SocialClient = Depends(get_social_client),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(401, "Missing authorization token")
    post = await social_client.get_post(post_id)
    if not post:
        raise HTTPException(401, "Post not found")

    await social_client.like_post(post_id=post_id, token=token)


@router.post("/post/{post_id}/unlike")
async def post_unlike(
        request: Request,
        post_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        social_client: SocialClient = Depends(get_social_client),
):
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "")

    if not token:
        raise HTTPException(401, "Missing authorization token")
    post = await social_client.get_post(post_id)
    if not post:
        raise HTTPException(401, "Post not found")

    await social_client.unlike_post(post_id=post_id, token=token)
