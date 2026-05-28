from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
import uuid
from decimal import Decimal

from src.db.postgres_engine import get_db
from src.models.albums_models import (
    Albums, Tracks, AlbumTracks, AlbumTypes, AlbumStatuses, TracksStatuses, TrackGenres, Genres
)
from src.api.dependencies import get_current_user, CurrentUser
from src.api.schemas import AlbumCreateDraft, AlbumUpdateDraft, TrackCreateDraft, TrackUpdateDraft

router = APIRouter(prefix="/get_music", tags=["Albums & Tracks"])

# Кэш ID справочников (в проде лучше вынести в Redis или config)


async def _get_ref_id(db: AsyncSession, model, title: str) -> int | None:
    res = await db.execute(select(model).where(model.title == title))
    obj = res.scalar_one_or_none()
    return obj.id if obj else None


@router.get("/albums/{album_id}", status_code=201)
async def get_public_album(
        album_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        user: CurrentUser = Depends(get_current_user)
):
    album = await db.execute(select(Albums).where(Albums.id == album_id)).scalar_one_or_none()

    if album is None or album.status != _get_ref_id(db, Albums, "public"):
        raise HTTPException(status_code=404, detail="Album not found")

    album_type = await db.execute((select(AlbumTypes)).where(AlbumTypes.id == album.type).scalar_one_or_none()).title
    tracks = await db.execute(select(AlbumTracks).where(AlbumTracks.album_id == album_id)).scalars().all()

    track_list = []

    for track in tracks:
        track_genres_id = await db.execute(select(TrackGenres).where(TrackGenres.track_id == track.track_id))
        genres = await db.execute(select(Genres).where(Genres.id in track_genres_id)).scalars().all()
        genres_list = []
        for genre in genres:
            genres_list.append(genre.title)

        track_list.append(
            {
                'id': track.id,
                "url": track.track_url,
                "title": track.title,
                "genres": genres_list,
                "bpm": track.bpm,
                "liked_quantity": track.liked_quantity,
                "listening_quantity": track.listening_quantity,
                "published_at": track.published_at,
            }
        )

    return {
        "title": album.title,
        "author_id": album.author_id,
        "type": album_type,
        "cover_url": album.cover_url,
        "liked_quantity": album.liked_quantity,
        "follower_quantity": album.follower_quantity,
        "listening_quantity": album.listening_quantity,
        "comments_quantity": album.comments_quantity,
        "published_at": album.published_at,
        "track_list": track_list,
    }



