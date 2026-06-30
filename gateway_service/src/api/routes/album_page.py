from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional, List
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
from src.api.helpers.format_date import format_date_ru

router = APIRouter(prefix="/album", tags=["Album Page"])


# ========== ПОЛУЧЕНИЕ ИНФОРМАЦИИ ОБ АЛЬБОМЕ ==========

@router.get("/{album_id}")
async def get_album_page(
        album_id: str,
        music_client: MusicClient = Depends(get_music_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение полной информации об альбоме для страницы.
    """

    # 1. Получаем информацию об альбоме
    try:
        album_info = await music_client.get_album(album_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Album not found: {str(e)}")

    if not album_info:
        raise HTTPException(status_code=404, detail="Album not found")

    # 2. Получаем информацию об авторе
    author_id = album_info.get("author_id")
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

    # 3. Форматируем дату публикации
    published_at = album_info.get("published_at")
    published_at_formatted = None
    if published_at:
        try:
            if isinstance(published_at, str):
                published_at_dt = datetime.fromisoformat(published_at.replace("+00:00", ""))
            else:
                published_at_dt = published_at
            published_at_formatted = format_date_ru(published_at_dt)
        except Exception:
            pass

    # 4. Получаем треки альбома с обогащением
    tracks = album_info.get("tracks", [])
    enriched_tracks = []

    for track in tracks:
        # Получаем жанры для каждого трека (если не пришли в ответе)
        track_genres = track.get("genres", [])

        # Получаем фиты для каждого трека
        track_feats = track.get("feats", [])

        # Получаем информацию об авторах фитов (если есть)
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

        enriched_tracks.append({
            "track_id": track.get("track_id"),
            "title": track.get("title"),
            "track_url": track.get("track_url"),
            "bpm": track.get("bpm"),
            "genres": track_genres,
            "feats": feats_info,
            "listening_quantity": track.get("listening_quantity", 0),
            "liked_quantity": track.get("liked_quantity", 0),
            "comments_quantity": track.get("comments_quantity", 0),
        })

    # 5. Формируем ответ
    return {
        "album": {
            "id": album_info.get("id"),
            "title": album_info.get("title"),
            "author": author_info,
            "cover_url": album_info.get("cover_url"),
            "type_id": album_info.get("type_id"),
            "type": album_info.get("type"),
            "liked_quantity": album_info.get("liked_quantity", 0),
            "follower_quantity": album_info.get("follower_quantity", 0),
            "listening_quantity": album_info.get("listening_quantity", 0),
            "comments_quantity": album_info.get("comments_quantity", 0),
            "tracks_count": len(enriched_tracks),
            "tracks": enriched_tracks,
            "published_at": published_at_formatted,
            "published_at_raw": album_info.get("published_at")
        }
    }

