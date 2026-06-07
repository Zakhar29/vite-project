# src/api/routes/get_music.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from src.db.postgres_engine import get_db
from src.models.albums_models import Albums, AlbumStatuses, AlbumTracks
from src.models.tracks_models import Tracks, TracksStatuses, Genres, TrackGenres, TrackFeats
# ... ваши импорты ...

router = APIRouter(prefix="/get_music", tags=["Public Music"])


async def _get_ref_id(db: AsyncSession, model, title: str) -> int | None:
    """Вспомогательная функция для получения ID справочника"""
    res = await db.execute(select(model).where(model.title == title))
    obj = res.scalar_one_or_none()
    return obj.id if obj else None

async def build_album_response(
    album,
    db: AsyncSession, 
    public_status_id: int, 
    public_track_status_id: int
):
    if album.status != public_status_id:
        return None
    
    tracks_select = await db.execute(
        select(Tracks)
        .join(AlbumTracks, AlbumTracks.track_id == Tracks.id)
        .where(
            AlbumTracks.album_id == album.id,
            Tracks.status == public_track_status_id
        )
        .order_by(AlbumTracks.number)
    )
    tracks = tracks_select.scalars().all()
    tracks_full = []
    
    for track in tracks:
        track_genres = await db.execute(
            select(Genres)
            .where(Genres.id.in_(select(TrackGenres.genre_id).where(TrackGenres.track_id == track.id)))
        )
        track_feats = await db.execute(
            select(TrackFeats).where(TrackFeats.track_id == track.id)
        )
        tracks_full.append({
            "track_id": track.id,
            "title": track.title,
            "feats": [tf.feat_user_id for tf in track_feats.scalars().all()],
            "track_url": track.track_url,
            "bpm": float(track.bpm) if track.bpm else None,
            "genres": [g.title for g in track_genres.scalars().all()],
            "listening_quantity": track.listening_quantity
        })
    
    return {
        "id": str(album.id),
        "title": album.title,
        "cover_url": album.cover_url,
        "type": album.type,
        "published_at": album.published_at.isoformat() if album.published_at else None,
        "tracks": tracks_full
    }


@router.get("/track_full/{track_id}")
async def get_track_full(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    track_select = await db.execute(select(Tracks).where(Tracks.id == track_id))
    track = track_select.scalar_one_or_none()
    
    if not track:
        raise HTTPException(404, "Track not found")
    
    track_genres = await db.execute(
        select(Genres)
        .where(Genres.id.in_(select(TrackGenres.genre_id).where(TrackGenres.track_id == track_id)))
    )
    track_feats = await db.execute(
        select(TrackFeats).where(TrackFeats.track_id == track_id)
    )
    
    return {
        "track_id": track.id,
        "title": track.title,
        "author_id": track.author_id,
        "feats": [tf.feat_user_id for tf in track_feats.scalars().all()],
        "track_url": track.track_url,
        "track_text": track.track_text,
        "bpm": float(track.bpm) if track.bpm else None,
        "genres": [g.title for g in track_genres.scalars().all()],
        "liked_quantity": track.liked_quantity,
        "comments_quantity": track.comments_quantity,
        "published_at": track.published_at
    }


@router.get("/track/{track_id}")
async def get_track(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    track_select = await db.execute(select(Tracks).where(Tracks.id == track_id))
    track = track_select.scalar_one_or_none()
    
    if not track:
        raise HTTPException(404, "Track not found")
    
    track_genres = await db.execute(
        select(Genres)
        .where(Genres.id.in_(select(TrackGenres.genre_id).where(TrackGenres.track_id == track_id)))
    )
    track_feats = await db.execute(
        select(TrackFeats).where(TrackFeats.track_id == track_id)
    )
    
    return {
        "track_id": track.id,
        "title": track.title,
        "author_id": track.author_id,
        "feats": [tf.feat_user_id for tf in track_feats.scalars().all()],
        "track_url": track.track_url,
        "bpm": float(track.bpm) if track.bpm else None,
        "genres": [g.title for g in track_genres.scalars().all()]
    }      

 

@router.get("/albums/{album_id}")
async def get_public_album(
    album_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    album = await db.get(Albums, album_id)
    if album is None:
        raise HTTPException(404, "Альбом не найден")
    
    public_status_id = await _get_ref_id(db, AlbumStatuses, "public")
    public_track_status_id = await _get_ref_id(db, TracksStatuses, "public")
    
    result = await build_album_response(album, db, public_status_id, public_track_status_id)
    
    if result is None:
        raise HTTPException(404, "Альбом не опубликован")
    
    return result


@router.get("/albums/user/{user_id}")
async def get_user_albums(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
):
    albums_result = await db.execute(
        select(Albums).where(Albums.author_id == user_id)
    )
    albums = albums_result.scalars().all()
    
    public_status_id = await _get_ref_id(db, AlbumStatuses, "public")
    public_track_status_id = await _get_ref_id(db, TracksStatuses, "public")
    
    albums_list = {"user_albums": [], "user_feats": []}
    
    
    
    for album in albums:
        resp = await build_album_response(album, db, public_status_id, public_track_status_id)
        if resp:
            albums_list["user_albums"].append(resp)
    
    # Для feats нужен отдельный запрос с join
    feats_result = await db.execute(
        select(Albums)
        .join(AlbumTracks, Albums.id == AlbumTracks.album_id)
        .join(Tracks, AlbumTracks.track_id == Tracks.id)
        .join(TrackFeats, TrackFeats.track_id == Tracks.id)
        .where(TrackFeats.feat_user_id == user_id)
        .distinct()
    )
    
    for album in feats_result.scalars().all():
        resp = await build_album_response(album, db, public_status_id, public_track_status_id)
        if resp:
            albums_list["user_feats"].append(resp)
    
    return albums_list

