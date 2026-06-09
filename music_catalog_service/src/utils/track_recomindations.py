from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_, func, desc, case
from typing import Optional, List
import uuid

from src.db.postgres_engine import get_db
from src.models.tracks_models import (
    Tracks, TracksStatuses, Genres, TrackGenres, TrackFeats,
    LikedTracks, ListeningTracks, GenreParents
)
from src.models.albums_models import (
    Albums, AlbumTracks
)
from config import settings


async def get_popular_genres(db: AsyncSession, limit: int = 5) -> List[int]:
    """Получение самых популярных жанров среди треков"""

    public_status_id = await get_public_track_status_id(db)

    popular_genres_stmt = (
        select(TrackGenres.genre_id, func.count().label("count"))
        .join(Tracks, Tracks.id == TrackGenres.track_id)
        .where(Tracks.status == public_status_id)
        .group_by(TrackGenres.genre_id)
        .order_by(desc("count"))
        .limit(limit)
    )

    result = await db.execute(popular_genres_stmt)
    return [row[0] for row in result.all()]


# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========
async def get_public_track_status_id(db: AsyncSession) -> int:
    """Получение ID статуса 'public' для треков"""
    result = await db.execute(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    )
    status_id = result.scalar_one_or_none()
    return status_id or 2


async def get_related_genres(
        db: AsyncSession,
        genre_ids: List[int],
        max_depth: int = None
) -> set[int]:
    """
    Рекурсивное получение связанных жанров из GenreParents.
    max_depth: максимальная глубина поиска (из настроек)
    """
    from src.models.tracks_models import GenreParents

    if max_depth is None:
        max_depth = settings.RECOMMENDATIONS_GENRE_DEPTH

    related = set(genre_ids)
    current_level = set(genre_ids)

    for _ in range(max_depth):
        next_level = set()

        for genre_id in current_level:
            # Родители
            parents_result = await db.execute(
                select(GenreParents.parent_id).where(GenreParents.child_id == genre_id)
            )
            for parent in parents_result.scalars().all():
                next_level.add(parent)

            # Дети
            children_result = await db.execute(
                select(GenreParents.child_id).where(GenreParents.parent_id == genre_id)
            )
            for child in children_result.scalars().all():
                next_level.add(child)

        related.update(next_level)
        current_level = next_level

    return related


async def enrich_track_response(
        track, db: AsyncSession
) -> dict:
    """Обогащает ответ трека жанрами и фитами"""
    album_select = await db.execute(
        select(Albums)
        .join(AlbumTracks, AlbumTracks.album_id == Albums.id)
        .where(AlbumTracks.track_id == track.id)
    )
    album = album_select.scalar_one_or_none()

    # Жанры
    genres_result = await db.execute(
        select(Genres)
        .join(TrackGenres)
        .where(TrackGenres.track_id == track.id)
    )
    genres = [g.title for g in genres_result.scalars().all()]

    # Фиты
    feats_result = await db.execute(
        select(TrackFeats).where(TrackFeats.track_id == track.id)
    )
    feats = [str(f.feat_user_id) for f in feats_result.scalars().all()]

    return {
        "track_id": str(track.id),
        "title": track.title,
        "album_id": str(album.id),
        "cover_url": album.cover_url,
        "author_id": str(track.author_id),
        "feats": feats,
        "track_url": track.track_url,
        "bpm": float(track.bpm) if track.bpm else None,
        "genres": genres,
        "liked_quantity": track.liked_quantity,
        "comments_quantity": track.comments_quantity,
        "listening_quantity": track.listening_quantity,
        "published_at": track.published_at.isoformat() if track.published_at else None
    }


# ========== ПОИСК С ФИЛЬТРАЦИЕЙ ==========



# ========== РЕКОМЕНДАЦИИ ==========

async def check_user_activity(user_id: uuid.UUID, db: AsyncSession) -> bool:
    """
    Проверяет, есть ли у пользователя активность с треками:
    - Лайки треков
    - Прослушивания треков
    """
    # Проверяем лайки треков
    likes_result = await db.execute(
        select(LikedTracks).where(LikedTracks.user_id == user_id).limit(1)
    )
    if likes_result.first():
        return True

    # Проверяем прослушивания треков
    listening_result = await db.execute(
        select(ListeningTracks).where(ListeningTracks.user_id == user_id).limit(1)
    )
    if listening_result.first():
        return True

    return False


async def global_track_recommendations(limit: int, db: AsyncSession) -> dict:
    """Глобальные рекомендации треков (популярное, новое, случайное) без дубликатов"""

    popular_limit = int(limit * settings.RECOMMENDATIONS_POPULAR_FACTOR)
    new_limit = int(limit * settings.RECOMMENDATIONS_NEW_FACTOR)
    random_limit = limit - popular_limit - new_limit

    recommendations = []
    seen_ids = set()

    public_status_id = await get_public_track_status_id(db)

    # 1. Популярные треки
    if popular_limit > 0:
        popular_stmt = (
            select(Tracks)
            .where(Tracks.status == public_status_id)
            .order_by(desc(Tracks.listening_quantity))
            .limit(popular_limit * 3)  # Увеличил запас
        )
        popular_result = await db.execute(popular_stmt)

        for track in popular_result.scalars().all():
            if str(track.id) not in seen_ids:
                recommendations.append(await enrich_track_response(track, db))
                seen_ids.add(str(track.id))
                if len(recommendations) >= limit:
                    return {
                        "items": recommendations[:limit],
                        "total": len(recommendations[:limit]),
                        "type": "global"
                    }

    # 2. Новые треки
    if new_limit > 0 and len(recommendations) < limit:
        new_stmt = (
            select(Tracks)
            .where(Tracks.status == public_status_id)
            .where(Tracks.id.not_in([uuid.UUID(uid) for uid in seen_ids] if seen_ids else []))
            .order_by(desc(Tracks.published_at))
            .limit(new_limit * 3)
        )
        new_result = await db.execute(new_stmt)

        for track in new_result.scalars().all():
            if str(track.id) not in seen_ids:
                recommendations.append(await enrich_track_response(track, db))
                seen_ids.add(str(track.id))
                if len(recommendations) >= limit:
                    return {
                        "items": recommendations[:limit],
                        "total": len(recommendations[:limit]),
                        "type": "global"
                    }

    # 3. Случайные треки
    if random_limit > 0 and len(recommendations) < limit:
        random_stmt = (
            select(Tracks)
            .where(Tracks.status == public_status_id)
            .where(Tracks.id.not_in([uuid.UUID(uid) for uid in seen_ids] if seen_ids else []))
            .order_by(func.random())
            .limit(random_limit * 5)
        )
        random_result = await db.execute(random_stmt)

        for track in random_result.scalars().all():
            if str(track.id) not in seen_ids:
                recommendations.append(await enrich_track_response(track, db))
                seen_ids.add(str(track.id))
                if len(recommendations) >= limit:
                    break

    return {
        "items": recommendations[:limit],
        "total": len(recommendations[:limit]),
        "type": "global"
    }


async def cold_start_recommendations(limit: int, db: AsyncSession) -> List[dict]:
    """Рекомендации для новых пользователей (холодный старт) без дубликатов"""

    popular_limit = int(limit * 0.6)  # 60% популярные
    new_limit = int(limit * 0.3)      # 30% новинки
    random_limit = limit - popular_limit - new_limit  # 10% случайные

    recommendations = []
    seen_ids = set()

    public_status_id = await get_public_track_status_id(db)

    # 1. Популярные треки
    if popular_limit > 0:
        popular_stmt = (
            select(Tracks)
            .where(Tracks.status == public_status_id)
            .order_by(desc(Tracks.listening_quantity))
            .limit(popular_limit * 3)
        )
        popular_result = await db.execute(popular_stmt)

        for track in popular_result.scalars().all():
            if str(track.id) not in seen_ids:
                recommendations.append(await enrich_track_response(track, db))
                seen_ids.add(str(track.id))
                if len(recommendations) >= limit:
                    return recommendations[:limit]

    # 2. Новые треки
    if new_limit > 0 and len(recommendations) < limit:
        new_stmt = (
            select(Tracks)
            .where(Tracks.status == public_status_id)
            .where(Tracks.id.not_in([uuid.UUID(uid) for uid in seen_ids] if seen_ids else []))
            .order_by(desc(Tracks.published_at))
            .limit(new_limit * 3)
        )
        new_result = await db.execute(new_stmt)

        for track in new_result.scalars().all():
            if str(track.id) not in seen_ids:
                recommendations.append(await enrich_track_response(track, db))
                seen_ids.add(str(track.id))
                if len(recommendations) >= limit:
                    return recommendations[:limit]

    # 3. Случайные треки
    if random_limit > 0 and len(recommendations) < limit:
        random_stmt = (
            select(Tracks)
            .where(Tracks.status == public_status_id)
            .where(Tracks.id.not_in([uuid.UUID(uid) for uid in seen_ids] if seen_ids else []))
            .order_by(func.random())
            .limit(random_limit * 5)
        )
        random_result = await db.execute(random_stmt)

        for track in random_result.scalars().all():
            if str(track.id) not in seen_ids:
                recommendations.append(await enrich_track_response(track, db))
                seen_ids.add(str(track.id))
                if len(recommendations) >= limit:
                    break

    return recommendations[:limit]


async def personalized_track_recommendations(user_id: uuid.UUID, limit: int, db: AsyncSession) -> dict:
    """Персонализированные рекомендации на основе истории пользователя"""

    # 1. Проверяем активность пользователя
    has_activity = await check_user_activity(user_id, db)

    if not has_activity:
        cold_start_recs = await cold_start_recommendations(limit, db)
        return {
            "items": cold_start_recs,
            "total": len(cold_start_recs),
            "type": "cold_start",
            "message": "New user. Showing popular tracks to get you started."
        }

    # 2. Получаем жанры пользователя
    genre_stmt = (
        select(TrackGenres.genre_id)
        .join(Tracks, Tracks.id == TrackGenres.track_id)
        .where(
            or_(
                Tracks.id.in_(select(LikedTracks.track_id).where(LikedTracks.user_id == user_id)),
                Tracks.id.in_(select(ListeningTracks.track_id).where(ListeningTracks.user_id == user_id))
            )
        )
        .group_by(TrackGenres.genre_id)
        .order_by(func.count().desc())
        .limit(5)
    )

    genre_result = await db.execute(genre_stmt)
    preferred_genres = [g for g in genre_result.scalars().all()]

    if not preferred_genres:
        popular_genres = await get_popular_genres(db)
        expanded_genres = set(popular_genres)
        preferred_genres = popular_genres
    else:
        expanded_genres = await get_related_genres(db, preferred_genres)

    # 3. Получаем авторов пользователя
    author_stmt = (
        select(Tracks.author_id)
        .where(
            or_(
                Tracks.id.in_(select(LikedTracks.track_id).where(LikedTracks.user_id == user_id)),
                Tracks.id.in_(select(ListeningTracks.track_id).where(ListeningTracks.user_id == user_id))
            )
        )
        .group_by(Tracks.author_id)
        .order_by(func.count().desc())
        .limit(10)
    )

    author_result = await db.execute(author_stmt)
    preferred_authors = [a for a in author_result.scalars().all()]

    # 4. Исключаем уже прослушанные/лайкнутые треки
    listened_tracks = select(ListeningTracks.track_id).where(ListeningTracks.user_id == user_id)
    liked_tracks = select(LikedTracks.track_id).where(LikedTracks.user_id == user_id)
    excluded_ids_subq = listened_tracks.union(liked_tracks)

    recommendations = []
    seen_ids = set()

    public_status_id = await get_public_track_status_id(db)

    # 5. Персонализированный запрос
    stmt = (
        select(Tracks)
        .where(Tracks.status == public_status_id)
        .where(~Tracks.id.in_(excluded_ids_subq))
    )

    conditions = []

    if expanded_genres:
        stmt = stmt.join(TrackGenres).where(TrackGenres.genre_id.in_(list(expanded_genres)))
        conditions.append("genres")
    if preferred_authors:
        stmt = stmt.where(Tracks.author_id.in_(preferred_authors))
        conditions.append("authors")

    stmt = stmt.order_by(desc(Tracks.listening_quantity)).limit(limit * 2)

    result = await db.execute(stmt)
    tracks = result.scalars().all()

    # Добавляем уникальные треки
    for track in tracks:
        if str(track.id) not in seen_ids:
            recommendations.append(await enrich_track_response(track, db))
            seen_ids.add(str(track.id))
            if len(recommendations) >= limit:
                break

    # 6. Если рекомендаций мало, добиваем популярными (исключая уже добавленные)
    if len(recommendations) < limit:
        needed = limit - len(recommendations)
        popular_stmt = (
            select(Tracks)
            .where(Tracks.status == public_status_id)
            .where(~Tracks.id.in_(excluded_ids_subq))
            .where(Tracks.id.not_in([uuid.UUID(uid) for uid in seen_ids] if seen_ids else []))
            .order_by(desc(Tracks.listening_quantity))
            .limit(needed * 2)
        )
        popular_result = await db.execute(popular_stmt)

        for track in popular_result.scalars().all():
            if str(track.id) not in seen_ids:
                recommendations.append(await enrich_track_response(track, db))
                seen_ids.add(str(track.id))
                if len(recommendations) >= limit:
                    break

        if len(recommendations) < limit:
            conditions.append("popular_fallback")

    # 7. Формируем ответ
    genre_names = {}
    if expanded_genres:
        genres_names_result = await db.execute(
            select(Genres.id, Genres.title).where(Genres.id.in_(list(expanded_genres)))
        )
        for g in genres_names_result.all():
            genre_names[g.id] = g.title

    return {
        "items": recommendations[:limit],
        "total": len(recommendations[:limit]),
        "type": "personalized",
        "preferred_genres": preferred_genres,
        "expanded_genres": list(expanded_genres) if expanded_genres else [],
        "expanded_genres_names": [{"id": gid, "name": genre_names.get(gid)} for gid in expanded_genres if genre_names.get(gid)] if expanded_genres else [],
        "preferred_authors": [str(a) for a in preferred_authors],
        "conditions_used": conditions if conditions else ["popular_fallback"]
    }
