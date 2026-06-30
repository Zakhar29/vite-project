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
from src.utils.track_recomindations import (
    get_related_genres,
    enrich_track_response,
    check_user_activity,
    global_track_recommendations,
    cold_start_recommendations,
    personalized_track_recommendations
)
from config import settings

router = APIRouter(prefix="/tracks", tags=["Tracks"])


@router.get("/search")
async def search_tracks(
        query: Optional[str] = Query(None, min_length=1, max_length=100, description="Поиск по названию"),
        genre_ids: Optional[List[int]] = Query(None, description="ID жанров"),
        author_id: Optional[uuid.UUID] = Query(None, description="ID автора"),
        bpm_min: Optional[float] = Query(None, ge=10, le=1000, description="Минимальный BPM"),
        bpm_max: Optional[float] = Query(None, ge=10, le=1000, description="Максимальный BPM"),
        sort_by: str = Query("relevance",
                             pattern="^(relevance|published_at|liked_quantity|listening_quantity|bpm|title)$"),
        sort_order: str = Query("desc", pattern="^(asc|desc)$"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """Поиск треков с фильтрацией"""

    stmt = select(Tracks).where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))

    if query:
        search_pattern = f"%{query}%"
        stmt = stmt.where(Tracks.title.ilike(search_pattern))

    if author_id:
        stmt = stmt.where(Tracks.author_id == author_id)
    if bpm_min:
        stmt = stmt.where(Tracks.bpm >= bpm_min)
    if bpm_max:
        stmt = stmt.where(Tracks.bpm <= bpm_max)
    if genre_ids:
        stmt = stmt.join(TrackGenres).where(TrackGenres.genre_id.in_(genre_ids))

    # Исправленная сортировка с case()
    if sort_by == "relevance" and query:
        stmt = stmt.order_by(
            case(
                (Tracks.title.ilike(f"{query}%"), 1),
                else_=2
            ).asc(),
            desc(Tracks.listening_quantity)
        )
    elif sort_by == "relevance":
        stmt = stmt.order_by(desc(Tracks.listening_quantity))
    else:
        order_col = getattr(Tracks, sort_by)
        if sort_order == "desc":
            stmt = stmt.order_by(desc(order_col))
        else:
            stmt = stmt.order_by(order_col)

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    tracks = result.scalars().all()

    response = []
    for track in tracks:
        response.append(await enrich_track_response(track, db))

    # Подсчёт общего количества
    count_stmt = select(func.count()).select_from(Tracks).where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))
    if query:
        count_stmt = count_stmt.where(Tracks.title.ilike(f"%{query}%"))
    if author_id:
        count_stmt = count_stmt.where(Tracks.author_id == author_id)
    if bpm_min:
        count_stmt = count_stmt.where(Tracks.bpm >= bpm_min)
    if bpm_max:
        count_stmt = count_stmt.where(Tracks.bpm <= bpm_max)
    if genre_ids:
        count_stmt = count_stmt.join(TrackGenres).where(TrackGenres.genre_id.in_(genre_ids))

    total = await db.execute(count_stmt)

    return {
        "items": response,
        "total": total.scalar_one(),
        "skip": skip,
        "limit": limit,
        "search_query": query
    }

@router.get("/recommendations")
async def get_track_recommendations(
        user_id: uuid.UUID | None = None,
        limit: int = Query(20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """Получение рекомендаций треков"""

    if user_id:
        return await personalized_track_recommendations(user_id, limit, db)
    else:
        return await global_track_recommendations(limit, db)
# ========== ПОХОЖИЕ ТРЕКИ ==========

@router.get("/{track_id}/similar")
async def get_similar_tracks(
        track_id: uuid.UUID,
        limit: int = Query(10, ge=1, le=50),
        db: AsyncSession = Depends(get_db)
):
    """Получение треков, похожих на указанный (по жанрам и BPM)"""
    track_result = await db.execute(
        select(Tracks)
        .where(
            and_(
                Tracks.id == track_id),
                Tracks.status.in_(select(
                    TracksStatuses.id)
                    .where(TracksStatuses.title == "public")
                )
            )
    )
    track = track_result.scalar_one_or_none()

    if not track:
        raise HTTPException(404, "Track not found")

    # Получаем жанры исходного трека
    genres_result = await db.execute(
        select(TrackGenres.genre_id).where(TrackGenres.track_id == track_id)
    )
    genre_ids = [g for g in genres_result.scalars().all()]

    if not genre_ids:
        return {"items": [], "total": 0, "based_on": str(track_id)}

    # Расширяем жанры через GenreParents
    expanded_genres = await get_related_genres(db, genre_ids, max_depth=1)

    stmt = (
        select(Tracks)
        .where(Tracks.status.in_(
        select(TracksStatuses.id).where(TracksStatuses.title == "public")
    ))
        .where(Tracks.id != track_id)
        .join(TrackGenres)
        .where(TrackGenres.genre_id.in_(expanded_genres))
    )

    # Фильтр по BPM (±5%)
    if track.bpm:
        bpm_min = float(track.bpm) * 0.95
        bpm_max = float(track.bpm) * 1.05
        stmt = stmt.where(Tracks.bpm.between(bpm_min, bpm_max))

    stmt = stmt.group_by(Tracks.id).order_by(func.count().desc()).limit(limit)

    result = await db.execute(stmt)
    similar_tracks = result.scalars().all()

    response = []
    for similar_track in similar_tracks:
        response.append(await enrich_track_response(similar_track, db))

    return {
        "items": response,
        "total": len(response),
        "based_on": str(track_id)
    }