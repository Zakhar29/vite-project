from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, desc, case
from typing import Optional, List
import uuid

from src.db.postgres_engine import get_db
from src.models.albums_models import (
    Albums, AlbumStatuses, AlbumTypes, AlbumTracks, AlbumFollows, LikedAlbums
)

from src.models.tracks_models import Tracks, TrackGenres, Genres, TrackFeats
from config import settings


async def get_public_status_id(db: AsyncSession) -> int:
    """Получение ID статуса 'public'"""
    result = await db.execute(select(AlbumStatuses.id).where(AlbumStatuses.title == "public"))
    status_id = result.scalar_one_or_none()
    return status_id or 2


async def get_album_genres(db: AsyncSession, album_id: uuid.UUID) -> List[str]:
    """Получение всех жанров треков в альбоме"""

    genres_result = await db.execute(
        select(Genres.title)
        .distinct()
        .join(TrackGenres, TrackGenres.genre_id == Genres.id)
        .join(Tracks, Tracks.id == TrackGenres.track_id)
        .join(AlbumTracks, AlbumTracks.track_id == Tracks.id)
        .where(AlbumTracks.album_id == album_id)
    )
    return [g for g in genres_result.scalars().all()]


async def enrich_album_response(album, db: AsyncSession) -> dict:
    """Обогащает ответ альбома жанрами и количеством треков"""

    # Количество треков
    tracks_count_result = await db.execute(
        select(func.count()).select_from(AlbumTracks).where(AlbumTracks.album_id == album.id)
    )
    tracks_count = tracks_count_result.scalar_one()

    # Жанры альбома
    genres = await get_album_genres(db, album.id)

    # Краткая информация о треках (первые 3)
    tracks_preview_result = await db.execute(
        select(Tracks.id, Tracks.title)
        .join(AlbumTracks, AlbumTracks.track_id == Tracks.id)
        .where(AlbumTracks.album_id == album.id)
        .order_by(AlbumTracks.number)
        .limit(3)
    )
    tracks_preview = [{"id": str(t.id), "title": t.title} for t in tracks_preview_result.all()]

    # Фиты альбома (уникальные фиты из треков)
    feats_result = await db.execute(
        select(TrackFeats.feat_user_id)
        .distinct()
        .join(Tracks, Tracks.id == TrackFeats.track_id)
        .join(AlbumTracks, AlbumTracks.track_id == Tracks.id)
        .where(AlbumTracks.album_id == album.id)
    )
    feats = [str(f) for f in feats_result.scalars().all()]

    # Тип альбома
    album_type_title = None
    if album.type:
        type_result = await db.execute(
            select(AlbumTypes.title).where(AlbumTypes.id == album.type)
        )
        album_type_title = type_result.scalar_one_or_none()

    return {
        "id": str(album.id),
        "title": album.title,
        "author_id": str(album.author_id),
        "cover_url": album.cover_url,
        "type_id": album.type,
        "type": album_type_title,
        "status": album.status,
        "genres": genres,
        "feats": feats,
        "tracks_count": tracks_count,
        "tracks_preview": tracks_preview,
        "liked_quantity": album.liked_quantity,
        "follower_quantity": album.follower_quantity,
        "listening_quantity": album.listening_quantity,
        "comments_quantity": album.comments_quantity,
        "created_at": album.created_at.isoformat() if album.created_at else None,
        "updated_at": album.updated_at.isoformat() if album.updated_at else None,
        "published_at": album.published_at.isoformat() if album.published_at else None
    }


async def check_user_activity(user_id: uuid.UUID, db: AsyncSession) -> bool:
    """
    Проверяет, есть ли у пользователя активность с альбомами:
    - Лайки альбомов
    - Подписки на альбомы
    """
    # Проверяем лайки альбомов
    likes_result = await db.execute(
        select(LikedAlbums).where(LikedAlbums.user_id == user_id).limit(1)
    )
    if likes_result.first():
        return True

    # Проверяем подписки на альбомы
    follows_result = await db.execute(
        select(AlbumFollows).where(AlbumFollows.user_id == user_id).limit(1)
    )
    if follows_result.first():
        return True

    return False


async def get_popular_albums_genres(db: AsyncSession, limit: int = 5) -> List[int]:
    """Получение самых популярных жанров среди альбомов"""

    popular_genres_stmt = (
        select(TrackGenres.genre_id, func.count().label("count"))
        .join(Tracks, Tracks.id == TrackGenres.track_id)
        .join(AlbumTracks, AlbumTracks.track_id == Tracks.id)
        .join(Albums, Albums.id == AlbumTracks.album_id)
        .where(Albums.status == await get_public_status_id(db))
        .group_by(TrackGenres.genre_id)
        .order_by(desc("count"))
        .limit(limit)
    )

    result = await db.execute(popular_genres_stmt)
    return [row[0] for row in result.all()]


async def check_album_activity(user_id: uuid.UUID, db: AsyncSession) -> bool:
    """Проверяет активность пользователя с альбомами"""

    # Проверяем лайки альбомов
    likes_result = await db.execute(
        select(LikedAlbums).where(LikedAlbums.user_id == user_id).limit(1)
    )
    if likes_result.first():
        return True

    # Проверяем подписки на альбомы
    follows_result = await db.execute(
        select(AlbumFollows).where(AlbumFollows.user_id == user_id).limit(1)
    )
    if follows_result.first():
        return True

    return False


async def get_user_album_genres(db: AsyncSession, user_id: uuid.UUID) -> List[int]:
    """Получение жанров из альбомов, с которыми взаимодействовал пользователь"""

    genre_stmt = (
        select(TrackGenres.genre_id)
        .distinct()
        .join(Tracks, Tracks.id == TrackGenres.track_id)
        .join(AlbumTracks, AlbumTracks.track_id == Tracks.id)
        .join(Albums, Albums.id == AlbumTracks.album_id)
        .where(
            or_(
                Albums.id.in_(select(LikedAlbums.album_id).where(LikedAlbums.user_id == user_id)),
                Albums.id.in_(select(AlbumFollows.album_id).where(AlbumFollows.user_id == user_id))
            )
        )
        .limit(10)
    )

    genre_result = await db.execute(genre_stmt)
    return [g for g in genre_result.scalars().all()]


async def cold_start_album_recommendations(limit: int, db: AsyncSession) -> List[dict]:
    """Рекомендации альбомов для новых пользователей (без дубликатов)"""

    public_status_id = await get_public_status_id(db)

    popular_limit = int(limit * 0.6)  # 60% популярные
    new_limit = int(limit * 0.3)  # 30% новинки
    random_limit = limit - popular_limit - new_limit  # 10% случайные

    recommendations = []
    seen_ids = set()

    # 1. Популярные альбомы (берём с запасом)
    popular_stmt = (
        select(Albums)
        .where(Albums.status == public_status_id)
        .order_by(desc(Albums.listening_quantity))
        .limit(popular_limit * 2)  # запас на случай дубликатов
    )
    popular_result = await db.execute(popular_stmt)

    for album in popular_result.scalars().all():
        if album.id not in seen_ids:
            recommendations.append(await enrich_album_response(album, db))
            seen_ids.add(album.id)
            if len(recommendations) >= popular_limit:
                break

    # 2. Новые альбомы (исключая уже выбранные)
    if len(recommendations) < limit:
        new_stmt = (
            select(Albums)
            .where(Albums.status == public_status_id)
            .where(Albums.id.not_in(seen_ids))  # исключаем уже выбранные
            .order_by(desc(Albums.published_at))
            .limit(new_limit * 2)
        )
        new_result = await db.execute(new_stmt)

        for album in new_result.scalars().all():
            if album.id not in seen_ids:
                recommendations.append(await enrich_album_response(album, db))
                seen_ids.add(album.id)
                if len(recommendations) >= limit:
                    break

    # 3. Случайные альбомы (исключая уже выбранные)
    if len(recommendations) < limit:
        random_stmt = (
            select(Albums)
            .where(Albums.status == public_status_id)
            .where(Albums.id.not_in(seen_ids))  # исключаем уже выбранные
            .order_by(func.random())
            .limit(random_limit * 3)
        )
        random_result = await db.execute(random_stmt)

        for album in random_result.scalars().all():
            if album.id not in seen_ids:
                recommendations.append(await enrich_album_response(album, db))
                seen_ids.add(album.id)
                if len(recommendations) >= limit:
                    break

    return recommendations[:limit]


async def global_album_recommendations(limit: int, db: AsyncSession) -> dict:
    """Глобальные рекомендации альбомов (популярное + новое + случайное) без дубликатов"""

    public_status_id = await get_public_status_id(db)

    popular_limit = int(limit * settings.RECOMMENDATIONS_POPULAR_FACTOR)
    new_limit = int(limit * settings.RECOMMENDATIONS_NEW_FACTOR)
    random_limit = limit - popular_limit - new_limit

    recommendations = []
    seen_ids = set()

    # 1. Популярные альбомы
    if popular_limit > 0:
        popular_stmt = (
            select(Albums)
            .where(Albums.status == public_status_id)
            .order_by(desc(Albums.listening_quantity))
            .limit(popular_limit * 2)
        )
        popular_result = await db.execute(popular_stmt)

        for album in popular_result.scalars().all():
            if album.id not in seen_ids:
                recommendations.append(await enrich_album_response(album, db))
                seen_ids.add(album.id)
                if len(recommendations) >= limit:
                    return {
                        "items": recommendations[:limit],
                        "total": len(recommendations[:limit]),
                        "type": "global"
                    }

    # 2. Новые альбомы
    if new_limit > 0 and len(recommendations) < limit:
        new_stmt = (
            select(Albums)
            .where(Albums.status == public_status_id)
            .where(Albums.id.not_in(seen_ids))
            .order_by(desc(Albums.published_at))
            .limit(new_limit * 2)
        )
        new_result = await db.execute(new_stmt)

        for album in new_result.scalars().all():
            if album.id not in seen_ids:
                recommendations.append(await enrich_album_response(album, db))
                seen_ids.add(album.id)
                if len(recommendations) >= limit:
                    return {
                        "items": recommendations[:limit],
                        "total": len(recommendations[:limit]),
                        "type": "global"
                    }

    # 3. Случайные альбомы
    if random_limit > 0 and len(recommendations) < limit:
        random_stmt = (
            select(Albums)
            .where(Albums.status == public_status_id)
            .where(Albums.id.not_in(seen_ids))
            .order_by(func.random())
            .limit(random_limit * 3)
        )
        random_result = await db.execute(random_stmt)

        for album in random_result.scalars().all():
            if album.id not in seen_ids:
                recommendations.append(await enrich_album_response(album, db))
                seen_ids.add(album.id)
                if len(recommendations) >= limit:
                    break

    return {
        "items": recommendations[:limit],
        "total": len(recommendations[:limit]),
        "type": "global"
    }


async def personalized_album_recommendations(user_id: uuid.UUID, limit: int, db: AsyncSession) -> dict:
    """Персонализированные рекомендации альбомов на основе истории пользователя"""

    public_status_id = await get_public_status_id(db)

    # Получаем жанры из альбомов пользователя
    preferred_genres = await get_user_album_genres(db, user_id)

    # Получаем авторов из альбомов пользователя
    author_stmt = (
        select(Albums.author_id)
        .where(
            or_(
                Albums.id.in_(select(LikedAlbums.album_id).where(LikedAlbums.user_id == user_id)),
                Albums.id.in_(select(AlbumFollows.album_id).where(AlbumFollows.user_id == user_id))
            )
        )
        .group_by(Albums.author_id)
        .order_by(func.count().desc())
        .limit(10)
    )

    author_result = await db.execute(author_stmt)
    preferred_authors = [a for a in author_result.scalars().all()]

    # Строим рекомендательный запрос
    stmt = select(Albums).where(Albums.status == public_status_id)

    # Исключаем уже взаимодействованные альбомы
    liked_albums = select(LikedAlbums.album_id).where(LikedAlbums.user_id == user_id)
    followed_albums = select(AlbumFollows.album_id).where(AlbumFollows.user_id == user_id)
    stmt = stmt.where(~Albums.id.in_(liked_albums.union(followed_albums)))

    conditions_used = []

    # Приоритет: жанры
    if preferred_genres:
        stmt = stmt.join(AlbumTracks).join(Tracks).join(TrackGenres).where(
            TrackGenres.genre_id.in_(preferred_genres)
        ).distinct()
        conditions_used.append("genres")

    # Затем авторы
    if preferred_authors and not conditions_used:
        stmt = stmt.where(Albums.author_id.in_(preferred_authors))
        conditions_used.append("authors")

    stmt = stmt.order_by(desc(Albums.listening_quantity)).limit(limit)

    result = await db.execute(stmt)
    albums = result.scalars().all()

    # Если рекомендаций мало, добиваем популярными
    if len(albums) < limit:
        popular_limit = limit - len(albums)
        popular_stmt = (
            select(Albums)
            .where(Albums.status == public_status_id)
            .where(~Albums.id.in_(liked_albums.union(followed_albums)))
            .order_by(desc(Albums.listening_quantity))
            .limit(popular_limit)
        )
        popular_result = await db.execute(popular_stmt)
        albums.extend(popular_result.scalars().all())
        conditions_used.append("popular_fallback")

    # Получаем названия жанров
    genre_names = {}
    if preferred_genres:
        genres_names_result = await db.execute(
            select(Genres.id, Genres.title).where(Genres.id.in_(preferred_genres))
        )
        for g in genres_names_result.all():
            genre_names[g.id] = g.title

    response = []
    for album in albums:
        response.append(await enrich_album_response(album, db))

    return {
        "items": response[:limit],
        "total": len(response[:limit]),
        "type": "personalized",
        "preferred_genres": preferred_genres,
        "preferred_genres_names": [{"id": gid, "name": genre_names.get(gid)} for gid in preferred_genres if
                                   genre_names.get(gid)],
        "preferred_authors": [str(a) for a in preferred_authors],
        "conditions_used": conditions_used
    }

