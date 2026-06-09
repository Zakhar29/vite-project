from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import Optional
from datetime import datetime

from src.api.dependencies import (
    get_current_user,
    get_optional_current_user,
    CurrentUser,
    get_social_client,
    get_comment_client,
    get_users_client
)
from src.clients.social_feed_service import SocialClient
from src.clients.comments_service import CommentClient
from src.clients.users_service import UsersClient
from src.api.helpers.format_date import format_date_ru

router = APIRouter(prefix="/post-page", tags=["Post Page"])


# ========== ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ПОСТЕ ==========

@router.get("/{post_id}")
async def get_post_page(
        post_id: str,
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        social_client: SocialClient = Depends(get_social_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение полной информации о посте для страницы.
    """

    # 1. Получаем информацию о посте
    try:
        post_info = await social_client.get_post(post_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Post not found: {str(e)}")

    if not post_info:
        raise HTTPException(status_code=404, detail="Post not found")

    # 2. Получаем информацию об авторе
    author_id = post_info.get("author_id")
    author_info = {}
    if author_id:
        try:
            user_info = await users_client.get_user_info(author_id)
            author_info = {
                "id": author_id,
                "nickname": user_info.get("user_nickname", "Пользователь"),
                "avatar_url": user_info.get("user_avatar", "/static/default-avatar.png")
            }
        except Exception:
            author_info = {
                "id": author_id,
                "nickname": "Пользователь",
                "avatar_url": "/static/default-avatar.png"
            }

    # 3. Форматируем дату создания
    created_at = post_info.get("created_at")
    created_at_formatted = None
    if created_at:
        try:
            if isinstance(created_at, str):
                created_at_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            else:
                created_at_dt = created_at
            created_at_formatted = format_date_ru(created_at_dt)
        except Exception:
            pass

    # 4. Формируем ответ
    return {
        "post": {
            "id": post_info.get("id"),
            "author": author_info,
            "text": post_info.get("text", ""),
            "media": post_info.get("media", []),
            "created_at": created_at_formatted,
            "created_at_raw": post_info.get("created_at"),
            "updated_at": post_info.get("updated_at"),
            "likes_quantity": post_info.get("likes_quantity", 0),
            "comments_quantity": post_info.get("comments_quantity", 0)
        },
        "user": {
            "id": str(current_user.id) if current_user else None,
            "nickname": current_user.nickname if current_user else None,
            "avatar_url": current_user.avatar_url if current_user else None,
            "is_authenticated": current_user is not None
        }
    }


# ========== ПОЛУЧЕНИЕ КОММЕНТАРИЕВ К ПОСТУ (ОТДЕЛЬНЫЙ ЭНДПОИНТ) ==========

@router.get("/{post_id}/comments")
async def get_post_comments(
        post_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        sort_by: str = Query("created_at", pattern="^(created_at|likes_quantity|rating_quantity)$"),
        sort_order: str = Query("asc", pattern="^(asc|desc)$"),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        social_client: SocialClient = Depends(get_social_client),
        comment_client: CommentClient = Depends(get_comment_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение комментариев к посту (с пагинацией и сортировкой).
    Отдельный эндпоинт для ленивой загрузки.
    """

    # 1. Проверяем, существует ли пост
    try:
        post_info = await social_client.get_post(post_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Post not found")

    if not post_info:
        raise HTTPException(status_code=404, detail="Post not found")

    # 2. Получаем комментарии из comment_service
    try:
        comments_result = await comment_client.list_post_comments(
            post_id=post_id,
            root_only=True,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_order=sort_order
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get comments: {str(e)}")

    # 3. Извлекаем список комментариев
    comments = comments_result.get("items", []) if isinstance(comments_result, dict) else []

    # 4. Собираем уникальные author_id для получения данных авторов
    author_ids = list(set([comment.get("author_id") for comment in comments if comment.get("author_id")]))

    # 5. Получаем данные авторов комментариев
    authors_data = {}
    for author_id in author_ids:
        try:
            user_info = await users_client.get_user_info(author_id)
            authors_data[author_id] = {
                "nickname": user_info.get("user_nickname", "Пользователь"),
                "avatar_url": user_info.get("user_avatar", "/static/default-avatar.png")
            }
        except Exception:
            authors_data[author_id] = {
                "nickname": "Пользователь",
                "avatar_url": "/static/default-avatar.png"
            }

    # 6. Форматируем комментарии
    formatted_comments = []
    for comment in comments:
        author_id = comment.get("author_id")
        author = authors_data.get(author_id, {})

        created_at = comment.get("created_at")
        created_at_formatted = None
        if created_at:
            try:
                if isinstance(created_at, str):
                    created_at_dt = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                else:
                    created_at_dt = created_at
                created_at_formatted = format_date_ru(created_at_dt)
            except Exception:
                pass

        formatted_comments.append({
            "id": comment.get("id"),
            "author": {
                "id": author_id,
                "nickname": author.get("nickname"),
                "avatar_url": author.get("avatar_url")
            },
            "comment": comment.get("comment"),
            "created_at": created_at_formatted,
            "created_at_raw": comment.get("created_at"),
            "likes_quantity": comment.get("likes_quantity", 0),
            "dislikes_quantity": comment.get("dislikes_quantity", 0),
            "rating_quantity": comment.get("rating_quantity", 0),
            "answer_quantity": comment.get("answer_quantity", 0)
        })

    return {
        "items": formatted_comments,
        "total": comments_result.get("total", 0) if isinstance(comments_result, dict) else len(comments),
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < comments_result.get("total", 0) if isinstance(comments_result, dict) else False
    }