from datetime import datetime, timezone

from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update

import uuid
import uuid6
from decimal import Decimal

from src.db.postgres_engine import get_db
from src.models.albums_models import (
    Albums, AlbumTracks, AlbumTypes, AlbumStatuses
)
from src.models.tracks_models import Tracks, TracksStatuses, Genres, TrackGenres
from src.api.dependencies import get_current_user, CurrentUser
from src.api.schemas import AlbumCreateDraft, AlbumUpdateDraft, TrackCreateDraft, TrackUpdateDraft

router = APIRouter(prefix="/album_create", tags=["Albums & Tracks creation"])

# Кэш ID справочников (в проде лучше вынести в Redis или config)


async def _get_ref_id(db: AsyncSession, model, title: str) -> int | None:
    res = await db.execute(select(model).where(model.title == title))
    obj = res.scalar_one_or_none()
    return obj.id if obj else None


class CreateAndAttachTrackRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    text: str = Field(default="")
    bpm: Decimal = Field(..., ge=10, le=1000)
    author_attention: bool = Field(default=False)


@router.post("/albums", status_code=201)
async def create_album_draft(
    payload: AlbumCreateDraft,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    type_id = await _get_ref_id(db, AlbumTypes, payload.type)
    status_id = await _get_ref_id(db, AlbumStatuses, "draft")

    album = Albums(
        author_id=user.id,
        title=payload.title.strip(),
        type=type_id,
        status=status_id,
        cover_url=payload.cover_url or ""
    )
    db.add(album)
    await db.commit()
    await db.refresh(album)
    return {"id": str(album.id), "title": album.title, "status": "draft"}


@router.patch("/albums/{album_id}")
async def update_album_draft(
    album_id: uuid.UUID,
    payload: AlbumUpdateDraft,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    status_id = await _get_ref_id(db, AlbumStatuses, "public")
    res = await db.execute(
        select(Albums).where(
            Albums.id == album_id,
            Albums.author_id == user.id,
            Albums.status != status_id
        )
    )
    album = res.scalar_one_or_none()
    if not album:
        raise HTTPException(404, "Альбом не найден или уже опубликован")

    if payload.title:
        album.title = payload.title.strip()
    if payload.cover_url:
        album.cover_url = payload.cover_url
    if payload.type:
        album.type = await _get_ref_id(db, AlbumTypes, payload.type) or album.type

    await db.commit()
    return {"status": "updated"}


@router.patch("/tracks/{track_id}/audio")
async def attach_audio(
    track_id: uuid.UUID,
    s3_url: str,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    async with db.begin():
        res = await db.execute(select(Tracks).where(Tracks.id == track_id, Tracks.author_id == user.id))
        track = res.scalar_one_or_none()
        if not track:
            raise HTTPException(404, "Трек не найден")
        track.track_url = s3_url
    return {"status": "attached"}
    

@router.post("/albums/{album_id}/tracks", status_code=201)
async def create_and_attach_track(
    album_id: uuid.UUID,
    payload: CreateAndAttachTrackRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user)
):
    # 1. Проверяем альбом
    album = await db.get(Albums, album_id)
    if not album or album.author_id != current_user.id:
        raise HTTPException(404, "Альбом не найден")
    
    # 2. Создаём новый трек
    draft_status_id = await _get_ref_id(db, TracksStatuses, "draft")
    
    new_track = Tracks(
        id=uuid6.uuid7(),
        author_id=current_user.id,
        title=payload.title.strip(),
        track_text=payload.text,
        track_url="",  
        bpm=payload.bpm,
        status=draft_status_id,
    )
    db.add(new_track)
    await db.flush()  
    
    # 3. Вычисляем номер трека в альбоме
    result = await db.execute(
        select(func.coalesce(func.max(AlbumTracks.number), 0) + 1)
        .where(AlbumTracks.album_id == album_id)
    )
    next_number = result.scalar_one()
    
    # 4. Привязываем трек к альбому
    album_track = AlbumTracks(
        album_id=album_id,
        track_id=new_track.id,  # 🔥 Используем только что созданный ID
        author_attention=payload.author_attention,
        number=next_number
    )
    db.add(album_track)
    
    await db.commit()
    
    return {
        "message": "Track created and attached",
        "track_id": str(new_track.id),
        "album_id": str(album_id),
        "number": next_number
    }


@router.post("/albums/{album_id}/publish")
async def publish_album(
    album_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    # Проверяем альбом
    album = await db.get(Albums, album_id)
    if not album or album.author_id != user.id:
        raise HTTPException(404, "Альбом не найден")
    
    # Проверяем, что есть хотя бы один трек
    tracks_count = await db.execute(
        select(func.count()).select_from(AlbumTracks).where(AlbumTracks.album_id == album_id)
    )
    if tracks_count.scalar_one() == 0:
        raise HTTPException(400, "Альбом должен содержать минимум 1 трек")
    
    # Меняем статус альбома
    public_status_id = await _get_ref_id(db, AlbumStatuses, "public")
    album.status = public_status_id
    album.published_at = datetime.now(timezone.utc)
    
    # Меняем статус всех треков
    track_public_status_id = await _get_ref_id(db, TracksStatuses, "public")
    await db.execute(
        update(Tracks)
        .where(Tracks.id.in_(
            select(AlbumTracks.track_id).where(AlbumTracks.album_id == album_id)
        ))
        .values(status=track_public_status_id, published_at=datetime.now(timezone.utc))
    )
    
    await db.commit()
    
    return {
        "status": "published",
        "album_id": str(album_id),
        "published_at": album.published_at.isoformat()
    }
