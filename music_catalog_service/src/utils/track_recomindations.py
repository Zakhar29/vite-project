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
from config import settings



# ========== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ==========

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


async def global_track_recommendations(
        limit: int, db: AsyncSession
) -> dict:
    """Глобальные рекомендации (популярное, новое, случайное)"""

    popular_limit = int(limit * settings.RECOMMENDATIONS_POPULAR_FACTOR)
    new_limit = int(limit * settings.RECOMMENDATIONS_NEW_FACTOR)
    random_limit = limit - popular_limit - new_limit

    # Популярные треки
    popular_stmt = (
        select(Tracks)
        .where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))
        .order_by(desc(Tracks.listening_quantity))
        .limit(popular_limit)
    )

    # Новые треки
    new_stmt = (
        select(Tracks)
        .where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))
        .order_by(desc(Tracks.published_at))
        .limit(new_limit)
    )

    # Случайные треки
    random_stmt = (
        select(Tracks)
        .where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))
        .order_by(func.random())
        .limit(random_limit)
    )

    popular_result = await db.execute(popular_stmt)
    new_result = await db.execute(new_stmt)
    random_result = await db.execute(random_stmt)

    recommendations = []

    for track in popular_result.scalars().all():
        recommendations.append(await enrich_track_response(track, db))
    for track in new_result.scalars().all():
        recommendations.append(await enrich_track_response(track, db))
    for track in random_result.scalars().all():
        recommendations.append(await enrich_track_response(track, db))

    return {
        "items": recommendations[:limit],
        "total": len(recommendations[:limit]),
        "type": "global"
    }


async def cold_start_recommendations(limit: int, db: AsyncSession) -> List[dict]:
    """Рекомендации для новых пользователей (холодный старт)"""

    from src.models.tracks_models import LikedTracks, ListeningTracks

    # Стратегия: популярные треки + новинки + случайные

    popular_limit = int(limit * 0.6)  # 60% популярные
    new_limit = int(limit * 0.3)  # 30% новинки
    random_limit = limit - popular_limit - new_limit  # 10% случайные
    # Популярные треки (по прослушиваниям)
    popular_stmt = (
        select(Tracks)
        .where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))
        .order_by(desc(Tracks.listening_quantity))
        .limit(popular_limit)
    )

    # Новинки
    new_stmt = (
        select(Tracks)
        .where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))
        .order_by(desc(Tracks.published_at))
        .limit(new_limit)
    )

    # Случайные треки (для разнообразия)
    random_stmt = (
        select(Tracks)
        .where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))
        .order_by(func.random())
        .limit(random_limit)
    )

    popular_result = await db.execute(popular_stmt)
    new_result = await db.execute(new_stmt)
    random_result = await db.execute(random_stmt)

    recommendations = []

    for track in popular_result.scalars().all():
        recommendations.append(await enrich_track_response(track, db))
    for track in new_result.scalars().all():
        recommendations.append(await enrich_track_response(track, db))
    for track in random_result.scalars().all():
        recommendations.append(await enrich_track_response(track, db))

    return recommendations[:limit]

async def personalized_track_recommendations(user_id: uuid.UUID, limit: int, db: AsyncSession) -> dict:
    """Персонализированные рекомендации на основе истории пользователя"""

    # 1. Проверяем активность пользователя
    has_activity = await check_user_activity(user_id, db)

    if not has_activity:
        # Холодный старт: рекомендуем популярные треки
        cold_start_recs = await cold_start_recommendations(limit, db)
        return {
            "items": cold_start_recs,
            "total": len(cold_start_recs),
            "type": "cold_start",
            "message": "New user. Showing popular tracks to get you started."
        }

    # 2. Получаем жанры пользователя (существующая логика)
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

    # Если жанров нет (пользователь что-то слушал, но жанры не определились)
    if not preferred_genres:
        popular_genres = await get_popular_genres(db)
        expanded_genres = set(popular_genres)
        preferred_genres = popular_genres
    else:
        # Расширяем жанры через GenreParents
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

    # 4. Строим рекомендательный запрос
    stmt = select(Tracks).where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))

    # Исключаем уже прослушанные/лайкнутые треки
    listened_tracks = select(ListeningTracks.track_id).where(ListeningTracks.user_id == user_id)
    liked_tracks = select(LikedTracks.track_id).where(LikedTracks.user_id == user_id)
    stmt = stmt.where(~Tracks.id.in_(listened_tracks.union(liked_tracks)))

    # Приоритет: расширенные жанры или авторы
    conditions = []
    if expanded_genres:
        stmt = stmt.join(TrackGenres).where(TrackGenres.genre_id.in_(list(expanded_genres)))
        conditions.append("genres")
    if preferred_authors:
        stmt = stmt.where(Tracks.author_id.in_(preferred_authors))
        conditions.append("authors")

    stmt = stmt.order_by(desc(Tracks.listening_quantity)).limit(limit)

    result = await db.execute(stmt)
    tracks = result.scalars().all()

    # 5. Если рекомендаций мало, добиваем популярными
    if len(tracks) < limit:
        popular_limit = limit - len(tracks)
        popular_stmt = (
            select(Tracks)
            .where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))
            .where(~Tracks.id.in_(listened_tracks.union(liked_tracks)))
            .order_by(desc(Tracks.listening_quantity))
            .limit(popular_limit)
        )
        popular_result = await db.execute(popular_stmt)
        tracks.extend(popular_result.scalars().all())

    # 6. Формируем ответ
    genre_names = {}
    if expanded_genres:
        genres_names_result = await db.execute(
            select(Genres.id, Genres.title).where(Genres.id.in_(list(expanded_genres)))
        )
        for g in genres_names_result.all():
            genre_names[g.id] = g.title

    response = []
    for track in tracks:
        response.append(await enrich_track_response(track, db))

    return {
        "items": response[:limit],
        "total": len(response[:limit]),
        "type": "personalized",
        "preferred_genres": preferred_genres,
        "expanded_genres": list(expanded_genres) if expanded_genres else [],
        "expanded_genres_names": [{"id": gid, "name": genre_names.get(gid)} for gid in expanded_genres if
                                  genre_names.get(gid)] if expanded_genres else [],
        "preferred_authors": [str(a) for a in preferred_authors],
        "conditions_used": conditions if conditions else ["popular_fallback"]
    }
