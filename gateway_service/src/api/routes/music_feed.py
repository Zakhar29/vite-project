from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from src.api.dependencies import (
    get_current_user,
    get_users_client,
    get_optional_current_user,
    CurrentUser,
    get_music_client
)
from src.clients.music_service import MusicClient
from src.clients.users_service import UsersClient
from src.api.helpers.format_date import format_date_ru

from src.api.schemas import (
    TrackRecommendationResponse,
    AlbumRecommendationResponse,
    RecommendationsResponse

)
router = APIRouter(prefix="/music-feed", tags=["Feed"])


@router.get("/tracks", response_model=RecommendationsResponse)
async def get_track_recommendations(
        request: Request,
        limit: int = Query(20, ge=1, le=100),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        music_client: MusicClient = Depends(get_music_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение рекомендаций треков.

    - Если пользователь авторизован: персонализированные рекомендации
    - Если не авторизован: глобальные популярные треки
    """

    user_id = None
    if current_user:
        user_id = str(current_user.id)

    try:
        result = await music_client.get_track_recommendations(
            user_id=user_id,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get track recommendations: {str(e)}")

    # Извлекаем items из результата
    items = result.get("items", []) if isinstance(result, dict) else []
    rec_type = result.get("type", "global") if isinstance(result, dict) else "global"

    # Собираем уникальные author_id для получения данных авторов
    author_ids = list(set([item.get("author_id") for item in items if item.get("author_id")]))

    # Получаем данные авторов
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

    # Форматируем каждый трек
    formatted_items = []
    for item in items:
        author_id = item.get("author_id")
        author = authors_data.get(author_id, {})

        # Форматируем дату публикации
        published_at = item.get("published_at")
        published_at_formatted = None
        published_at_raw = None

        if published_at:
            try:
                if isinstance(published_at, str):
                    published_at_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                else:
                    published_at_dt = published_at
                published_at_formatted = format_date_ru(published_at_dt)
                published_at_raw = published_at_dt.isoformat()
            except Exception:
                pass

        formatted_items.append({
            "track_id": item.get("track_id"),
            "title": item.get("title"),
            "album_id": item.get("album_id"),
            "cover_url": item.get("cover_url"),
            "author_id": author_id,
            "author_nickname": author.get("nickname"),
            "author_avatar": author.get("avatar_url"),
            "feats": item.get("feats", []),
            "track_url": item.get("track_url"),
            "bpm": item.get("bpm"),
            "genres": item.get("genres", []),
            "liked_quantity": item.get("liked_quantity", 0),
            "comments_quantity": item.get("comments_quantity", 0),
            "listening_quantity": item.get("listening_quantity", 0),
            "published_at_formatted": published_at_formatted,
            "published_at_raw": published_at_raw
        })

    return RecommendationsResponse(
        items=formatted_items,
        total=len(formatted_items),
        type=rec_type
    )


# ========== РЕКОМЕНДАЦИИ АЛЬБОМОВ ==========

@router.get("/albums", response_model=RecommendationsResponse)
async def get_album_recommendations(
        request: Request,
        limit: int = Query(20, ge=1, le=100),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        music_client: MusicClient = Depends(get_music_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение рекомендаций альбомов.

    - Если пользователь авторизован: персонализированные рекомендации
    - Если не авторизован: глобальные популярные альбомы
    """

    user_id = None
    if current_user:
        user_id = str(current_user.id)

    try:
        result = await music_client.get_album_recommendations(
            user_id=user_id,
            limit=limit
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get album recommendations: {str(e)}")

    # Извлекаем items из результата
    items = result.get("items", []) if isinstance(result, dict) else []
    rec_type = result.get("type", "global") if isinstance(result, dict) else "global"

    # Собираем уникальные author_id для получения данных авторов
    author_ids = list(set([item.get("author_id") for item in items if item.get("author_id")]))

    # Получаем данные авторов
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

    # Форматируем каждый альбом
    formatted_items = []
    for item in items:
        author_id = item.get("author_id")
        author = authors_data.get(author_id, {})

        # Форматируем дату публикации
        published_at = item.get("published_at")
        published_at_formatted = None
        published_at_raw = None

        if published_at:
            try:
                if isinstance(published_at, str):
                    published_at_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                else:
                    published_at_dt = published_at
                published_at_formatted = format_date_ru(published_at_dt)
                published_at_raw = published_at_dt.isoformat()
            except Exception:
                pass

        formatted_items.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "author_id": author_id,
            "author_nickname": author.get("nickname"),
            "author_avatar": author.get("avatar_url"),
            "cover_url": item.get("cover_url"),
            "type_id": item.get("type_id"),
            "type": item.get("type"),
            "genres": item.get("genres", []),
            "liked_quantity": item.get("liked_quantity", 0),
            "follower_quantity": item.get("follower_quantity", 0),
            "listening_quantity": item.get("listening_quantity", 0),
            "comments_quantity": item.get("comments_quantity", 0),
            "tracks_count": item.get("tracks_count", 0),
            "published_at_formatted": published_at_formatted,
            "published_at_raw": published_at_raw
        })

    return RecommendationsResponse(
        items=formatted_items,
        total=len(formatted_items),
        type=rec_type
    )


# ========== СМЕШАННЫЕ РЕКОМЕНДАЦИИ (ДЛЯ ГЛАВНОЙ СТРАНИЦЫ) ==========

@router.get("/mixed")
async def get_mixed_recommendations(
        request: Request,
        tracks_limit: int = Query(10, ge=1, le=50),
        albums_limit: int = Query(10, ge=1, le=50),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        music_client: MusicClient = Depends(get_music_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение смешанных рекомендаций (треки + альбомы) для главной страницы.
    """

    user_id = None
    if current_user:
        user_id = str(current_user.id)

    # Получаем рекомендации треков
    tracks_result = await music_client.get_track_recommendations(
        user_id=user_id,
        limit=tracks_limit
    )

    # Получаем рекомендации альбомов
    albums_result = await music_client.get_album_recommendations(
        user_id=user_id,
        limit=albums_limit
    )

    tracks_items = tracks_result.get("items", []) if isinstance(tracks_result, dict) else []
    albums_items = albums_result.get("items", []) if isinstance(albums_result, dict) else []

    # Собираем все author_id из треков и альбомов
    author_ids = set()
    for item in tracks_items:
        if item.get("author_id"):
            author_ids.add(item.get("author_id"))
    for item in albums_items:
        if item.get("author_id"):
            author_ids.add(item.get("author_id"))

    # Получаем данные авторов
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

    # Форматируем треки
    formatted_tracks = []
    for item in tracks_items:
        author_id = item.get("author_id")
        author = authors_data.get(author_id, {})

        published_at = item.get("published_at")
        published_at_formatted = None
        if published_at:
            try:
                if isinstance(published_at, str):
                    published_at_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                else:
                    published_at_dt = published_at
                published_at_formatted = format_date_ru(published_at_dt)
            except Exception:
                pass

        formatted_tracks.append({
            "track_id": item.get("track_id"),
            "title": item.get("title"),
            "album_id": item.get("album_id"),
            "cover_url": item.get("cover_url"),
            "author_id": author_id,
            "author_nickname": author.get("nickname"),
            "author_avatar": author.get("avatar_url"),
            "feats": item.get("feats", []),
            "track_url": item.get("track_url"),
            "bpm": item.get("bpm"),
            "genres": item.get("genres", []),
            "liked_quantity": item.get("liked_quantity", 0),
            "comments_quantity": item.get("comments_quantity", 0),
            "listening_quantity": item.get("listening_quantity", 0),
            "published_at_formatted": published_at_formatted
        })

    # Форматируем альбомы
    formatted_albums = []
    for item in albums_items:
        author_id = item.get("author_id")
        author = authors_data.get(author_id, {})

        published_at = item.get("published_at")
        published_at_formatted = None
        if published_at:
            try:
                if isinstance(published_at, str):
                    published_at_dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
                else:
                    published_at_dt = published_at
                published_at_formatted = format_date_ru(published_at_dt)
            except Exception:
                pass

        formatted_albums.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "author_id": author_id,
            "author_nickname": author.get("nickname"),
            "author_avatar": author.get("avatar_url"),
            "cover_url": item.get("cover_url"),
            "type_id": item.get("type_id"),
            "type": item.get("type"),
            "genres": item.get("genres", []),
            "liked_quantity": item.get("liked_quantity", 0),
            "follower_quantity": item.get("follower_quantity", 0),
            "listening_quantity": item.get("listening_quantity", 0),
            "comments_quantity": item.get("comments_quantity", 0),
            "tracks_count": item.get("tracks_count", 0),
            "published_at_formatted": published_at_formatted
        })

    return {
        "tracks": {
            "items": formatted_tracks,
            "total": len(formatted_tracks),
            "type": tracks_result.get("type", "global") if isinstance(tracks_result, dict) else "global"
        },
        "albums": {
            "items": formatted_albums,
            "total": len(formatted_albums),
            "type": albums_result.get("type", "global") if isinstance(albums_result, dict) else "global"
        },
        "user": {
            "id": str(current_user.id) if current_user else None,
            "nickname": current_user.nickname if current_user else None,
            "avatar_url": current_user.avatar_url if current_user else None,
            "is_authenticated": current_user is not None
        }
    }