from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
from datetime import datetime

from src.api.dependencies import (
    get_current_user,
    get_optional_current_user,
    CurrentUser,
    get_users_client,
    get_music_client,
    get_social_client
)
from src.clients.users_service import UsersClient
from src.clients.music_service import MusicClient
from src.clients.social_feed_service import SocialClient

router = APIRouter(prefix="/search", tags=["Search"])


# ========== ПОИСК ПОЛЬЗОВАТЕЛЕЙ ==========

@router.get("/users")
async def search_users(
        query: str = Query(..., min_length=1, max_length=100),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Поиск пользователей по никнейму.
    """
    result = await users_client.search_users(
        query=query,
        skip=skip,
        limit=limit,
        sort_by="relevance",
        sort_order="desc"
    )

    return {
        "items": result.get("items", []),
        "total": result.get("total", 0),
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < result.get("total", 0),
        "search_query": query
    }


# ========== ПОИСК ТРЕКОВ ==========

@router.get("/tracks")
async def search_tracks(
        query: Optional[str] = Query(None, min_length=1, max_length=100),
        genre_ids: Optional[str] = Query(None),
        bpm_min: Optional[float] = Query(None, ge=10, le=1000),
        bpm_max: Optional[float] = Query(None, ge=10, le=1000),
        sort_by: str = Query("relevance"),
        sort_order: str = Query("desc"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        music_client: MusicClient = Depends(get_music_client)
):
    """
    Поиск треков с фильтрацией.
    """
    genre_list = None
    if genre_ids:
        try:
            genre_list = [int(g) for g in genre_ids.split(",") if g]
        except ValueError:
            pass

    result = await music_client.search_tracks(
        query=query,
        genre_ids=genre_list,
        bpm_min=bpm_min,
        bpm_max=bpm_max,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )

    return {
        "items": result.get("items", []),
        "total": result.get("total", 0),
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < result.get("total", 0),
        "search_query": query
    }


# ========== ПОИСК АЛЬБОМОВ ==========

@router.get("/albums")
async def search_albums(
        query: Optional[str] = Query(None, min_length=1, max_length=100),
        genre_ids: Optional[str] = Query(None),
        album_type: Optional[int] = Query(None),
        sort_by: str = Query("relevance"),
        sort_order: str = Query("desc"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        music_client: MusicClient = Depends(get_music_client)
):
    """
    Поиск альбомов с фильтрацией.
    """
    genre_list = None
    if genre_ids:
        try:
            genre_list = [int(g) for g in genre_ids.split(",") if g]
        except ValueError:
            pass

    result = await music_client.search_albums(
        query=query,
        genre_ids=genre_list,
        album_type=album_type,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )

    return {
        "items": result.get("items", []),
        "total": result.get("total", 0),
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < result.get("total", 0),
        "search_query": query
    }


# ========== ПОИСК ПОСТОВ ==========

@router.get("/posts")
async def search_posts(
        query: Optional[str] = Query(None, min_length=1, max_length=100),
        sort_by: str = Query("created_at"),
        sort_order: str = Query("desc"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        social_client: SocialClient = Depends(get_social_client)
):
    """
    Поиск постов (по тексту).
    """
    # В social_feed_service нет прямого поиска, используем list_posts с фильтрацией
    # Для полноценного поиска нужно добавить эндпоинт в social_feed_service
    result = await social_client.list_posts(
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )

    # Фильтруем посты по тексту на стороне BFF (временное решение)
    items = result.get("items", [])
    if query:
        items = [post for post in items if query.lower() in post.get("text", "").lower()]

    return {
        "items": items,
        "total": len(items),
        "skip": skip,
        "limit": limit,
        "has_more": False,
        "search_query": query
    }


# ========== ГЛОБАЛЬНЫЙ ПОИСК ==========

@router.get("/all")
async def global_search(
        query: str = Query(..., min_length=1, max_length=100),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=50),
        current_user: Optional[CurrentUser] = Depends(get_optional_current_user),
        users_client: UsersClient = Depends(get_users_client),
        music_client: MusicClient = Depends(get_music_client),
        social_client: SocialClient = Depends(get_social_client)
):
    """
    Глобальный поиск по всем категориям.
    """
    # Поиск пользователей
    users_result = await users_client.search_users(query=query, skip=0, limit=5)

    # Поиск треков
    tracks_result = await music_client.search_tracks(query=query, skip=0, limit=5)

    # Поиск альбомов
    albums_result = await music_client.search_albums(query=query, skip=0, limit=5)

    # Поиск постов (ограниченно)
    posts_result = await social_client.list_posts(skip=0, limit=10)
    posts_items = posts_result.get("items", [])
    if query:
        posts_items = [post for post in posts_items if query.lower() in post.get("text", "").lower()]

    return {
        "query": query,
        "users": {
            "items": users_result.get("items", [])[:5],
            "total": users_result.get("total", 0)
        },
        "tracks": {
            "items": tracks_result.get("items", [])[:5],
            "total": tracks_result.get("total", 0)
        },
        "albums": {
            "items": albums_result.get("items", [])[:5],
            "total": albums_result.get("total", 0)
        },
        "posts": {
            "items": posts_items[:5],
            "total": len(posts_items)
        }
    }