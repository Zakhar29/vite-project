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
        # ===== УБИРАЕМ ЗАВИСИМОСТЬ ОТ АВТОРИЗАЦИИ =====
        # current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        users_client: UsersClient = Depends(get_users_client),
        social_client: SocialClient = Depends(get_social_client)
):
    """
    Получение ленты постов для главной страницы.
    ПОЛНОСТЬЮ ПУБЛИЧНЫЙ ЭНДПОИНТ - не требует авторизации.
    """

    # ===== ПЫТАЕМСЯ ПОЛУЧИТЬ ПОЛЬЗОВАТЕЛЯ, НО НЕ ТРЕБУЕМ =====
    is_authenticated = False
    current_user = None
    token = None
    
    # Проверяем Authorization header
    auth_header = request.headers.get("Authorization", "")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        # Пытаемся получить пользователя через get_optional_current_user
        try:
            # Создаем зависимость вручную
            from src.api.dependencies import get_optional_current_user
            # Это не сработает напрямую, поэтому используем другой подход
        except:
            pass
    
    # Вместо этого используем простой подход - получаем user_id из токена если есть
    user_id = None
    if token:
        try:
            import jwt
            from config import settings
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}
            )
            user_uuid = payload.get("user_id") or payload.get("sub")
            if user_uuid:
                user_id = str(user_uuid)
                is_authenticated = True
        except Exception:
            pass

    following_ids = []

    # ========== 1. ПОЛУЧАЕМ СПИСОК ПОДПИСОК (ТОЛЬКО ДЛЯ АВТОРИЗОВАННЫХ) ==========
    if is_authenticated and user_id:
        try:
            following = await users_client.get_following(
                user_id=user_id,
                skip=0,
                limit=100
            )
            if isinstance(following, dict):
                following_items = following.get("items", [])
                following_ids = [user.get("id") for user in following_items if user.get("id")]
            elif isinstance(following, list):
                following_ids = [user.get("id") for user in following if user.get("id")]
        except Exception as e:
            print(f"Warning: Failed to get following list: {e}")
            following_ids = []

    # ========== 2. ПОЛУЧАЕМ РЕКОМЕНДАЦИИ ПОСТОВ ==========
    posts = []
    total = 0
    
    try:
        # Если есть подписки — передаём их
        posts_result = await social_client.get_recommended_posts(
            following_ids=following_ids if following_ids else None,
            skip=skip,
            limit=limit
        )
        
        # Извлекаем посты
        if isinstance(posts_result, dict):
            posts = posts_result.get("items", [])
            total = posts_result.get("total", 0)
        elif isinstance(posts_result, list):
            posts = posts_result
            total = len(posts)
        
        # ===== ФИЛЬТРУЕМ НЕВАЛИДНЫЕ ПОСТЫ =====
        valid_posts = []
        for post in posts:
            if isinstance(post, dict) and post.get("id"):
                valid_posts.append(post)
            else:
                print(f"⚠️ Пропускаем невалидный пост: {post}")
        
        posts = valid_posts
        
    except Exception as e:
        print(f"❌ Ошибка получения постов: {e}")
        # Fallback: получаем популярные посты
        try:
            popular_result = await social_client.list_posts(
                skip=0,
                limit=limit,
                sort_by="likes_quantity",
                sort_order="desc"
            )
            if isinstance(popular_result, dict):
                posts = popular_result.get("items", [])
                total = popular_result.get("total", 0)
            elif isinstance(popular_result, list):
                posts = popular_result
                total = len(posts)
        except Exception as e2:
            print(f"❌ Ошибка получения популярных постов: {e2}")
            posts = []
            total = 0

    # ========== 3. ИЗВЛЕКАЕМ АВТОРОВ ==========
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
        "total": total if total > 0 else len(formatted_posts),
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total,
        "feed_type": "mixed" if following_ids else "popular"
    }

    # Добавляем данные пользователя только если авторизован
    if is_authenticated and user_id:
        try:
            # Пытаемся получить данные пользователя
            user_info = await users_client.get_user_info(user_id)
            response_data["user"] = {
                "id": user_id,
                "nickname": user_info.get("user_nickname", "Пользователь"),
                "avatar_url": user_info.get("user_avatar", "/static/default-avatar.png")
            }
        except Exception:
            pass

    return response_data
