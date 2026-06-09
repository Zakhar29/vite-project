from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update, delete
import uuid

from src.db.postgres_engine import get_db
from src.models.tracks_models import Tracks, LikedTracks
from src.models.albums_models import Albums, LikedAlbums, AlbumFollows
from src.api.dependencies import get_current_user, CurrentUser

router = APIRouter(prefix="/music", tags=["Music Counters"])


# ========== КОММЕНТАРИИ ==========

@router.patch("/tracks/{track_id}/inc-comments")
async def increment_track_comments(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Увеличить счётчик комментариев трека (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Tracks)
        .where(Tracks.id == track_id)
        .values(comments_quantity=Tracks.comments_quantity + 1)
        .returning(Tracks.id, Tracks.comments_quantity)
    )
    updated = result.fetchone()
    
    if not updated:
        raise HTTPException(404, "Track not found")
    
    return {"track_id": str(updated[0]), "comments_quantity": updated[1]}


@router.patch("/tracks/{track_id}/dec-comments")
async def decrement_track_comments(
    track_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Уменьшить счётчик комментариев трека (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Tracks)
        .where(Tracks.id == track_id, Tracks.comments_quantity > 0)
        .values(comments_quantity=Tracks.comments_quantity - 1)
        .returning(Tracks.id, Tracks.comments_quantity)
    )
    updated = result.fetchone()
    
    if not updated:
        raise HTTPException(404, "Track not found or comments_quantity is 0")
    
    return {"track_id": str(updated[0]), "comments_quantity": updated[1]}


@router.patch("/albums/{album_id}/inc-comments")
async def increment_album_comments(
    album_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    user: CurrentUser = Depends(get_current_user)
):
    """Увеличить счётчик комментариев альбома (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Albums)
        .where(Albums.id == album_id)
        .values(comments_quantity=Albums.comments_quantity + 1)
        .returning(Albums.id, Albums.comments_quantity)
    )
    updated = result.fetchone()
    
    if not updated:
        raise HTTPException(404, "Album not found")
    
    return {"album_id": str(updated[0]), "comments_quantity": updated[1]}


@router.patch("/albums/{album_id}/dec-comments")
async def decrement_album_comments(
        album_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        user: CurrentUser = Depends(get_current_user)
):
    """Уменьшить счётчик комментариев альбома (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Albums)
        .where(Albums.id == album_id, Albums.comments_quantity > 0)
        .values(comments_quantity=Albums.comments_quantity - 1)
        .returning(Albums.id, Albums.comments_quantity)
    )
    updated = result.fetchone()
    
    if not updated:
        raise HTTPException(404, "Album not found or comments_quantity is 0")
    
    return {"album_id": str(updated[0]), "comments_quantity": updated[1]}


# ========== ЛАЙКИ (ТОЛЬКО ДЛЯ ТРЕКОВ) ==========

@router.patch("/tracks/{track_id}/inc-likes")
async def increment_track_likes(
        track_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        user: CurrentUser = Depends(get_current_user)
):
    """Увеличить счётчик лайков трека (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Tracks)
        .where(Tracks.id == track_id)
        .values(liked_quantity=Tracks.liked_quantity + 1)
        .returning(Tracks.id, Tracks.liked_quantity)
    )
    updated = result.fetchone()

    like = LikedTracks(track_id = track_id, user_id = user.id)

    db.add(like)
    await db.commit()
    await db.refresh(like)
    
    if not updated:
        raise HTTPException(404, "Track not found")
    
    return {"track_id": str(updated[0]), "liked_quantity": updated[1]}


@router.patch("/tracks/{track_id}/dec-likes")
async def decrement_track_likes(
        track_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        user: CurrentUser = Depends(get_current_user)
):
    """Уменьшить счётчик лайков трека (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Tracks)
        .where(Tracks.id == track_id, Tracks.liked_quantity > 0)
        .values(liked_quantity=Tracks.liked_quantity - 1)
        .returning(Tracks.id, Tracks.liked_quantity)
    )
    updated = result.fetchone()
    await db.execute(
        delete(LikedTracks)
            .where(
            LikedTracks.track_id == track_id,
            LikedTracks.user_id == user.id
        )
    )

    await db.commit()

    if not updated:
        raise HTTPException(404, "Track not found or liked_quantity is 0")
    
    return {"track_id": str(updated[0]), "liked_quantity": updated[1]}


@router.patch("/albums/{album_id}/inc-likes")
async def increment_album_likes(
        album_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        user: CurrentUser = Depends(get_current_user)
):
    """Увеличить счётчик лайков трека (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Albums)
        .where(Albums.id == album_id)
        .values(liked_quantity=Tracks.liked_quantity + 1)
        .returning(Albums.id, Tracks.liked_quantity)
    )
    updated = result.fetchone()

    like = LikedAlbums(album_id=album_id, user_id=user.id)

    db.add(like)
    await db.commit()
    await db.refresh(like)

    if not updated:
        raise HTTPException(404, "Track not found")

    return {"track_id": str(updated[0]), "liked_quantity": updated[1]}


@router.patch("/albums/{album_id}/dec-likes")
async def decrement_album_likes(
        album_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        user: CurrentUser = Depends(get_current_user)
):
    """Уменьшить счётчик лайков трека (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Albums)
        .where(Albums.id == album_id, Albums.liked_quantity > 0)
        .values(liked_quantity=Albums.liked_quantity - 1)
        .returning(Albums.id, Albums.liked_quantity)
    )
    updated = result.fetchone()
    await db.execute(
        delete(LikedAlbums)
        .where(
            LikedAlbums.album_id == album_id,
            LikedAlbums.user_id == user.id
        )
    )

    await db.commit()

    if not updated:
        raise HTTPException(404, "Track not found or liked_quantity is 0")

    return {"album_id": str(updated[0]), "liked_quantity": updated[1]}


# ========== ПРОСЛУШИВАНИЯ (ТРЕКИ) ==========

@router.patch("/tracks/{track_id}/inc-listening")
async def increment_track_listening(
        track_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
):
    """Увеличить счётчик прослушиваний трека (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Tracks)
        .where(Tracks.id == track_id)
        .values(listening_quantity=Tracks.listening_quantity + 1)
        .returning(Tracks.id, Tracks.listening_quantity)
    )
    updated = result.fetchone()
    
    if not updated:
        raise HTTPException(404, "Track not found")
    
    return {"track_id": str(updated[0]), "listening_quantity": updated[1]}


# ========== ПРОСЛУШИВАНИЯ (АЛЬБОМЫ) ==========

@router.patch("/albums/{album_id}/inc-listening")
async def increment_album_listening(
        album_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
):
    """Увеличить счётчик прослушиваний альбома (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Albums)
        .where(Albums.id == album_id)
        .values(listening_quantity=Albums.listening_quantity + 1)
        .returning(Albums.id, Albums.listening_quantity)
    )
    updated = result.fetchone()

    if not updated:
        raise HTTPException(404, "Album not found")

    return {"album_id": str(updated[0]), "listening_quantity": updated[1]}


@router.patch("/albums/{album_id}/follow")
async def album_follow(
        album_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        user: CurrentUser = Depends(get_current_user)
):
    """Увеличить счётчик прослушиваний альбома (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Albums)
        .where(Albums.id == album_id)
        .values(listening_quantity=Albums.follower_quantity + 1)
        .returning(Albums.id, Albums.follower_quantity)
    )
    updated = result.fetchone()
    follow = AlbumFollows(album_id=album_id, user_id=user.id)

    db.add(follow)
    await db.commit()
    await db.refresh(follow)

    if not updated:
        raise HTTPException(404, "Album not found")

    return {"album_id": str(updated[0]), "listening_quantity": updated[1]}


@router.patch("/albums/{album_id}/unfollow")
async def album_unfollow(
        album_id: uuid.UUID,
        db: AsyncSession = Depends(get_db),
        user: CurrentUser = Depends(get_current_user)
):
    """Уменьшить счётчик лайков трека (внутренний эндпоинт для BFF)"""
    result = await db.execute(
        update(Albums)
        .where(Albums.id == album_id, Albums.follower_quantity > 0)
        .values(liked_quantity=Albums.follower_quantity - 1)
        .returning(Albums.id, Albums.follower_quantity)
    )
    updated = result.fetchone()
    await db.execute(
        delete(AlbumFollows)
        .where(
            AlbumFollows.album_id == album_id,
            AlbumFollows.user_id == user.id
        )
    )

    await db.commit()

    if not updated:
        raise HTTPException(404, "Track not found or liked_quantity is 0")

    return {"album_id": str(updated[0]), "liked_quantity": updated[1]}