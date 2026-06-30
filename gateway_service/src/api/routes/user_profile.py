from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, Request, Query
from typing import Optional, List
from datetime import datetime
import random
import re

from src.api.dependencies import (
    get_current_user,
    get_optional_current_user,
    CurrentUser,
    get_users_client,
    get_music_client,
    get_media_client,
    get_social_client
)
from src.api.helpers.user_top_music import get_top_tracks, get_recent_albums
from src.api.helpers.format_date import format_date_ru

from src.clients.users_service import UsersClient
from src.clients.music_service import MusicClient
from src.clients.social_feed_service import SocialClient
from src.clients.media_service import MediaClient


router = APIRouter(prefix="/user", tags=["User Page"])


@router.get("/me")
async def get_my_profile(
        current_user: CurrentUser = Depends(get_current_user),
        users_client: UsersClient = Depends(get_users_client),
        music_client: MusicClient = Depends(get_music_client),
        social_client: SocialClient = Depends(get_social_client)
):
    """
    Получение полной информации о текущем пользователе для страницы профиля.
    """
    user_info = await users_client.get_user_info(str(current_user.id))
    top_tracks = await get_top_tracks(str(current_user.id), music_client, limit=5)
    recent_albums = await get_recent_albums(str(current_user.id), music_client, limit=5)

    posts_result = await social_client.list_posts(
        author_id=str(current_user.id),
        skip=0,
        limit=10,
        sort_by="created_at",
        sort_order="desc"
    )

    return {
        "user": {
            "id": str(current_user.id),
            "username": user_info.get("user_name"),
            "nickname": user_info.get("user_nickname", current_user.nickname),
            "avatar_url": user_info.get("user_avatar", current_user.avatar_url),
            "bio": user_info.get("user_bio", ""),
            "follower_quantity": user_info.get("user_follower_quantity", 0),
            "following_quantity": user_info.get("user_following_quantity", 0),
            "friends_quantity": user_info.get("user_friends_quantity", 0),
            "listening_quantity": user_info.get("user_listening_quantity", 0),
            "month_listening_quantity": user_info.get("user_month_listening_quantity", 0)
        },
        "top_tracks": top_tracks,
        "recent_albums": recent_albums,
        "recent_posts": {
            "items": posts_result.get("items", [])[:5],
            "total": posts_result.get("total", 0)
        }
    }


# ========== ПРОФИЛЬ ДРУГОГО ПОЛЬЗОВАТЕЛЯ ==========

@router.get("/{user_id}")
async def get_user_profile(
        user_id: str,
        request: Request,
        users_client: UsersClient = Depends(get_users_client),
        music_client: MusicClient = Depends(get_music_client),
        social_client: SocialClient = Depends(get_social_client)
):
    """
    Получение полной информации о пользователе.
    ПУБЛИЧНЫЙ эндпоинт - не требует авторизации.
    """
    try:
        user_info = await users_client.get_user_info(user_id)
    except Exception as e:
        print(f"❌ Ошибка получения информации о пользователе {user_id}: {e}")
        raise HTTPException(status_code=404, detail="User not found")

    if not user_info:
        raise HTTPException(status_code=404, detail="User not found")

    # ===== ПЫТАЕМСЯ ПОЛУЧИТЬ ТОКЕН, НО НЕ ТРЕБУЕМ =====
    is_following = False
    auth_header = request.headers.get("Authorization", "")
    


    if auth_header and auth_header.startswith("Bearer "):
        from jose import JWTError, jwt
        from config import settings
        
        token = auth_header.replace("Bearer ", "")
        try:
            # Пытаемся получить текущего пользователя
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": False}
            )
            current_user_id = payload.get("user_id") or payload.get("sub")
            
            if current_user_id:
                # Проверяем подписку
                try:
                    following = await users_client.get_following(
                        user_id=current_user_id,
                        limit=100
                    )
                    if isinstance(following, dict):
                        following_ids = [u.get("following_id") for u in following.get("followings", []) if u.get("following_id")]
                        is_following = user_id in following_ids
                    elif isinstance(following, list):
                        following_ids = [u.get("following_idid") for u in following if u.get("following_id")]
                        is_following = user_id in following_ids
                except Exception as e:
                    print(f"⚠️ Ошибка проверки подписки: {e}")
                    
        except JWTError as e:
            print(f"⚠️ Ошибка JWT: {e}")
        except Exception as e:
            print(f"⚠️ Ошибка проверки токена: {e}")

    # Получаем топ треки и альбомы
    top_tracks = await get_top_tracks(user_id, music_client, users_client, limit=5)
    recent_albums = await get_recent_albums(user_id, music_client, users_client, limit=5)

    # Получаем посты
    try:
        posts_result = await social_client.list_posts(
            author_id=user_id,
            skip=0,
            limit=10,
            sort_by="created_at",
            sort_order="desc"
        )
        posts_items = posts_result.get("items", [])
        posts_total = posts_result.get("total", 0)
    except Exception as e:
        print(f"⚠️ Ошибка получения постов: {e}")
        posts_items = []
        posts_total = 0

    # Форматируем посты
    formatted_posts = []
    for post in posts_items:
        created_at = post.get("created_at")
        if isinstance(created_at, str):
            try:
                created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
            except:
                created_at = datetime.now()
        elif not created_at:
            created_at = datetime.now()
        
        # Получаем данные автора поста
        post_author_id = post.get("author_id")
        post_author = {}
        if post_author_id:
            try:
                post_user_info = await users_client.get_user_info(post_author_id)
                post_author = {
                    "id": post_author_id,
                    "nickname": post_user_info.get("user_nickname", "Пользователь"),
                    "avatar_url": post_user_info.get("user_avatar", "/static/default-avatar.png")
                }
            except Exception:
                post_author = {
                    "id": post_author_id,
                    "nickname": "Пользователь",
                    "avatar_url": "/static/default-avatar.png"
                }
        
        formatted_posts.append({
            "id": post.get("id"),
            "text": post.get("text", ""),
            "media": post.get("media", []),
            "created_at_formatted": format_date_ru(created_at),
            "created_at_raw": created_at.isoformat() if created_at else None,
            "likes_quantity": post.get("likes_quantity", 0),
            "comments_quantity": post.get("comments_quantity", 0),
            "author": post_author
        })

    return {
        "user": {
            "id": user_id,
            "username": user_info.get("user_name"),
            "nickname": user_info.get("user_nickname", "User"),
            "avatar_url": user_info.get("user_avatar", "/static/default-avatar.png"),
            "bio": user_info.get("user_bio", ""),
            "follower_quantity": user_info.get("user_follower_quantity", 0),
            "following_quantity": user_info.get("user_following_quantity", 0),
            "friends_quantity": user_info.get("user_friends_quantity", 0),
            "listening_quantity": user_info.get("user_listening_quantity", 0),
            "month_listening_quantity": user_info.get("user_month_listening_quantity", 0),
            "is_following": is_following
        },
        "top_tracks": top_tracks,
        "recent_albums": recent_albums,
        "recent_posts": {
            "items": formatted_posts[:5],
            "total": posts_total
        }
    }


# ========== ВСЕ ТРЕКИ ПОЛЬЗОВАТЕЛЯ ==========

@router.get("/{user_id}/tracks")
async def get_user_tracks(
        user_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        sort_by: str = Query("listening_quantity", pattern="^(listening_quantity|liked_quantity|created_at|title)$"),
        sort_order: str = Query("desc", pattern="^(asc|desc)$"),
        users_client: UsersClient = Depends(get_users_client),
        music_client: MusicClient = Depends(get_music_client)
):
    """Все треки пользователя с пагинацией, сортировкой и данными автора."""
    result = await music_client.search_tracks(
        author_id=user_id,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )

    items = result.get("items", [])
    total = result.get("total", 0)

    # Получаем данные авторов
    author_ids = list(set([item.get("author_id") for item in items if item.get("author_id")]))
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

    # Форматируем треки
    formatted_items = []
    for item in items:
        author_id = item.get("author_id")
        author = authors_data.get(author_id, {
            "id": author_id,
            "nickname": "Пользователь",
            "avatar_url": "/static/default-avatar.png"
        })

        # Форматируем дату
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
            "author": author,
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

    return {
        "items": formatted_items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


# ========== ВСЕ АЛЬБОМЫ ПОЛЬЗОВАТЕЛЯ ==========

@router.get("/{user_id}/albums")
async def get_user_albums(
        user_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        sort_by: str = Query("published_at", pattern="^(published_at|created_at|listening_quantity|title)$"),
        sort_order: str = Query("desc", pattern="^(asc|desc)$"),
        users_client: UsersClient = Depends(get_users_client),
        music_client: MusicClient = Depends(get_music_client)
):
    """Все альбомы пользователя с пагинацией, сортировкой и данными автора."""
    result = await music_client.search_albums(
        author_id=user_id,
        sort_by=sort_by,
        sort_order=sort_order,
        skip=skip,
        limit=limit
    )

    items = result.get("items", [])
    total = result.get("total", 0)

    # Получаем данные авторов
    author_ids = list(set([item.get("author_id") for item in items if item.get("author_id")]))
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

    # Форматируем альбомы
    formatted_items = []
    for item in items:
        author_id = item.get("author_id")
        author = authors_data.get(author_id, {
            "id": author_id,
            "nickname": "Пользователь",
            "avatar_url": "/static/default-avatar.png"
        })

        # Форматируем дату
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

        # Получаем треки альбома
        album_tracks = []
        try:
            tracks_result = await music_client.get_album_tracks(item.get("id"))
            tracks = tracks_result.get("items", [])
            
            # Получаем данные авторов для треков (если отличаются)
            track_author_ids = list(set([t.get("author_id") for t in tracks if t.get("author_id")]))
            track_authors_data = {}
            for track_author_id in track_author_ids:
                if track_author_id not in authors_data:
                    try:
                        user_info = await users_client.get_user_info(track_author_id)
                        track_authors_data[track_author_id] = {
                            "id": track_author_id,
                            "nickname": user_info.get("user_nickname", "Пользователь"),
                            "avatar_url": user_info.get("user_avatar", "/static/default-avatar.png")
                        }
                    except Exception:
                        track_authors_data[track_author_id] = {
                            "id": track_author_id,
                            "nickname": "Пользователь",
                            "avatar_url": "/static/default-avatar.png"
                        }
            
            for track in tracks:
                track_author_id = track.get("author_id")
                track_author = track_authors_data.get(track_author_id) or authors_data.get(track_author_id, {
                    "id": track_author_id,
                    "nickname": "Пользователь",
                    "avatar_url": "/static/default-avatar.png"
                })
                
                album_tracks.append({
                    "track_id": track.get("track_id"),
                    "title": track.get("title"),
                    "track_url": track.get("track_url"),
                    "bpm": track.get("bpm"),
                    "genres": track.get("genres", []),
                    "feats": track.get("feats", []),
                    "author": track_author,
                    "listening_quantity": track.get("listening_quantity", 0),
                    "liked_quantity": track.get("liked_quantity", 0),
                    "comments_quantity": track.get("comments_quantity", 0),
                })
        except Exception as e:
            print(f"⚠️ Ошибка получения треков для альбома {item.get('id')}: {e}")

        formatted_items.append({
            "id": item.get("id"),
            "title": item.get("title"),
            "author": author,
            "cover_url": item.get("cover_url"),
            "type": item.get("type"),
            "genres": item.get("genres", []),
            "liked_quantity": item.get("liked_quantity", 0),
            "follower_quantity": item.get("follower_quantity", 0),
            "listening_quantity": item.get("listening_quantity", 0),
            "comments_quantity": item.get("comments_quantity", 0),
            "tracks_count": len(album_tracks),
            "tracks": album_tracks,
            "published_at_formatted": published_at_formatted,
            "published_at_raw": published_at_raw
        })

    return {
        "items": formatted_items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


# ========== ВСЕ ПОСТЫ ПОЛЬЗОВАТЕЛЯ ==========

@router.get("/{user_id}/posts")
async def get_user_posts(
        user_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        sort_by: str = Query("created_at", pattern="^(created_at|likes_quantity|comments_quantity)$"),
        sort_order: str = Query("desc", pattern="^(asc|desc)$"),
        social_client: SocialClient = Depends(get_social_client)
):
    """Все посты пользователя с пагинацией и сортировкой."""
    result = await social_client.list_posts(
        author_id=user_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        sort_order=sort_order
    )

    return {
        "items": result.get("items", []),
        "total": result.get("total", 0),
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < result.get("total", 0)
    }


# ========== ПОДПИСЧИКИ ==========

@router.get("/{user_id}/followers")
async def get_user_followers(
        user_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        users_client: UsersClient = Depends(get_users_client)
):
    """Список подписчиков пользователя."""
    result = await users_client.get_followers(user_id, skip=skip, limit=limit)
    items = result.get("followers", []) if isinstance(result, dict) else result
    total = result.get("total", len(items)) if isinstance(result, dict) else len(items)

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


# ========== ПОДПИСКИ ==========

@router.get("/{user_id}/following")
async def get_user_following(
        user_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        users_client: UsersClient = Depends(get_users_client)
):
    """Список подписок пользователя."""
    result = await users_client.get_following(user_id, skip=skip, limit=limit)
    items = result.get("followings", []) if isinstance(result, dict) else result
    total = result.get("total", len(items)) if isinstance(result, dict) else len(items)

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


# ========== ДРУЗЬЯ ==========

@router.get("/{user_id}/friends")
async def get_user_friends(
        user_id: str,
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        users_client: UsersClient = Depends(get_users_client)
):
    """Список друзей пользователя."""
    result = await users_client.get_friends(user_id, skip=skip, limit=limit)
    items = result.get("friends", []) if isinstance(result, dict) else result
    total = result.get("total", len(items)) if isinstance(result, dict) else len(items)

    return {
        "items": items,
        "total": total,
        "skip": skip,
        "limit": limit,
        "has_more": (skip + limit) < total
    }


# ========== ПОДПИСАТЬСЯ / ОТПИСАТЬСЯ ==========

@router.post("/{user_id}/follow")
async def follow_user(
        user_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        users_client: UsersClient = Depends(get_users_client)
):
    """Подписаться на пользователя."""
    if user_id == str(current_user.id):
        raise HTTPException(status_code=400, detail="Cannot follow yourself")

    try:
        result = await users_client.follow(user_id=user_id, token=current_user.token)
        return {"success": True, "message": "Subscribed successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Follow error: {e}")
        # Даже при ошибке возвращаем успех, так как подписка могла уже существовать
        return {"success": True, "message": "Subscribed successfully"}


@router.post("/{user_id}/unfollow")
async def unfollow_user(
        user_id: str,
        current_user: CurrentUser = Depends(get_current_user),
        users_client: UsersClient = Depends(get_users_client)
):
    """Отписаться от пользователя."""
    try:
        result = await users_client.unfollow(user_id=user_id, token=current_user.token)
        return {"success": True, "message": "Unsubscribed successfully"}
    except HTTPException as e:
        raise e
    except Exception as e:
        print(f"Unfollow error: {e}")
        # Даже при ошибке возвращаем успех
        return {"success": True, "message": "Unsubscribed successfully"}



@router.get("/settings/me")
async def get_my_edit_info(
        current_user: CurrentUser = Depends(get_current_user),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Получение информации о пользователе для страницы редактирования.
    """
    user_info = await users_client.get_user_info(str(current_user.id))

    return {
        "id": str(current_user.id),
        "username": user_info.get("user_name", ""),
        "nickname": user_info.get("user_nickname", current_user.nickname),
        "avatar_url": user_info.get("user_avatar", current_user.avatar_url),
        "bio": user_info.get("user_bio", "")
    }


@router.put("/settings/avatar")
async def upload_and_update_avatar(
        file: UploadFile = File(..., media_type="image/jpeg"),
        current_user: CurrentUser = Depends(get_current_user),
        users_client: UsersClient = Depends(get_users_client),
        media_client: MediaClient = Depends(get_media_client)
):
    """
    Загрузить новый аватар через media_service и обновить профиль.
    """

    # 1. Удаляем старый аватар
    user_info = await users_client.get_me(token=current_user.token)
    old_avatar_url = user_info.get("avatar_url", "")
    if old_avatar_url:
        try:
            await media_client.delete_avatar(current_user.token)
        except Exception as e:
            print(f"Warning: Failed to delete old avatar: {e}")

    # 2. Загружаем новый аватар в S3
    result = await media_client.upload_avatar(file=file, token=current_user.token)

    # 3. Извлекаем URL большого аватара (large.avif — третий элемент, индекс 2)
    avatar_url = ""
    if isinstance(result, list) and len(result) >= 3:
        avatar_url = result[2].get("url", "")
    elif isinstance(result, dict) and result.get("media") and len(result["media"]) >= 3:
        avatar_url = result["media"][2].get("url", "")

    if not avatar_url:
        raise HTTPException(status_code=500, detail=f"Failed to get avatar URL. Response: {result}")

    # 4. Обновляем профиль
    await users_client.update_avatar(avatar_url=avatar_url, token=current_user.token)

    return {
        "message": "Avatar updated successfully",
        "avatar_url": avatar_url
    }


# ========== ОБНОВЛЕНИЕ БИОГРАФИИ ==========

@router.put("/settings/bio")
async def update_my_bio(
        bio: str,
        current_user: CurrentUser = Depends(get_current_user),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Обновить биографию пользователя.
    """
    if len(bio) > 500:
        raise HTTPException(status_code=400, detail="Bio too long (max 500 characters)")

    result = await users_client.update_bio(bio, current_user.token)
    return result


# ========== ОБНОВЛЕНИЕ НИКНЕЙМА ==========

@router.put("/settings/nickname")
async def update_my_nickname(
        nickname: str,
        current_user: CurrentUser = Depends(get_current_user),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Обновить никнейм пользователя.
    """
    if len(nickname) < 2 or len(nickname) > 30:
        raise HTTPException(status_code=400, detail="Nickname must be 2-30 characters")

    result = await users_client.rename_nickname(nickname, current_user.token)
    return result


# ========== ОБНОВЛЕНИЕ USERNAME ==========

@router.put("/settings/username")
async def update_my_username(
        username: str,
        current_user: CurrentUser = Depends(get_current_user),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Обновить имя пользователя (username).
    """
    if not re.match(r"^[a-zA-Z0-9_]{3,30}$", username):
        raise HTTPException(status_code=400, detail="Username must be 3-30 characters (letters, numbers, underscore)")

    result = await users_client.rename_username(username, current_user.token)
    return result


# ========== СМЕНА ПАРОЛЯ ==========

@router.put("/settings/password")
async def change_my_password(
        password: str,
        new_password: str,
        current_user: CurrentUser = Depends(get_current_user),
        users_client: UsersClient = Depends(get_users_client)
):
    """
    Сменить пароль пользователя.
    """
    if len(new_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    result = await users_client.change_password(password, new_password, current_user.token)
    return result
