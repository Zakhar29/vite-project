from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func, desc, case
from typing import Optional, List
import uuid

from src.db.postgres_engine import get_db
from src.models.albums_models import (
    Albums, AlbumStatuses, AlbumTypes, AlbumTracks, AlbumFollows, LikedAlbums
)
from src.utils.album_recomendations import (
    get_public_status_id,
    get_album_genres,
    enrich_album_response,
    check_user_activity,
    get_popular_albums_genres,
    check_album_activity,
    get_user_album_genres,
    cold_start_album_recommendations,
    global_album_recommendations,
    personalized_album_recommendations
)
from src.models.tracks_models import Tracks, TrackGenres, Genres, TrackFeats
from config import settings

router = APIRouter(prefix="/albums", tags=["Albums"])


@router.get("/search")
async def search_albums(
        query: Optional[str] = Query(None, min_length=1, max_length=100, description="Поиск по названию альбома"),
        genre_ids: Optional[List[int]] = Query(None, description="ID жанров"),
        author_id: Optional[uuid.UUID] = Query(None, description="ID автора"),
        album_type: Optional[int] = Query(None, description="Тип альбома (1-album, 2-single, 3-ep)"),
        published_after: Optional[str] = Query(None, description="Опубликован после (ISO дата)"),
        published_before: Optional[str] = Query(None, description="Опубликован до (ISO дата)"),
        sort_by: str = Query("relevance",
                             pattern="^(relevance|created_at|published_at|liked_quantity|listening_quantity|tracks_count)$"),
        sort_order: str = Query("desc", pattern="^(asc|desc)$"),
        skip: int = Query(0, ge=0),
        limit: int = Query(20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """Поиск альбомов с фильтрацией"""

    public_status_id = await get_public_status_id(db)
    stmt = select(Albums).where(Albums.status == public_status_id)

    if query:
        search_pattern = f"%{query}%"
        stmt = stmt.where(Albums.title.ilike(search_pattern))

    if author_id:
        stmt = stmt.where(Albums.author_id == author_id)
    if album_type:
        stmt = stmt.where(Albums.type == album_type)
    if published_after:
        stmt = stmt.where(Albums.published_at >= published_after)
    if published_before:
        stmt = stmt.where(Albums.published_at <= published_before)
    if genre_ids:
        stmt = stmt.join(AlbumTracks).join(Tracks).join(TrackGenres).where(
            TrackGenres.genre_id.in_(genre_ids)
        ).distinct()

    # Исправленная сортировка с case()
    if sort_by == "relevance" and query:
        stmt = stmt.order_by(
            case(
                (Albums.title.ilike(f"{query}%"), 1),
                (Albums.title.ilike(f"%{query}%"), 2),
                else_=3
            ).asc(),
            desc(Albums.listening_quantity)
        )
    elif sort_by == "relevance":
        stmt = stmt.order_by(desc(Albums.listening_quantity))
    elif sort_by == "tracks_count":
        subq = (
            select(AlbumTracks.album_id, func.count().label("track_count"))
            .group_by(AlbumTracks.album_id)
            .subquery()
        )
        stmt = stmt.outerjoin(subq, subq.c.album_id == Albums.id)
        if sort_order == "desc":
            stmt = stmt.order_by(desc(func.coalesce(subq.c.track_count, 0)))
        else:
            stmt = stmt.order_by(func.coalesce(subq.c.track_count, 0))
    else:
        order_col = getattr(Albums, sort_by)
        if sort_order == "desc":
            stmt = stmt.order_by(desc(order_col))
        else:
            stmt = stmt.order_by(order_col)

    stmt = stmt.offset(skip).limit(limit)

    result = await db.execute(stmt)
    albums = result.scalars().all()

    response = []
    for album in albums:
        response.append(await enrich_album_response(album, db))

    # Подсчёт общего количества
    count_stmt = select(func.count()).select_from(Albums).where(Albums.status == public_status_id)
    if query:
        count_stmt = count_stmt.where(Albums.title.ilike(f"%{query}%"))
    if author_id:
        count_stmt = count_stmt.where(Albums.author_id == author_id)
    if album_type:
        count_stmt = count_stmt.where(Albums.type == album_type)
    if published_after:
        count_stmt = count_stmt.where(Albums.published_at >= published_after)
    if published_before:
        count_stmt = count_stmt.where(Albums.published_at <= published_before)

    total = await db.execute(count_stmt)

    return {
        "items": response,
        "total": total.scalar_one(),
        "skip": skip,
        "limit": limit,
        "search_query": query
    }


# ========== ПОХОЖИЕ АЛЬБОМЫ ==========

@router.get("/{album_id}/similar")
async def get_similar_albums(
        album_id: uuid.UUID,
        limit: int = Query(10, ge=1, le=50),
        db: AsyncSession = Depends(get_db)
):
    """
    Получение альбомов, похожих на указанный.
    Основано на общих жанрах и авторе.
    """

    public_status_id = await get_public_status_id(db)

    # Получаем исходный альбом
    album_result = await db.execute(select(Albums).where(Albums.id == album_id))
    album = album_result.scalar_one_or_none()

    if not album:
        raise HTTPException(404, "Album not found")

    # Получаем жанры исходного альбома
    album_genres = await get_album_genres(db, album_id)

    if not album_genres:
        return {"items": [], "total": 0, "based_on": str(album_id)}

    # Получаем ID жанров по названиям
    genres_result = await db.execute(
        select(Genres.id).where(Genres.title.in_(album_genres))
    )
    genre_ids = [g for g in genres_result.scalars().all()]

    # Ищем похожие альбомы
    stmt = (
        select(Albums)
        .where(Albums.status == public_status_id)
        .where(Albums.id != album_id)
        .join(AlbumTracks)
        .join(Tracks)
        .join(TrackGenres)
        .where(TrackGenres.genre_id.in_(genre_ids))
        .distinct()
    )

    # Приоритет: альбомы того же автора
    stmt = stmt.order_by(
        func.case((Albums.author_id == album.author_id, 1), else_=2).asc(),
        desc(Albums.listening_quantity)
    ).limit(limit)

    result = await db.execute(stmt)
    similar_albums = result.scalars().all()

    response = []
    for similar_album in similar_albums:
        response.append(await enrich_album_response(similar_album, db))

    return {
        "items": response,
        "total": len(response),
        "based_on": str(album_id)
    }


@router.get("/recommendations")
async def get_album_recommendations(
        user_id: Optional[uuid.UUID] = Query(None, description="ID пользователя для персонализации"),
        limit: int = Query(20, ge=1, le=100),
        db: AsyncSession = Depends(get_db)
):
    """
    Получение рекомендаций альбомов.
    Если указан user_id и есть активность — персонализированные.
    Если user_id не указан или пользователь новый — глобальные рекомендации.
    """

    if user_id:
        has_activity = await check_album_activity(user_id, db)

        if not has_activity:
            # Холодный старт
            cold_start_recs = await cold_start_album_recommendations(limit, db)
            return {
                "items": cold_start_recs,
                "total": len(cold_start_recs),
                "type": "cold_start",
                "message": "New user. Showing popular albums to get you started."
            }

        # Персонализированные рекомендации
        return await personalized_album_recommendations(user_id, limit, db)
    else:
        # Глобальные рекомендации
        return await global_album_recommendations(limit, db)



