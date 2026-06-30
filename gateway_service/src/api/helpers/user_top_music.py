from fastapi import APIRouter, Depends, HTTPException, Request, Query
from typing import Optional, List
from datetime import datetime
import random

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
from src.api.helpers.format_date import parse_datetime, format_date_ru


async def get_top_tracks(
    user_id: str, 
    music_client: MusicClient, 
    users_client: UsersClient,
    limit: int = 5
) -> List[dict]:
    """
    Получение топ-5 треков пользователя по прослушиваниям.
    """
    result = await music_client.search_tracks(
        author_id=user_id,
        sort_by="listening_quantity",
        sort_order="desc",
        limit=limit * 2
    )

    tracks = result.get("items", [])

    def track_score(track):
        return (
            track.get("listening_quantity", 0),
            track.get("liked_quantity", 0),
            track.get("comments_quantity", 0)
        )

    tracks.sort(key=track_score, reverse=True)
    top_tracks = tracks[:limit]
    random.shuffle(top_tracks)

    # Обогащаем данными авторов
    enriched_tracks = []
    for track in top_tracks:
        author_id = track.get("author_id")
        author_data = {}
        if author_id:
            try:
                user_info = await users_client.get_user_info(author_id)
                author_data = {
                    "id": author_id,
                    "nickname": user_info.get("user_nickname", "Пользователь"),
                    "avatar_url": user_info.get("user_avatar", "/static/default-avatar.png")
                }
            except Exception:
                author_data = {
                    "id": author_id,
                    "nickname": "Пользователь",
                    "avatar_url": "/static/default-avatar.png"
                }
        published_at = track.get("published_at")
        published_at_formatted = None
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

        enriched_track = {
            **track,
            "author": author_data,
            "published_at_formatted": published_at_formatted
        }
        enriched_tracks.append(enriched_track)

    return enriched_tracks


async def get_recent_albums(
    user_id: str, 
    music_client: MusicClient,
    users_client: UsersClient,
    limit: int = 5
) -> List[dict]:
    """
    Получение последних 5 альбомов пользователя.
    """
    result = await music_client.search_albums(
        author_id=user_id,
        sort_by="published_at",
        sort_order="desc",
        limit=limit
    )

    albums = result.get("items", [])

    # Обогащаем данными авторов
    enriched_albums = []
    for album in albums:
        author_id = album.get("author_id")
        author_data = {}
        if author_id:
            try:
                user_info = await users_client.get_user_info(author_id)
                author_data = {
                    "id": author_id,
                    "nickname": user_info.get("user_nickname", "Пользователь"),
                    "avatar_url": user_info.get("user_avatar", "/static/default-avatar.png")
                }
            except Exception:
                author_data = {
                    "id": author_id,
                    "nickname": "Пользователь",
                    "avatar_url": "/static/default-avatar.png"
                }
        published_at = album.get("published_at")
        published_at_formatted = None
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

        enriched_album = {
            **album,
            "author": author_data,
            "published_at_formatted": published_at_formatted
        }
        enriched_albums.append(enriched_album)

    return enriched_albums