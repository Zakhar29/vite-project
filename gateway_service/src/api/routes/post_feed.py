from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import Optional, List
from datetime import datetime

from src.api.dependencies import (
    get_current_user,
    get_optional_current_user,
    CurrentUser,
    get_users_client,
    get_social_client
)
from src.api.helpers.format_date import format_date_ru
from src.clients.social_feed_service import SocialClient
from src.clients.users_service import UsersClient


router = APIRouter(prefix="/feed", tags=["Feed"])


@router.get("/main")
async def get_feed(
        request: Request,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=50),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        users_client: UsersClient = Depends(get_users_client),
        social_client: SocialClient = Depends(get_social_client)
):
    """
    Получение ленты постов для главной страницы.

    Алгоритм:
    1. Если пользователь авторизован:
       - Получаем список подписок
       - Если есть подписки → смешанная лента (посты подписок + популярные)
       - Если нет подписок → только популярные посты
    2. Если пользователь не авторизован:
       - Только популярные посты
    """

    # Получаем токен (если есть)
    auth_header = request.headers.get("Authorization", "")
    token = auth_header.replace("Bearer ", "") if auth_header else None

    following_ids = []
    is_authenticated = current_user is not None

    # ========== 1. ПОЛУЧАЕМ СПИСОК ПОДПИСОК (ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ) ==========
    if is_authenticated and token:
        try:
            following = await users_client.get_following(
                user_id=str(current_user.id),
                skip=0,
                limit=100
            )
            # Извлекаем ID пользователей, на которых подписан
            if isinstance(following, dict):
                following_items = following.get("items", [])
                following_ids = [user.get("id") for user in following_items if user.get("id")]
            elif isinstance(following, list):
                following_ids = [user.get("id") for user in following if user.get("id")]
        except Exception as e:
            print(f"Warning: Failed to get following list: {e}")
            following_ids = []

    # ========== 2. ПОЛУЧАЕМ РЕКОМЕНДАЦИИ ПОСТОВ ==========
    try:
        # Если есть подписки — передаём их, иначе social_service вернёт только популярные
        posts_result = await social_client.get_recommended_posts(
            following_ids=following_ids if following_ids else None,
            skip=skip,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get posts: {str(e)}")

    # ========== 3. ИЗВЛЕКАЕМ АВТОРОВ ДЛЯ ОБОГАЩЕНИЯ ДАННЫМИ ==========
    posts = posts_result.get("items", [])
    author_ids = list(set([post.get("author_id") for post in posts if post.get("author_id")]))

    # ========== 4. ПОЛУЧАЕМ ДАННЫЕ АВТОРОВ ==========
    authors_data = {}
    for author_id in author_ids:
        try:
            user_info = await users_client.get_user_info(author_id)
            authors_data[author_id] = {
                "id": author_id,
                "nickname": user_info.get("user_nickname", "Пользователь"),
                "avatar_url": user_info.get("user_avatar", "/static/default-avatar.png")
            }
        except Exception:
            authors_data[author_id] = {
                "id": author_id,
                "nickname": "Пользователь",
                "avatar_url": "/static/default-avatar.png"
            }

    # ========== 5. ФОРМАТИРУЕМ ПОСТЫ ==========
    formatted_posts = []
    for post in posts:
        author_id = post.get("author_id")
        author = authors_data.get(author_id, {})

        created_at = post.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except:
                created_at = datetime.now()
        elif not created_at:
            created_at = datetime.now()

        formatted_posts.append({
            "id": post.get("id"),
            "text": post.get("text", ""),
            "media": post.get("media", []),
            "created_at_formatted": format_date_ru(created_at),
            "created_at_raw": created_at.isoformat() if created_at else None,
            "likes_quantity": post.get("likes_quantity", 0),
            "comments_quantity": post.get("comments_quantity", 0),
            "author": {
                "id": author.get("id"),
                "nickname": author.get("nickname"),
                "avatar_url": author.get("avatar_url")
            }
        })

    # ========== 6. ФОРМИРУЕМ ОТВЕТ ==========
    response_data = {
        "posts": formatted_posts,
        "total": posts_result.get("total", 0),
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < posts_result.get("total", 0),
        "feed_type": "mixed" if following_ids else "popular"
    }

    # Добавляем данные пользователя только для авторизованных
    if is_authenticated and current_user:
        response_data["user"] = {
            "id": str(current_user.id),
            "nickname": current_user.nickname,
            "avatar_url": current_user.avatar_url
        }

    return response_data
