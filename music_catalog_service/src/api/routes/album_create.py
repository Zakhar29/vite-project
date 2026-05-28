from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid
from decimal import Decimal

from src.db.postgres_engine import get_db
from src.models.albums_models import (
    Albums, Tracks, AlbumTracks, AlbumTypes, AlbumStatuses, TracksStatuses
)
from src.api.dependencies import get_current_user, CurrentUser
from src.api.schemas import AlbumCreateDraft, AlbumUpdateDraft, TrackCreateDraft, TrackUpdateDraft

router = APIRouter(prefix="/album_create", tags=["Albums & Tracks creation"])

# Кэш ID справочников (в проде лучше вынести в Redis или config)


async def _get_ref_id(db: AsyncSession, model, title: str) -> int | None:
    res = await db.execute(select(model).where(model.title == title))
    obj = res.scalar_one_or_none()
    return obj.id if obj else None


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
    async with db.begin():
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

    return {"status": "updated"}


@router.post("/albums/{album_id}/tracks", status_code=201)
async def add_track_to_album(
    album_id: uuid.UUID,
    payload: TrackCreateDraft,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    async with db.begin():
        status_id = await _get_ref_id(db, AlbumStatuses, "public")
        album_res = await db.execute(
            select(Albums).where(
                Albums.id == album_id,
                Albums.author_id == user.id,
                Albums.status != status_id
            )
        )
        if not album_res.scalar_one_or_none():
            raise HTTPException(400, "Редактирование опубликованного альбома запрещено")

        next_num_res = await db.execute(
            select(func.coalesce(func.max(AlbumTracks.number), 0) + 1)
            .where(AlbumTracks.album_id == album_id)
        )
        next_number = next_num_res.scalar()

        track_status_id = await _get_ref_id(db, TracksStatuses, "draft")
        track = Tracks(
            author_id=user.id,
            title=payload.title.strip(),
            track_text=payload.text or "",
            bpm=payload.bpm or Decimal("0.00"),
            track_url="",
            status=track_status_id
        )
        db.add(track)
        db.add(AlbumTracks(album_id=album_id, track_id=track.id, number=next_number))

    return {"track_id": str(track.id), "number": next_number}


@router.patch("/tracks/{track_id}/attach-audio")
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


@router.post("/albums/{album_id}/publish")
async def publish_album(
    album_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    async with db.begin():
        album_res = await db.execute(
            select(Albums).where(Albums.id == album_id, Albums.author_id == user.id)
        )
        album = album_res.scalar_one_or_none()
        if not album:
            raise HTTPException(404, "Альбом не найден")
        if album.status == await _get_ref_id(db, AlbumStatuses, "public"):
            raise HTTPException(400, "Уже опубликован")

        tracks_res = await db.execute(
            select(Tracks).join(AlbumTracks).where(AlbumTracks.album_id == album_id)
        )
        tracks = tracks_res.scalars().all()

        if not tracks:
            raise HTTPException(400, "Требуется минимум 1 трек")
        for t in tracks:
            if not t.title or not t.track_url:
                raise HTTPException(400, f"Трек {t.id} не готов к публикации")

        album.status = await _get_ref_id(db, AlbumStatuses, "public")
        track_pub_status = await _get_ref_id(db, TracksStatuses, "public")
        album.published_at = datetime.utcnow().replace(tzinfo=timezone.utc)

        for t in tracks:
            t.status = track_pub_status
            t.published_at = datetime.utcnow().replace(tzinfo=timezone.utc)

    return {"status": "published", "album_id": str(album_id), "track_count": len(tracks)}
