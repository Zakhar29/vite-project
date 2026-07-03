from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import Optional
from datetime import datetime

from src.api.dependencies import (
    get_current_user,
    get_optional_current_user,
    CurrentUser,
    get_music_client,
    get_comment_client,
    get_users_client
)
from src.clients.music_service import MusicClient
from src.clients.comments_service import CommentClient
from src.clients.users_service import UsersClient
from src.api.helpers.format_date import parse_datetime, format_date_ru

router = APIRouter(prefix="/track-page", tags=["Track Page"])


# ========== ПОЛУЧЕНИЕ ИНФОРМАЦИИ О ТРЕКЕ ==========

@router.get("/{track_id}")
async def get_track_page(
        track_id: str,
        music_client: MusicClient = Depends(get_music_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение полной информации о треке для страницы.
    """

    # 1. Получаем полную информацию о треке
    try:
        track_info = await music_client.get_track_full(track_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Track not found: {str(e)}")

    if not track_info:
        raise HTTPException(status_code=404, detail="Track not found")

    # 2. Получаем информацию об авторе
    author_id = track_info.get("author_id")
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
    track_feats = track_info.get("feats", [])

    feats_info = []
    for feat_id in track_feats:
        try:
            feat_user = await users_client.get_user_info(feat_id)
            feats_info.append({
                "id": feat_id,
                "nickname": feat_user.get("user_nickname", "Пользователь"),
            })
        except Exception:
            feats_info.append({
                "id": feat_id,
                "nickname": "Пользователь",
            })
    published_at = track_info.get("published_at")
    if published_at:
        try:
            if isinstance(published_at, str):
                # Убираем Z и парсим
                dt_str = published_at.replace("+00:00", "")
                published_at_dt = datetime.fromisoformat(dt_str)
            else:
                published_at_dt = published_at
            
            published_at_formatted = format_date_ru(published_at_dt)
        except Exception as e:
            print(f"⚠️ Ошибка форматирования даты: {e}")
            # Если ошибка - ставим сегодня
            published_at_formatted = "сегодня"
    else:
        # Если даты нет - ставим сегодня
        published_at_formatted = "сегодня"

    # 4. Формируем ответ
    return {
        "track": {
            "track_id": track_info.get("track_id"),
            "title": track_info.get("title"),
            "cover_url": track_info.get("cover_url"),
            "author": author_info,
            "feats": feats_info,
            "track_url": track_info.get("track_url"),
            "track_text": track_info.get("track_text"),
            "bpm": track_info.get("bpm"),
            "genres": track_info.get("genres", []),
            "liked_quantity": track_info.get("liked_quantity", 0),
            "comments_quantity": track_info.get("comments_quantity", 0),
            "listening_quantity": track_info.get("listening_quantity", 0),
            "published_at": published_at_formatted,
            "published_at_raw": track_info.get("published_at")
        }
    }


# ========== ПОЛУЧЕНИЕ КОММЕНТАРИЕВ К ТРЕКУ (ОТДЕЛЬНЫЙ ЭНДПОИНТ) ==========

@router.get("/{track_id}/comments")
async def get_track_comments(
        track_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        sort_by: str = Query("created_at", pattern="^(created_at|likes_quantity|rating_quantity)$"),
        sort_order: str = Query("asc", pattern="^(asc|desc)$"),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        music_client: MusicClient = Depends(get_music_client),
        comment_client: CommentClient = Depends(get_comment_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение комментариев к треку (с пагинацией и сортировкой).
    Отдельный эндпоинт для ленивой загрузки.
    """

    # 1. Проверяем, существует ли трек
    try:
        track_info = await music_client.get_track(track_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Track not found")

    if not track_info:
        raise HTTPException(status_code=404, detail="Track not found")

    # 2. Получаем комментарии из comment_service
    try:
        comments_result = await comment_client.list_track_comments(
            track_id=track_id,
            root_only=True,
            skip=skip,
            limit=limit
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
            "track_timecode": comment.get("track_timecode"),
            "created_at": created_at_formatted or comment.get("created_at"),
            "created_at_formatted": created_at_formatted,
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