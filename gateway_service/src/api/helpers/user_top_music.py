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


async def get_top_tracks(user_id: str, music_client: MusicClient, limit: int = 5) -> List[dict]:
    """
    Получение топ-5 треков пользователя по прослушиваниям, лайкам и комментариям.
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

    return top_tracks


async def get_recent_albums(user_id: str, music_client: MusicClient, limit: int = 5) -> List[dict]:
    """
    Получение последних 5 альбомов пользователя.
    """
    result = await music_client.search_albums(
        author_id=user_id,
        sort_by="published_at",
        sort_order="desc",
        limit=limit
    )

    return result.get("items", [])