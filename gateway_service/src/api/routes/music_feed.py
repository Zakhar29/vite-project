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
            "published_at_raw": published_at
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
                    published_at_dt = datetime.fromisoformat(published_at.replace("+00:00", ""))
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
        # Убираем зависимость от авторизации полностью
        music_client: MusicClient = Depends(get_music_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение смешанных рекомендаций (треки + альбомы) для главной страницы.
    ПОЛНОСТЬЮ ПУБЛИЧНЫЙ эндпоинт - не требует авторизации.
    """
    import uuid

    # Пытаемся получить пользователя из заголовка, но не требуем
    user_id = None
    is_authenticated = False

    # Проверяем Authorization header вручную
    auth_header = request.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header.replace("Bearer ", "")
        try:
            # Декодируем токен без проверки (просто получаем user_id)
            import jwt
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}  # Не проверяем истечение
            )
            user_uuid = payload.get("user_id") or payload.get("sub")
            if user_uuid:
                user_id = uuid.UUID(str(user_uuid))
                is_authenticated = True
        except Exception:
            # Если не удалось декодировать - просто игнорируем
            pass

    # Получаем рекомендации треков
    tracks_items = []
    tracks_type = "global"

    try:
        tracks_result = await music_client.get_track_recommendations(
            user_id=user_id if is_authenticated else None,
            limit=tracks_limit
        )

        tracks_items = tracks_result.get("items", []) if isinstance(tracks_result, dict) else []
        tracks_type = tracks_result.get("type", "global") if isinstance(tracks_result, dict) else "global"

    except Exception as e:
        print(f"Error getting track recommendations: {e}")
        # Fallback: получаем популярные через поиск
        try:
            tracks_result = await music_client.search_tracks(
                sort_by="listening_quantity",
                sort_order="desc",
                limit=tracks_limit
            )
            tracks_items = tracks_result.get("items", []) if isinstance(tracks_result, dict) else []
            tracks_type = "popular"
        except Exception:
            tracks_items = []
            tracks_type = "error"

    # Получаем рекомендации альбомов
    albums_items = []
    albums_type = "global"

    try:
        albums_result = await music_client.get_album_recommendations(
            user_id=user_id if is_authenticated else None,
            limit=albums_limit
        )

        albums_items = albums_result.get("items", []) if isinstance(albums_result, dict) else []
        albums_type = albums_result.get("type", "global") if isinstance(albums_result, dict) else "global"

    except Exception as e:
        print(f"Error getting album recommendations: {e}")
        # Fallback: получаем популярные через поиск
        try:
            albums_result = await music_client.search_albums(
                sort_by="listening_quantity",
                sort_order="desc",
                limit=albums_limit
            )
            albums_items = albums_result.get("items", []) if isinstance(albums_result, dict) else []
            albums_type = "popular"
        except Exception:
            albums_items = []
            albums_type = "error"

    # Если нет рекомендаций - получаем просто популярное
    if not tracks_items and not albums_items:
        try:
            tracks_result = await music_client.search_tracks(
                sort_by="listening_quantity",
                sort_order="desc",
                limit=tracks_limit
            )
            tracks_items = tracks_result.get("items", []) if isinstance(tracks_result, dict) else []
            tracks_type = "popular"
        except Exception:
            pass

        try:
            albums_result = await music_client.search_albums(
                sort_by="listening_quantity",
                sort_order="desc",
                limit=albums_limit
            )
            albums_items = albums_result.get("items", []) if isinstance(albums_result, dict) else []
            albums_type = "popular"
        except Exception:
            pass

    # Собираем все author_id
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
            user_info = await users_client.get_user_info(str(author_id))
            authors_data[author_id] = {
                "id": str(author_id),
                "nickname": user_info.get("user_nickname", "Пользователь"),
                "avatar_url": user_info.get("user_avatar", "/static/default-avatar.png")
            }
        except Exception:
            authors_data[author_id] = {
                "id": str(author_id),
                "nickname": "Пользователь",
                "avatar_url": "/static/default-avatar.png"
            }

    # Форматируем треки
    formatted_tracks = []
    for item in tracks_items:
        author_id = item.get("author_id")
        author = authors_data.get(author_id, {
            "id": str(author_id) if author_id else "",
            "nickname": "Пользователь",
            "avatar_url": "/static/default-avatar.png"
        })

        published_at = item.get("published_at")
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

        formatted_tracks.append({
            "track_id": item.get("track_id"),
            "title": item.get("title"),
            "album_id": item.get("album_id"),
            "cover_url": item.get("cover_url"),
            "author": author,
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
        author = authors_data.get(author_id, {
            "id": str(author_id) if author_id else "",
            "nickname": "Пользователь",
            "avatar_url": "/static/default-avatar.png"
        })

        published_at = item.get("published_at")
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

        # Получаем треки альбома для плеера
        album_tracks = []
        try:
            tracks_data = await music_client.get_album_tracks(item.get("id"))
            for t in tracks_data.get("items", []):
                album_tracks.append({
                    "track_id": t.get("track_id"),
                    "title": t.get("title"),
                    "track_url": t.get("track_url"),
                    "cover_url": t.get("cover_url") or item.get("cover_url"),
                    "author_id": str(author_id) if author_id else "",
                    "author_nickname": author.get("nickname"),
                    "duration": t.get("duration"),
                    "bpm": t.get("bpm")
                })
        except Exception:
            pass

        formatted_albums.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "author": author,
            "cover_url": item.get("cover_url"),
            "type_id": item.get("type_id"),
            "subtype": item.get("type"),
            "tracks": album_tracks,
            "tracks_count": len(album_tracks) or item.get("tracks_count", 0),
            "genres": item.get("genres", []),
            "liked_quantity": item.get("liked_quantity", 0),
            "follower_quantity": item.get("follower_quantity", 0),
            "listening_quantity": item.get("listening_quantity", 0),
            "comments_quantity": item.get("comments_quantity", 0),
            "published_at_formatted": published_at_formatted
        })

    return {
        "tracks": {
            "items": formatted_tracks,
            "total": len(formatted_tracks),
            "type": tracks_type
        },
        "albums": {
            "items": formatted_albums,
            "total": len(formatted_albums),
            "type": albums_type
        }
    }


@router.get("/tracks/{track_id}/similar")
async def get_similar_tracks(
        track_id: str,
        limit: int = Query(10, ge=1, le=50),
        music_client: MusicClient = Depends(get_music_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение треков, похожих на указанный.
    Возвращает: название, обложку, автора (ник + id), track_id, track_url.
    """

    # 1. Получаем похожие треки из music_catalog_service
    try:
        result = await music_client.get_similar_tracks(track_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get similar tracks: {str(e)}")

    items = result.get("items", [])

    if not items:
        return {
            "items": [],
            "total": 0,
            "based_on": track_id
        }

    # 2. Собираем уникальные author_id
    author_ids = list(set([item.get("author_id") for item in items if item.get("author_id")]))

    # 3. Получаем данные авторов
    authors_data = {}
    for author_id in author_ids:
        try:
            user_info = await users_client.get_user_info(author_id)
            authors_data[author_id] = {
                "id": author_id,
                "nickname": user_info.get("user_nickname", "Пользователь")
            }
        except Exception:
            authors_data[author_id] = {
                "id": author_id,
                "nickname": "Пользователь"
            }

    # 4. Формируем ответ
    formatted_items = []
    for item in items:
        author_id = item.get("author_id")
        author = authors_data.get(author_id, {})

        formatted_items.append({
            "track_id": item.get("track_id"),
            "title": item.get("title"),
            "cover_url": item.get("cover_url"),
            "track_url": item.get("track_url"),
            "bpm": item.get("bpm"),
            "genres": item.get("genres", []),
            "author": {
                "id": author.get("id"),
                "nickname": author.get("nickname")
            }
        })

    return {
        "items": formatted_items,
        "total": len(formatted_items),
        "based_on": track_id
    }


# ========== ПОХОЖИЕ АЛЬБОМЫ ==========

@router.get("/albums/{album_id}/similar")
async def get_similar_albums(
        album_id: str,
        limit: int = Query(10, ge=1, le=50),
        music_client: MusicClient = Depends(get_music_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение альбомов, похожих на указанный.
    Возвращает: название, обложку, автора (ник + id), album_id.
    """

    # 1. Получаем похожие альбомы из music_catalog_service
    try:
        result = await music_client.get_similar_albums(album_id, limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get similar albums: {str(e)}")

    items = result.get("items", [])

    if not items:
        return {
            "items": [],
            "total": 0,
            "based_on": album_id
        }

    # 2. Собираем уникальные author_id
    author_ids = list(set([item.get("author_id") for item in items if item.get("author_id")]))

    # 3. Получаем данные авторов
    authors_data = {}
    for author_id in author_ids:
        try:
            user_info = await users_client.get_user_info(author_id)
            authors_data[author_id] = {
                "id": author_id,
                "nickname": user_info.get("user_nickname", "Пользователь")
            }
        except Exception:
            authors_data[author_id] = {
                "id": author_id,
                "nickname": "Пользователь"
            }

    # 4. Формируем ответ
    formatted_items = []
    for item in items:
        author_id = item.get("author_id")
        author = authors_data.get(author_id, {})

        formatted_items.append({
            "album_id": item.get("id"),
            "title": item.get("title"),
            "cover_url": item.get("cover_url"),
            "author": {
                "id": author.get("id"),
                "nickname": author.get("nickname")
            }
        })

    return {
        "items": formatted_items,
        "total": len(formatted_items),
        "based_on": album_id
    }


@router.get("/new-releases")
async def get_new_releases(
        request: Request,
        limit: int = Query(20, ge=1, le=100),
        music_client: MusicClient = Depends(get_music_client),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение новинок (альбомы и треки) для главной страницы.
    Использует поиск с сортировкой по дате публикации и рандомизацией.
    """
    import random

    try:
        # Получаем последние альбомы (сортировка по дате публикации)
        albums_result = await music_client.search_albums(
            sort_by="published_at",
            sort_order="desc",
            limit=limit * 2  # Берем больше для рандомизации
        )

        # Получаем последние треки (сортировка по дате публикации)
        tracks_result = await music_client.search_tracks(
            sort_by="published_at",
            sort_order="desc",
            limit=limit * 2  # Берем больше для рандомизации
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get new releases: {str(e)}")

    albums_items = albums_result.get("items", []) if isinstance(albums_result, dict) else []
    tracks_items = tracks_result.get("items", []) if isinstance(tracks_result, dict) else []

    # Перемешиваем для разнообразия
    random.shuffle(albums_items)
    random.shuffle(tracks_items)

    # Собираем все author_id
    all_author_ids = []
    for item in albums_items + tracks_items:
        if item.get("author_id"):
            all_author_ids.append(item.get("author_id"))

    # Получаем данные авторов
    authors_data = {}
    for author_id in set(all_author_ids):
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

    unified_items = []

    # Форматируем альбомы (берем половину от лимита)
    albums_to_take = min(len(albums_items), limit // 2 + limit % 2)
    for album in albums_items[:albums_to_take]:
        author_id = album.get("author_id")
        author = authors_data.get(author_id, {
            "id": author_id or "",
            "nickname": "Пользователь",
            "avatar_url": "/static/default-avatar.png"
        })

        # Получаем треки альбома для плеера
        album_tracks = []
        try:
            tracks_data = await music_client.get_album_tracks(album.get("id"))
            for t in tracks_data.get("items", []):
                album_tracks.append({
                    "track_id": t.get("track_id"),
                    "title": t.get("title"),
                    "track_url": t.get("track_url"),
                    "cover_url": t.get("cover_url") or album.get("cover_url"),
                    "author_id": author_id or "",
                    "author_nickname": author.get("nickname"),
                    "duration": t.get("duration"),
                    "bpm": t.get("bpm")
                })
        except Exception:
            pass

        # Форматируем дату
        published_at_formatted = None
        published_at_raw = None
        if album.get("published_at"):
            try:
                if isinstance(album.get("published_at"), str):
                    dt = datetime.fromisoformat(album.get("published_at").replace("+00:00", ""))
                else:
                    dt = album.get("published_at")
                published_at_formatted = format_date_ru(dt)
                published_at_raw = dt.isoformat()
            except Exception:
                pass

        unified_items.append({
            "id": album.get("id"),
            "title": album.get("title"),
            "cover_url": album.get("cover_url"),
            "author": author,
            "type": "album",
            "subtype": album.get("type"),  # Album, EP, Single
            "tracks": album_tracks,
            "tracks_count": len(album_tracks),
            "genres": album.get("genres", []),
            "liked_quantity": album.get("liked_quantity", 0),
            "published_at_formatted": published_at_formatted,
            "published_at_raw": published_at_raw
        })

    # Форматируем треки (берем оставшуюся часть лимита)
    tracks_to_take = min(len(tracks_items), limit - len(unified_items))
    for track in tracks_items[:tracks_to_take]:
        author_id = track.get("author_id")
        author = authors_data.get(author_id, {
            "id": author_id or "",
            "nickname": "Пользователь",
            "avatar_url": "/static/default-avatar.png"
        })

        # Форматируем дату
        published_at_formatted = None
        published_at_raw = None
        if track.get("published_at"):
            try:
                if isinstance(track.get("published_at"), str):
                    dt = datetime.fromisoformat(track.get("published_at").replace("+00:00", ""))
                else:
                    dt = track.get("published_at")
                published_at_formatted = format_date_ru(dt)
                published_at_raw = dt.isoformat()
            except Exception:
                pass

        unified_items.append({
            "id": track.get("track_id"),
            "title": track.get("title"),
            "cover_url": track.get("cover_url"),
            "author": author,
            "type": "track",
            "track_url": track.get("track_url"),
            "album_id": track.get("album_id"),
            "bpm": track.get("bpm"),
            "genres": track.get("genres", []),
            "liked_quantity": track.get("liked_quantity", 0),
            "published_at_formatted": published_at_formatted,
            "published_at_raw": published_at_raw
        })

    # Если нужно больше треков, добираем из оставшихся
    if len(unified_items) < limit and len(tracks_items) > tracks_to_take:
        additional_tracks = tracks_items[tracks_to_take:limit - len(unified_items)]
        for track in additional_tracks:
            author_id = track.get("author_id")
            author = authors_data.get(author_id, {
                "id": author_id or "",
                "nickname": "Пользователь",
                "avatar_url": "/static/default-avatar.png"
            })

            published_at_formatted = None
            published_at_raw = None
            if track.get("published_at"):
                try:
                    if isinstance(track.get("published_at"), str):
                        dt = datetime.fromisoformat(track.get("published_at").replace("Z", "+00:00"))
                    else:
                        dt = track.get("published_at")
                    published_at_formatted = format_date_ru(dt)
                    published_at_raw = dt.isoformat()
                except Exception:
                    pass

            unified_items.append({
                "id": track.get("track_id"),
                "title": track.get("title"),
                "cover_url": track.get("cover_url"),
                "author": author,
                "type": "track",
                "track_url": track.get("track_url"),
                "album_id": track.get("album_id"),
                "bpm": track.get("bpm"),
                "genres": track.get("genres", []),
                "liked_quantity": track.get("liked_quantity", 0),
                "published_at_formatted": published_at_formatted,
                "published_at_raw": published_at_raw
            })

    # Еще раз перемешиваем итоговый список для разнообразия
    random.shuffle(unified_items)

    return {
        "items": unified_items,
        "total": len(unified_items),
        "type": "global",
        "section": "new_releases"
    }
