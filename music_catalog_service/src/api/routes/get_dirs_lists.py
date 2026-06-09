# src/api/routes/get_music.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from src.db.postgres_engine import get_db
from src.models.albums_models import AlbumTypes
from src.models.tracks_models import Genres

# ... ваши импорты ...

router = APIRouter(prefix="/get_dirs_lists", tags=["Public Music"])


@router.get("/album_types")
async def get_album_types(
        db: AsyncSession = Depends(get_db)
):
    """Получение списка типов альбомов"""
    result = await db.execute(select(AlbumTypes))
    items = result.scalars().all()

    return {
        "items": [
            {"id": item.id, "title": item.title}
            for item in items
        ]
    }


@router.get("/genres")
async def get_genres(
        db: AsyncSession = Depends(get_db)
):
    """Получение списка жанров"""
    result = await db.execute(select(Genres))
    items = result.scalars().all()

    return {
        "items": [
            {"id": item.id, "title": item.title}
            for item in items
        ]
    }



